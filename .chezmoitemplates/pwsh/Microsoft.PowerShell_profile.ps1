if (Test-Path "~/.config/oh-my-posh/ensono.omp.json") {
    oh-my-posh init pwsh --config '~/.config/oh-my-posh/ensono.omp.json' | Invoke-Expression
} else {
    oh-my-posh init pwsh --config 'https://raw.githubusercontent.com/richards-ensono/dotfiles/master/dot_config/oh-my-posh/ensono.omp.json' | Invoke-Expression
}

if ((Get-Command hugo | Measure-Object).Count -gt 0) {
  hugo completion powershell | Out-String | Invoke-Expression
}

if ((Get-Command gpg-agent | Measure-Object).Count -gt 0) {
  if ((Get-Process -ProcessName gpg-agent -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0) {
    & gpg-connect-agent /bye
  }
}

if ((Get-Command podman -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0) {
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

