# audio-diag.ps1
# Read-only diagnostic report for sound / PnP problems on Windows 10 and 11.
# Collects facts only: no drivers are installed or removed, no registry values are changed.
# Run as administrator for sections 5 (driver store) and full details.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\audio-diag.ps1
#
# Result: audio-diag_<date>.txt on the Desktop.

$ErrorActionPreference = 'Continue'

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$stamp = Get-Date -Format 'yyyy-MM-dd_HH-mm'
$out = Join-Path ([Environment]::GetFolderPath('Desktop')) "audio-diag_$stamp.txt"

Start-Transcript -Path $out -Force | Out-Null

Write-Host "audio-diag: read-only report, nothing is changed"
Write-Host "Computer: $env:COMPUTERNAME"
Write-Host "User: $env:USERNAME"
Write-Host "Date: $(Get-Date)"
Write-Host "Administrator: $isAdmin"

Write-Host "`n=== 1. SYSTEM ==="
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture | Format-List

Write-Host "`n=== 2. DEVICES WITH PROBLEMS (present only) ==="
Get-PnpDevice | Where-Object { $_.Status -ne 'OK' -and $_.Present -eq $true } |
  Sort-Object Class |
  Format-Table -Auto Status, Class, Problem, FriendlyName, InstanceId

Write-Host "`n=== 3. AUDIO DEVICES (MEDIA class) ==="
Get-PnpDevice -Class MEDIA | Format-List Status, Present, Problem, FriendlyName, InstanceId

Write-Host "`n=== 4. AUDIO DEVICE PROPERTIES ==="
foreach ($dev in (Get-PnpDevice -Class MEDIA)) {
  Write-Host "--- $($dev.FriendlyName) [$($dev.Status)]"
  Write-Host "    $($dev.InstanceId)"
  foreach ($k in 'DEVPKEY_Device_HardwareIds',
                 'DEVPKEY_Device_DriverProvider',
                 'DEVPKEY_Device_DriverVersion',
                 'DEVPKEY_Device_DriverDate',
                 'DEVPKEY_Device_DriverInfPath',
                 'DEVPKEY_Device_Parent') {
    $p = Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName $k -ErrorAction SilentlyContinue
    if ($p) { Write-Host ("    {0}: {1}" -f $k, ($p.Data -join ' | ')) }
  }
}

Write-Host "`n=== 5. AUDIO DRIVER PACKAGES (driver store) ==="
if ($isAdmin) {
  try {
    Get-WindowsDriver -Online | Where-Object { $_.ClassName -eq 'MEDIA' } |
      Select-Object ProviderName, Version, Date, OriginalFileName, Driver |
      Sort-Object ProviderName |
      Format-Table -Auto
  } catch {
    Write-Host "Get-WindowsDriver failed: $($_.Exception.Message)"
  }
} else {
  Write-Host "skipped: run as administrator"
}

Write-Host "`n=== 6. HDAUDIO DEVICES (including non-present) ==="
Get-PnpDevice | Where-Object { $_.InstanceId -like 'HDAUDIO*' } |
  Format-Table -Auto Status, Class, FriendlyName, InstanceId

Write-Host "`n=== 7. AUDIO CLASS FILTER VALUES ==="
$ac = 'HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e96c-e325-11ce-bfc1-08002be10318}'
$classFilters = (Get-ItemProperty $ac -ErrorAction SilentlyContinue).PSObject.Properties |
  Where-Object { $_.Name -match 'Filters' }
if ($classFilters) {
  $classFilters | ForEach-Object { Write-Host ("    {0} = {1}" -f $_.Name, ($_.Value -join ', ')) }
} else {
  Write-Host "    (no UpperFilters / LowerFilters)"
}

Write-Host "`n=== 8. PER-DEVICE FILTER VALUES (HDAUDIO) ==="
$root = 'HKLM:\SYSTEM\CurrentControlSet\Enum\HDAUDIO'
$found = $false
$keys = Get-ChildItem $root -Recurse -ErrorAction SilentlyContinue |
  Where-Object { $_.PSChildName -eq 'Device Parameters' }
foreach ($k in $keys) {
  $p = Get-ItemProperty $k.PSPath -ErrorAction SilentlyContinue
  foreach ($prop in ($p.PSObject.Properties | Where-Object { $_.Name -match 'Filter' })) {
    $found = $true
    Write-Host ("    {0}" -f $k.PSPath)
    Write-Host ("        {0} = {1}" -f $prop.Name, ($prop.Value -join ', '))
  }
}
if (-not $found) { Write-Host "    (no filter values)" }

Write-Host "`n=== 9. RECENT PnP DRIVER FAILURES (Kernel-PnP, event 219) ==="
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-Kernel-PnP'; Id=219} -MaxEvents 15 -ErrorAction SilentlyContinue |
  Select-Object TimeCreated, Message | Format-List

Write-Host "`n=== 10. LAST UPDATES ==="
Get-HotFix | Sort-Object InstalledOn -Descending |
  Select-Object -First 6 HotFixID, InstalledOn, Description |
  Format-Table -Auto

Stop-Transcript | Out-Null
Write-Host ""
Write-Host "Report saved to: $out"
