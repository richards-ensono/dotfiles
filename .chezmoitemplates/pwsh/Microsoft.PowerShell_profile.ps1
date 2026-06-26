if (Test-Path "~/.config/oh-my-posh/cloud-native-tokyo-night.omp.json") {
    oh-my-posh init pwsh --config '~/.config/oh-my-posh/cloud-native-tokyo-night.omp.json' | Invoke-Expression
} else {
    oh-my-posh init pwsh --config 'https://raw.githubusercontent.com/richards-ensono/dotfiles/master/dot_config/oh-my-posh/cloud-native-tokyo-night.omp.json' | Invoke-Expression
}

if ((get-command hugo | Measure-Object).Count -gt 0) {
  hugo completion powershell | Out-String | Invoke-Expression
}

if ((get-command podman -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0) {
    Set-Alias -Name docker -Value podman
    podman completion powershell | Out-String | Invoke-Expression
}

Set-Alias -Name vi -Value nvim
Set-Alias -Name vim -Value nvim
Set-Alias -Name ls -Value Get-ChildItem
Set-Alias -Name ll -Value Get-ChildItem -Force

$env:VISUAL = "nvim"
$env:EDITOR = "nvim"

$openSshExecutable = "C:\Windows\System32\OpenSSH\ssh.exe";
if (Test-Path $openSshExecutable) {
    $env:GIT_SSH=$openSshExecutable;
}

Set-PSReadlineKeyHandler -Key ctrl+d -Function DeleteCharOrExit
Set-PSReadlineKeyHandler -Key ctrl+l -Function ClearScreen
