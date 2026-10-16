param(
    [switch]$Clean,
    [string]$ResultManifest = "results/pending.json",
    [switch]$RequireReviewed,
    [switch]$RequireComplete
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$perlPath = "C:\Strawberry\perl\bin"

Push-Location $repoRoot
try {
    if (Test-Path $perlPath) {
        $env:Path = "$perlPath;$env:Path"
    }

    $latexmkCommand = Get-Command latexmk -ErrorAction SilentlyContinue
    if (-not $latexmkCommand) {
        throw "latexmk is required but was not found on PATH"
    }

    if ($Clean) {
        & $latexmkCommand.Source -C main.tex supplementary.tex
        if ($LASTEXITCODE -ne 0) {
            throw "latexmk clean failed with exit code $LASTEXITCODE"
        }
        exit 0
    }

    $resultArguments = @(
        "scripts/import_results.py",
        "--manifest", $ResultManifest,
        "--bindings", "results/bindings.json",
        "--output", "results.tex"
    )
    if ($RequireReviewed) {
        $resultArguments += "--require-reviewed"
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python 3 is required but was not found on PATH"
    }
    if ($RequireComplete) {
        $resultArguments += "--require-complete"
    }
    & $pythonCommand.Source @resultArguments
    if ($LASTEXITCODE -ne 0) {
        throw "result import failed with exit code $LASTEXITCODE"
    }

    & $pythonCommand.Source scripts/render_figures.py
    if ($LASTEXITCODE -ne 0) {
        throw "figure rendering failed with exit code $LASTEXITCODE"
    }

    foreach ($document in @("main.tex", "supplementary.tex")) {
        & $latexmkCommand.Source -pdf -interaction=nonstopmode -halt-on-error -file-line-error $document
        if ($LASTEXITCODE -ne 0) {
            throw "LaTeX build failed for $document with exit code $LASTEXITCODE"
        }
    }
}
finally {
    Pop-Location
}

