param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "check", "build", "desktop")]
    [string]$Task = "dev",

    [Parameter(Position = 1)]
    [ValidateSet("python", "windows", "linux", "mac")]
    [string]$BuildTarget = "python"
)

$ErrorActionPreference = "Stop"
$repositoryRoot = $PSScriptRoot
$virtualEnvironmentPython = Join-Path $repositoryRoot ".venv\Scripts\python.exe"

function Invoke-Step {
    param([string[]]$Arguments)
    & $virtualEnvironmentPython @Arguments
    if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
}

Push-Location $repositoryRoot

if (-not (Test-Path $virtualEnvironmentPython)) {
    Write-Host "First run: creating .venv and installing the project with its development tools"
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
    Invoke-Step @("-m", "pip", "install", "--quiet", "--upgrade", "pip")
    Invoke-Step @("-m", "pip", "install", "--quiet", "--editable", ".[desktop-interface,web-interface]", "pytest", "ruff", "mypy")
}

switch ($Task) {
    "dev" {
        $env:FLET_LOG_LEVEL = "info"
        & $virtualEnvironmentPython -m pool_heat_exchanger_designer gui --web
    }
    "test" {
        & $virtualEnvironmentPython -m pytest -q
    }
    "check" {
        Invoke-Step @("-m", "pytest", "-q")
        Invoke-Step @("-m", "ruff", "check", ".")
        Invoke-Step @("-m", "ruff", "format", "--check", ".")
        & $virtualEnvironmentPython -m mypy
    }
    "build" {
        switch ($BuildTarget) {
            "python" {
                Invoke-Step @("-m", "pip", "install", "--quiet", "build")
                & $virtualEnvironmentPython -m build --outdir dist
            }
            "windows" {
                Invoke-Step @("-m", "pip", "install", "--quiet", "flet-cli")
                & (Join-Path $repositoryRoot ".venv\Scripts\flet.exe") build windows
            }
            default {
                Write-Host "flet can only build the $BuildTarget app on a $BuildTarget machine; this one is Windows."
                Pop-Location
                exit 2
            }
        }
    }
    "desktop" {
        $executable = Join-Path $repositoryRoot "build\windows\pool-heat-exchanger-designer.exe"
        if (-not (Test-Path $executable)) {
            Write-Host "No Windows build found. Build it first with: run build windows"
            Pop-Location
            exit 2
        }
        $startedAt = Get-Date
        $application = Start-Process -FilePath $executable -PassThru
        Write-Host "Desktop app started (process $($application.Id)). Close its window to stop."
        $logFile = $null
        foreach ($attempt in 1..30) {
            Start-Sleep -Milliseconds 500
            $logFile = Get-ChildItem "$env:LOCALAPPDATA\*\pool-heat-exchanger-designer\console.log" -ErrorAction SilentlyContinue |
                Where-Object { $_.LastWriteTime -ge $startedAt } |
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($logFile) { break }
        }
        if ($null -eq $logFile) {
            Write-Host "console.log did not appear; errors will only show inside the app window."
            $application.WaitForExit()
        }
        else {
            Write-Host "Streaming the app's Python log: $($logFile.FullName)"
            $linesShown = 0
            while (-not $application.HasExited) {
                $lines = @(Get-Content $logFile.FullName -ErrorAction SilentlyContinue)
                if ($lines.Count -gt $linesShown) {
                    $lines[$linesShown..($lines.Count - 1)] | ForEach-Object { Write-Host $_ }
                    $linesShown = $lines.Count
                }
                Start-Sleep -Milliseconds 700
            }
            $lines = @(Get-Content $logFile.FullName -ErrorAction SilentlyContinue)
            if ($lines.Count -gt $linesShown) {
                $lines[$linesShown..($lines.Count - 1)] | ForEach-Object { Write-Host $_ }
            }
            Write-Host "Desktop app exited."
        }
    }
}

$taskExitCode = $LASTEXITCODE
Pop-Location
exit $taskExitCode
