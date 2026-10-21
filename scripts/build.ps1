<#
.SYNOPSIS
Compile the paper PDFs from the committed sources and optionally check them.

.DESCRIPTION
The standalone paper and supplement read each other's .aux files (xr-hyper), so
they are built supplement -> main -> supplement -> main; latexmk skips passes that
are already current. The full edition uses pdfLaTeX and the Chinese edition
XeLaTeX. Tables are refreshed separately by the export scripts (see README);
-Figures reruns every figure producer before compiling.

.EXAMPLE
./scripts/build.ps1 -Check
./scripts/build.ps1 -Target main
#>
param(
    [ValidateSet("all", "main", "supplementary", "full", "zh")]
    [string[]]$Target = @("all"),
    [switch]$Figures,
    [switch]$Check,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$perlPath = "C:\Strawberry\perl\bin"

function Invoke-Checked([string]$Description, [scriptblock]$Command) {
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE"
    }
}

Push-Location $repoRoot
try {
    if (Test-Path $perlPath) {
        $env:Path = "$perlPath;$env:Path"
    }
    $latexmk = (Get-Command latexmk -ErrorAction SilentlyContinue).Source
    if (-not $latexmk) {
        throw "latexmk is required but was not found on PATH"
    }
    $python = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        $python = (Get-Command python -ErrorAction SilentlyContinue).Source
    }

    if ($Clean) {
        # Keep the tracked reading PDFs; remove only rebuildable auxiliary files.
        Invoke-Checked "latexmk clean" { & $latexmk -c main.tex supplementary.tex paper_full.tex manuscript_zh.tex }
        foreach ($document in @("main", "supplementary", "paper_full", "manuscript_zh")) {
            foreach ($suffix in @(".bbl", ".brf", ".synctex", ".synctex.gz")) {
                $auxiliaryPath = Join-Path $repoRoot ($document + $suffix)
                if (Test-Path -LiteralPath $auxiliaryPath) {
                    Remove-Item -LiteralPath $auxiliaryPath
                }
            }
        }
        return
    }
    if (($Figures -or $Check) -and -not $python) {
        throw "Python 3 is required for -Figures and -Check but was not found"
    }
    if ($Figures) {
        Invoke-Checked "figure build" { & $python scripts/build_figures.py }
    }

    $wanted = if ($Target -contains "all") { @("main", "supplementary", "full", "zh") } else { $Target }
    $sequence = @()
    if (($wanted -contains "main") -and ($wanted -contains "supplementary")) {
        $sequence += @("supplementary.tex", "main.tex", "supplementary.tex", "main.tex")
    } elseif ($wanted -contains "main") {
        $sequence += "main.tex"
    } elseif ($wanted -contains "supplementary") {
        $sequence += "supplementary.tex"
    }
    if ($wanted -contains "full") {
        $sequence += "paper_full.tex"
    }
    $options = @("-interaction=nonstopmode", "-halt-on-error", "-file-line-error")
    foreach ($document in $sequence) {
        Invoke-Checked "LaTeX build of $document" { & $latexmk -pdf @options $document }
    }
    if ($wanted -contains "zh") {
        Invoke-Checked "Chinese build" { & $latexmk -xelatex @options manuscript_zh.tex }
    }

    if ($Check) {
        Invoke-Checked "unit tests" { & $python -m unittest discover -s tests }
        Invoke-Checked "manuscript checks" { & $python scripts/check_build.py }
    }
}
finally {
    Pop-Location
}
