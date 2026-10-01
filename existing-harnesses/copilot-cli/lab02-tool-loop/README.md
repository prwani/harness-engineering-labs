# Lab 2A — Built-in tool loop

Use **this lab's** `provider.env.example` and the [preflight](../) in
a disposable workspace. Create `service.txt` with `printf 'demo-order:
Go; port 3000; queue orders-demo\n' > "$workdir/service.txt"`.

Run `copilot -C "$workdir" -i "Read service.txt and report name, language,
port and queue with a file citation. Do not modify files."`. Approve
only the required read. Compare to a new empty directory with the same
request. Inspect which tool actually read the file and compare the
citation with `service.txt`. Do not deliberately enable unrestricted
shell execution as in build-your-own Lab 2A; the native loop already
pairs calls and results, and its internal transcript is not ours.
Record the observed tool and any unavailable internal details.
