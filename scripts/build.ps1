param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$perlPath = "C:\Strawberry\perl\bin"

Push-Location $repoRoot
try {
    if (Test-Path $perlPath) {
        $env:Path = "$perlPath;$env:Path"
    }

    if ($Clean) {
        latexmk -C
        if ($LASTEXITCODE -ne 0) {
            throw "latexmk clean failed with exit code $LASTEXITCODE"
        }
        exit 0
    }

    python scripts/render_figures.py
    if ($LASTEXITCODE -ne 0) {
        throw "figure rendering failed with exit code $LASTEXITCODE"
    }

    latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex
    if ($LASTEXITCODE -ne 0) {
        throw "LaTeX build failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

