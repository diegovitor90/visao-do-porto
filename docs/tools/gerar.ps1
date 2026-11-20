[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$PlantUmlJar,
    [Parameter(Mandatory=$true)][string]$AsciidoctorModule,
    [Parameter(Mandatory=$true)][string]$ChromePath,
    [string]$PlaywrightModule = $env:PLAYWRIGHT_MODULE,
    [string]$PythonExe = '',
    [string]$NodeExe = 'node',
    [string]$JavaExe = 'java'
)
# Compatível com Windows PowerShell 5.1 e PowerShell 7.
$ErrorActionPreference = 'Stop'
# Saída Unicode dos processos Python no terminal Windows.
$env:PYTHONIOENCODING = 'utf-8'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (-not $PythonExe) { $PythonExe = Join-Path $repoRoot 'backend/fastapi/.venv/Scripts/python.exe' }
foreach ($target in @($PlantUmlJar,$AsciidoctorModule,$ChromePath,$PythonExe)) {
    if (-not (Test-Path -LiteralPath $target)) { throw "Ferramenta ausente: $target. Consulte docs/operacao/documentacao.md" }
}
$jar = (Resolve-Path -LiteralPath $PlantUmlJar).Path
$module = (Resolve-Path -LiteralPath $AsciidoctorModule).Path
$chrome = (Resolve-Path -LiteralPath $ChromePath).Path
$fontes = Join-Path $repoRoot 'docs/arquitetura/diagramas/fontes'
$imagens = Join-Path $repoRoot 'docs/arquitetura/diagramas/imagens'
$gerado = Join-Path $repoRoot 'docs/arquitetura/gerado'
New-Item -ItemType Directory -Force $imagens,$gerado | Out-Null
Push-Location $repoRoot
try {
    & $PythonExe -B (Join-Path $PSScriptRoot 'verificar_docs.py') --fontes
    if ($LASTEXITCODE -ne 0) { throw 'Verificação inicial falhou' }
    & $PythonExe -B (Join-Path $PSScriptRoot 'extrair_contratos.py')
    if ($LASTEXITCODE -ne 0) { throw 'Extração falhou' }
    $diagrams = @(Get-ChildItem -LiteralPath $fontes -Filter '*.puml' | Sort-Object Name)
    foreach ($format in @('svg','png')) {
        foreach ($diagram in $diagrams) {
            & $JavaExe '-Djava.awt.headless=true' -jar $jar -Playout=smetana "-t$format" -charset UTF-8 -failfast2 -o $imagens $diagram.FullName
            if ($LASTEXITCODE -ne 0) { throw "PlantUML falhou: $($diagram.Name)" }
        }
    }
    $master = Join-Path $repoRoot 'docs/arquitetura/arquitetura.adoc'
    $html = Join-Path $gerado 'arquitetura.html'
    $pdf = Join-Path $gerado 'arquitetura.pdf'
    & $NodeExe (Join-Path $PSScriptRoot 'render_html.cjs') $master $html $module
    if ($LASTEXITCODE -ne 0) { throw 'HTML falhou' }
    & $NodeExe (Join-Path $PSScriptRoot 'render_pdf.cjs') $html $pdf $chrome $PlaywrightModule
    if ($LASTEXITCODE -ne 0) { throw 'PDF falhou' }
    & $PythonExe -B (Join-Path $PSScriptRoot 'verificar_docs.py')
    if ($LASTEXITCODE -ne 0) { throw 'Verificação final falhou' }
    $manifest = [ordered]@{
        plantuml_jar_sha256 = (Get-FileHash -LiteralPath $jar -Algorithm SHA256).Hash.ToLower()
        plantuml_version = (& $JavaExe -jar $jar -version | Select-Object -First 1)
        asciidoctor_version = (& $NodeExe -p "require(process.argv[1]).version" (Join-Path $module 'package.json'))
        node_version = (& $NodeExe --version)
        python_version = (& $PythonExe --version)
        chrome_version = (Get-Item -LiteralPath $chrome).VersionInfo.ProductVersion
        sources_sha256 = [ordered]@{}
        artifacts_sha256 = [ordered]@{}
    }
    $docFiles = Get-ChildItem (Join-Path $repoRoot 'docs') -Recurse -File | Where-Object {
        $_.Extension -in @('.md','.adoc','.puml','.css','.py','.cjs','.ps1')
    }
    foreach ($file in $docFiles) {
        $name = $file.FullName.Substring($repoRoot.Length).TrimStart([char[]]'\/').Replace('\','/')
        $manifest.sources_sha256[$name] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLower()
    }
    foreach ($file in @(Get-Item $html,$pdf) + @(Get-ChildItem $imagens -File)) {
        $name = $file.FullName.Substring($repoRoot.Length).TrimStart([char[]]'\/').Replace('\','/')
        $manifest.artifacts_sha256[$name] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLower()
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $gerado 'manifesto-build.json') -Encoding utf8
    Write-Host "Documentação gerada em docs/arquitetura/gerado. Nenhum teste funcional foi executado."
} finally { Pop-Location }
