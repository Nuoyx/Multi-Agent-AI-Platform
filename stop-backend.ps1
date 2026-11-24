[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
$services = @{
    'Gateway' = 'ALiceAI\backend\gateway'
    'Auth' = 'ALiceAI\backend\services\auth'
}

$processes = @(Get-CimInstance Win32_Process)
$matched = 0
foreach ($service in $services.GetEnumerator()) {
    $pythonPath = Join-Path $PSScriptRoot "$($service.Value)\.venv\Scripts\python.exe"
    $pythonCommand = '^"?' + [regex]::Escape($pythonPath) + '"?\s'
    $candidates = @($processes | Where-Object {
        $_.Name -eq 'python.exe' -and
        ($_.ExecutablePath -eq $pythonPath -or $_.CommandLine -match $pythonCommand) -and
        $_.CommandLine -match '\buvicorn\s+app\.main:app(?:\s|$)'
    })

    # Stop the launcher tree, including Uvicorn's reload supervisor and workers.
    $candidateIds = @($candidates | ForEach-Object { $_.ProcessId })
    foreach ($candidate in $candidates) {
        if ($candidate.ParentProcessId -in $candidateIds) { continue }
        $matched++
        if ($PSCmdlet.ShouldProcess("$($service.Key) (PID $($candidate.ProcessId))", 'Stop backend process tree')) {
            # Recheck identity before terminating a process from the snapshot.
            $current = Get-CimInstance Win32_Process -Filter "ProcessId = $($candidate.ProcessId)"
            if (!$current -or $current.CreationDate -ne $candidate.CreationDate) { continue }
            & taskkill.exe /PID $candidate.ProcessId /T /F
            if ($LASTEXITCODE -ne 0) { throw "Unable to stop $($service.Key)." }
            Write-Output "Stopped $($service.Key)."
        }
    }
}

if ($matched -eq 0) {
    Write-Output 'No running Gateway or Auth Uvicorn service found for this project.'
}
