# Creates or updates the AgriShift AI Desktop Shortcut
$ErrorActionPreference = "SilentlyContinue"

$desktop = [Environment]::GetFolderPath("Desktop")
$projectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $projectDir) {
    $projectDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
}

$shortcutPath = Join-Path $desktop "AgriShift AI.lnk"
$targetScript = Join-Path $projectDir "start_agrishift.bat"
$iconPath = Join-Path $projectDir "agrishift.ico"

if (-not (Test-Path $targetScript)) {
    Write-Warning "Target launcher script not found at $targetScript"
    exit 1
}

try {
    $wsh = New-Object -ComObject WScript.Shell
    $shortcut = $wsh.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $targetScript
    $shortcut.WorkingDirectory = $projectDir
    if (Test-Path $iconPath) {
        $shortcut.IconLocation = "$iconPath,0"
    }
    $shortcut.Description = "AgriShift AI - Real Earth Observation & Agronomic Crop Rotation Platform"
    $shortcut.Save()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wsh) | Out-Null
    Write-Host "Desktop shortcut created/updated successfully at: $shortcutPath"
} catch {
    Write-Error "Failed to create desktop shortcut: $_"
    exit 1
}
