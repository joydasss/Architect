<#
.SYNOPSIS
    Builds a combined PDF/EPUB of the Architect Handbook from BOOK_PLAN.md order.
.DESCRIPTION
    Concatenates chapter Markdown files in the order they appear in BOOK_PLAN.md's
    part table, then runs Pandoc to produce build/handbook.pdf and build/handbook.epub.
    Requires Pandoc (https://pandoc.org/) and a LaTeX engine (e.g. MiKTeX/TinyTeX) for PDF output.
.PARAMETER Format
    One or more of: pdf, epub, both (default: both)
#>
param(
    [ValidateSet('pdf', 'epub', 'both')]
    [string]$Format = 'both'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$buildDir = Join-Path $root 'build'
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    Write-Error "Pandoc not found on PATH. Install it from https://pandoc.org/ and re-run."
    exit 1
}

$pdfEngine = Get-Command pdflatex, xelatex, lualatex, wkhtmltopdf -ErrorAction SilentlyContinue | Select-Object -First 1
if ($Format -in @('pdf', 'both') -and -not $pdfEngine) {
    Write-Error "No PDF engine found (pdflatex/xelatex/lualatex/wkhtmltopdf). Install a LaTeX distribution (e.g. MiKTeX or TinyTeX: https://miktex.org/ or https://yihui.org/tinytex/) and re-run, or use -Format epub."
    exit 1
}

# Ordered list of part folders, matching BOOK_PLAN.md's reading-order table.
$partFolders = @(
    '01_Architecture_Mindset', '02_Design_Thinking_and_Product_Management',
    '03_Software_Engineering_Foundations', '04_Frontend_Architecture',
    '05_Networking_and_OS', '06_Databases_and_Storage',
    '07_System_Design_and_Distributed_Systems', '08_API_Architecture',
    '09_Cloud_Computing', '10_Kubernetes', '11_DevOps', '12_Observability',
    '13_Security', '14_AI_and_GenAI', '15_Enterprise_Architecture',
    '16_Performance_Engineering', '17_Architecture_Patterns',
    '18_Architecture_Documentation', '19_Soft_Skills',
    '20_Real_World_Case_Studies', '21_Additional_Architect_Competencies',
    '22_Appendices_and_Glossary'
)

$chapterFiles = New-Object System.Collections.Generic.List[string]
foreach ($part in $partFolders) {
    $partPath = Join-Path $root $part
    if (-not (Test-Path $partPath)) { continue }
    $overview = Join-Path $partPath 'PART_OVERVIEW.md'
    if (Test-Path $overview) { $chapterFiles.Add($overview) }
    Get-ChildItem -Path $partPath -Filter 'CH*.md' -File |
        Sort-Object Name |
        ForEach-Object { $chapterFiles.Add($_.FullName) }
}

if ($chapterFiles.Count -eq 0) {
    Write-Warning "No chapter files found yet - build will only contain part overviews (if any)."
}

Write-Host "Concatenating $($chapterFiles.Count) file(s) in reading order..."

if ($Format -in @('pdf', 'both')) {
    $pdfEngineArg = if ($pdfEngine.Name -eq 'wkhtmltopdf') { @('--pdf-engine=wkhtmltopdf') } else { @() }
    $headerInclude = Join-Path $PSScriptRoot 'pdf-header.tex'
    $headerArg = if ($pdfEngine.Name -ne 'wkhtmltopdf' -and (Test-Path $headerInclude)) { @('--include-in-header', $headerInclude) } else { @() }
    pandoc @chapterFiles -o (Join-Path $buildDir 'handbook.pdf') --toc --toc-depth=2 @pdfEngineArg @headerArg
    Write-Host "Wrote $(Join-Path $buildDir 'handbook.pdf')"
}
if ($Format -in @('epub', 'both')) {
    pandoc @chapterFiles -o (Join-Path $buildDir 'handbook.epub') --toc --toc-depth=2
    Write-Host "Wrote $(Join-Path $buildDir 'handbook.epub')"
}
