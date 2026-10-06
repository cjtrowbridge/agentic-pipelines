[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$PipelineArgs)

$ErrorActionPreference = 'Stop'

try {
    Write-Host 'bootstrap: locating REPLACE_PYTHON_COMMAND'
    if (-not (Get-Command REPLACE_PYTHON_COMMAND -ErrorAction SilentlyContinue)) {
        throw 'REPLACE_PYTHON_COMMAND is unavailable. Follow the host setup instructions.'
    }

    & REPLACE_PYTHON_COMMAND -B "$PSScriptRoot/../scripts/bootstrap.py"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host 'bootstrap: prerequisites ready; starting host pipeline'
    & REPLACE_PIPELINE_COMMAND @PipelineArgs
    exit $LASTEXITCODE
}
catch [System.Management.Automation.PipelineStoppedException] {
    Write-Error 'bootstrap: interrupted'
    exit 130
}
catch {
    Write-Error "bootstrap: $($_.Exception.Message)"
    exit 1
}
