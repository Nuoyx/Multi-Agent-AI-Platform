[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
$services = @{
    'com.nuoy.gateway.GatewayApplication' = 'ALiceAI\backend\gateway'
    'com.nuoy.auth.AuthApplication'       = 'ALiceAI\backend\services\auth'
}

$javaProcesses = & jcmd -l
if ($LASTEXITCODE -ne 0) { throw 'Unable to list Java processes with jcmd.' }

$matched = 0
foreach ($entry in $javaProcesses) {
    if ($entry -notmatch '^\s*(\d+)\s+(\S+)') { continue }
    $processId = [int]$Matches[1]
    $mainClass = $Matches[2]
    if (!$services.ContainsKey($mainClass)) { continue }

    # Maven starts each application in its module directory.
    $moduleDirectory = Join-Path $PSScriptRoot $services[$mainClass]
    $properties = & jcmd $processId VM.system_properties
    if ($LASTEXITCODE -ne 0) { throw "Unable to verify the directory for PID $processId." }
    $directoryLine = $properties | Where-Object { $_ -like 'user.dir=*' } | Select-Object -First 1
    if (!$directoryLine) { throw "Missing working directory for PID $processId." }
    $directory = $directoryLine.Substring('user.dir='.Length).Replace('\\', '\').Replace('\:', ':')
    if ([IO.Path]::GetFullPath($directory) -ne $moduleDirectory) { continue }

    $matched++
    if ($PSCmdlet.ShouldProcess("$mainClass (PID $processId)", 'Stop service')) {
        $process = Get-Process -Id $processId
        $process | Stop-Process -PassThru | Wait-Process -Timeout 15
        Write-Output "Stopped $mainClass (PID $processId)."
    }
}

if ($matched -eq 0) { Write-Output 'No running Gateway or Auth service found for this project.' }
