"""Create an optional per-user shortcut after a successful installation."""
from pathlib import Path
import base64
import subprocess


def create_shortcut(installation, desktop=None):
    installation = Path(installation).resolve(strict=True)
    executable = installation / 'app/SteveInTheZone.exe'
    if not executable.is_file():
        raise FileNotFoundError(executable)
    icon = installation / 'app/_internal/assets/zone-mark.ico'
    def quoted(value):
        return "'" + str(value).replace("'", "''") + "'"
    desktop_expression = quoted(Path(desktop).resolve(strict=True)) if desktop else "[Environment]::GetFolderPath('Desktop')"
    script = f"""
$ErrorActionPreference = 'Stop'
$desktop = {desktop_expression}
$shell = New-Object -ComObject WScript.Shell
$target = {quoted(executable)}
$name = 'Steve in the Zone'
$index = 1
while ($true) {{
    $path = Join-Path $desktop ($name + '.lnk')
    if (-not (Test-Path -LiteralPath $path)) {{ break }}
    $existing = $shell.CreateShortcut($path)
    if ($existing.TargetPath -eq $target) {{ break }}
    $index += 1
    $name = 'Steve in the Zone (' + $index + ')'
}}
$shortcut = $shell.CreateShortcut($path)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = {quoted(executable.parent)}
$shortcut.IconLocation = {quoted(str(icon) + ',0')}
$shortcut.Description = 'Steve in the Zone'
$shortcut.Save()
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Write-Output $path
"""
    encoded = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
    result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded],
                            capture_output=True, encoding='utf-8', errors='replace', timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW, check=True)
    return Path(result.stdout.strip())
