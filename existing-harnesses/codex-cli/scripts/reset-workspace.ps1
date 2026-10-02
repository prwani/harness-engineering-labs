[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)]
    [ValidateSet('lab00-setup', 'lab01-baseline', 'lab02-tool-loop', 'lab02b-hooks',
        'lab03-sessions', 'lab04-planning', 'lab05-file-memory', 'lab06-approval',
        'lab07-observability', 'lab08-skills-tools', 'lab09-background-agents',
        'lab10-compaction', 'lab11-loops', 'lab12-graphs', 'lab13-capstone',
        'lab14-comparison')]
    [string]$Lab,
    [switch]$Second
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$labPath = Join-Path $root $Lab
$name = if ($Second) { 'workspace-b' } else { 'workspace' }
$workspace = Join-Path $labPath $name
if (-not (Test-Path -LiteralPath (Join-Path $labPath 'README.md'))) {
    throw "Missing lab: $labPath"
}
foreach ($path in @($root, $labPath, $workspace)) {
    if ((Test-Path -LiteralPath $path) -and
        ((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Refusing to reset through a link: $path"
    }
}
if ($PSCmdlet.ShouldProcess($workspace, 'Delete workspace contents except .gitkeep')) {
    New-Item -ItemType Directory -Path $workspace -Force | Out-Null
    foreach ($item in Get-ChildItem -LiteralPath $workspace -Force) {
        if ($item.Name -eq '.gitkeep') { continue }
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Remove workspace link manually before resetting: $($item.FullName)"
        }
        $links = if ($item.PSIsContainer) {
            @(Get-ChildItem -LiteralPath $item.FullName -Recurse -Force |
                Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
        } else { @() }
        if ($links.Count) { throw "Remove nested workspace links manually before resetting." }
        Remove-Item -LiteralPath $item.FullName -Recurse -Force
    }
    if (-not (Test-Path -LiteralPath (Join-Path $workspace '.gitkeep'))) {
        New-Item -ItemType File -Path (Join-Path $workspace '.gitkeep') | Out-Null
    }
    Write-Output "Reset: $workspace. Codex history in CODEX_HOME was not deleted."
}
