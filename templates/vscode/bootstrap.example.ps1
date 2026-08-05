[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$PipelineArgs)

$ErrorActionPreference = 'Stop'

try {
    Write-Host 'bootstrap: checking REPLACE_PREREQUISITE_COMMAND'
    if (-not (Get-Command REPLACE_PREREQUISITE_COMMAND -ErrorAction SilentlyContinue)) {
        throw 'REPLACE_PREREQUISITE_COMMAND is unavailable. Follow the host setup instructions.'
    }

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
