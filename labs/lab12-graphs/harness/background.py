"""Background agents: a whole `harness ask` run, detached, in its own worktree.

``harness ask --bg -n NAME "task"`` creates a Git worktree for the project
at ``.harness/worktrees/NAME`` on a new branch ``worktree-NAME`` (from the
last commit, so commit first), then starts a detached ``harness ask`` there
and returns at once. Its output goes to a log file and its steps to a trace.

There is no one to answer permission prompts in the background, so it runs
with ``--accept-edits``: edits are allowed inside its own worktree, and
anything else that would ask is denied. The worktree is what makes this
safe alongside your own edits.

``harness agents`` lists background agents, ``harness logs NAME`` shows a
log, and ``harness rm NAME`` removes the agent, its worktree and branch. It
refuses while the agent runs or when the worktree has uncommitted changes.
State is kept in ``$HARNESS_HOME/projects/<project>/background/``.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from harness.session import project_dir

_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")


@dataclass
class BackgroundAgent:
    name: str
    task: str
    repo: str
    worktree: str
    branch: str
    log: str
    trace: str
    started: str
    pid: int = 0

    @property
    def exit_file(self) -> Path:
        return Path(self.log).with_suffix(".exit")

    @property
    def exit_code(self) -> int | None:
        return int(self.exit_file.read_text()) if self.exit_file.is_file() else None

    @property
    def status(self) -> str:
        if self.exit_code is not None:
            return "done" if self.exit_code == 0 else f"failed (exit {self.exit_code})"
        return "running" if _alive(self.pid) else "stopped (no exit code)"


def _alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                                capture_output=True, text=True, check=False)
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def state_dir(repo: Path) -> Path:
    return project_dir(repo) / "background"


def _meta_path(repo: Path, name: str) -> Path:
    return state_dir(repo) / f"{name}.json"


def load(repo: Path, name: str) -> BackgroundAgent:
    path = _meta_path(repo, name)
    if not path.is_file():
        raise ValueError(f"no background agent named {name}")
    return BackgroundAgent(**json.loads(path.read_text(encoding="utf-8")))


def save(agent: BackgroundAgent) -> None:
    path = _meta_path(Path(agent.repo), agent.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(agent), indent=2), encoding="utf-8")


def list_agents(repo: Path) -> list[BackgroundAgent]:
    return [BackgroundAgent(**json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(state_dir(repo).glob("*.json"))]


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def ask_command(worktree: Path, name: str, task: str, trace: Path) -> list[str]:
    """The detached run: `harness ask` in the worktree, edits accepted, traced."""
    return [sys.executable, "-c", "from harness.cli.app import app; app()",
            "ask", "--repo", str(worktree), "--accept-edits", "-n", name, "--trace", str(trace), "--", task]


def start(repo: Path, name: str, task: str, command: list[str] | None = None) -> BackgroundAgent:
    repo = repo.resolve()
    if not _NAME.match(name):
        raise ValueError("background agent name must be lowercase letters, digits and hyphens")
    if _meta_path(repo, name).exists():
        raise ValueError(f"background agent {name} exists; remove it with: harness rm {name}")
    root = Path(_git(repo, "rev-parse", "--show-toplevel").strip())
    worktree, branch = root / ".harness" / "worktrees" / name, f"worktree-{name}"
    _git(root, "worktree", "add", "-b", branch, str(worktree), "HEAD")
    folder = state_dir(repo)
    folder.mkdir(parents=True, exist_ok=True)
    agent = BackgroundAgent(
        name=name, task=task, repo=str(repo), worktree=str(worktree), branch=branch,
        log=str(folder / f"{name}.log"), trace=str(folder / f"{name}.trace.jsonl"),
        started=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    save(agent)
    runner = [sys.executable, "-m", "harness.background", str(_meta_path(repo, name)), "--",
              *(command or ask_command(worktree, name, task, Path(agent.trace)))]
    env = dict(os.environ)
    package_root = str(Path(__file__).resolve().parents[1])
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [package_root, env.get("PYTHONPATH")]))
    detach = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS}
              if os.name == "nt" else {"start_new_session": True})
    process = subprocess.Popen(runner, cwd=worktree, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **detach)
    agent.pid = process.pid
    save(agent)
    return agent


def remove(repo: Path, name: str, *, force: bool = False) -> None:
    agent = load(repo.resolve(), name)
    if agent.status == "running":
        raise RuntimeError(f"{name} is still running; wait for it, or stop process {agent.pid}")
    worktree = Path(agent.worktree)
    if worktree.exists():
        if not force and _git(worktree, "status", "--porcelain").strip():
            raise RuntimeError(f"{worktree} has uncommitted changes; copy what you need, "
                               "clean it, or use --force")
        _git(Path(agent.repo), "worktree", "remove", *(["--force"] if force else []), str(worktree))
    _git(Path(agent.repo), "branch", "-D", agent.branch)
    for path in (Path(agent.log), Path(agent.trace), agent.exit_file, _meta_path(Path(agent.repo), name)):
        path.unlink(missing_ok=True)


def describe(repo: Path) -> str:
    agents = list_agents(repo.resolve())
    if not agents:
        return "No background agents."
    return "\n".join(f"{agent.name:<16} {agent.status:<22} {agent.branch}  {agent.task[:60]}"
                     for agent in agents)


def _run(meta: Path, command: list[str]) -> int:
    """Child process: run the command, log its output, record the exit code."""
    agent = BackgroundAgent(**json.loads(meta.read_text(encoding="utf-8")))
    with open(agent.log, "a", encoding="utf-8") as log:
        log.write(f"$ harness ask (background {agent.name}) in {agent.worktree}\n")
        log.flush()
        code = subprocess.run(command, cwd=agent.worktree, stdin=subprocess.DEVNULL,
                              stdout=log, stderr=subprocess.STDOUT, check=False).returncode
        log.write(f"\n[exit {code}]\n")
    agent.exit_file.write_text(str(code))
    return code


if __name__ == "__main__":
    separator = sys.argv.index("--")
    sys.exit(_run(Path(sys.argv[1]), sys.argv[separator + 1:]))
