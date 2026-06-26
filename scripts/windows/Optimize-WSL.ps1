[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [ValidateSet('Full', 'Quick')]
    [string]$Mode = 'Full'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)

    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Assert-OptimizeVhdAvailable {
    if (Get-Command -Name Optimize-VHD -ErrorAction SilentlyContinue) {
        return
    }

    try {
        Import-Module -Name Hyper-V -ErrorAction Stop
    }
    catch {
        throw 'Optimize-VHD is not available. Install the Hyper-V PowerShell feature and run the script again.'
    }

    if (-not (Get-Command -Name Optimize-VHD -ErrorAction SilentlyContinue)) {
        throw 'Optimize-VHD is not available after importing the Hyper-V module.'
    }
}

function Get-RunningWslDistributions {
    $wslCommand = Get-Command -Name wsl.exe -ErrorAction SilentlyContinue
    if (-not $wslCommand) {
        throw 'wsl.exe is not available on PATH.'
    }

    $output = & $wslCommand.Source --list --running --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "wsl.exe --list --running failed with exit code $LASTEXITCODE."
    }

    return @(
        $output |
        Where-Object { $_ -and $_.Trim() } |
        ForEach-Object { $_.Trim() }
    )
}

function Resolve-VhdPaths {
    param(
        [string]$BasePath,
        [string]$VhdFileName
    )

    $candidatePaths = [System.Collections.Generic.List[string]]::new()

    if ($VhdFileName) {
        if ([System.IO.Path]::IsPathRooted($VhdFileName)) {
            $candidatePaths.Add($VhdFileName)
        }
        elseif ($BasePath) {
            $candidatePaths.Add((Join-Path -Path $BasePath -ChildPath $VhdFileName))
        }
    }

    if ($BasePath) {
        if ($BasePath.EndsWith('.vhdx', [System.StringComparison]::OrdinalIgnoreCase)) {
            $candidatePaths.Add($BasePath)
        }
        else {
            $candidatePaths.Add((Join-Path -Path $BasePath -ChildPath 'ext4.vhdx'))
            $candidatePaths.Add((Join-Path -Path $BasePath -ChildPath 'LocalState\ext4.vhdx'))

            foreach ($searchPath in @($BasePath, (Join-Path -Path $BasePath -ChildPath 'LocalState'))) {
                if (-not (Test-Path -LiteralPath $searchPath -PathType Container)) {
                    continue
                }

                foreach ($vhd in Get-ChildItem -LiteralPath $searchPath -Filter '*.vhdx' -File -ErrorAction SilentlyContinue) {
                    $candidatePaths.Add($vhd.FullName)
                }
            }
        }
    }

    return @(
        $candidatePaths |
        Select-Object -Unique |
        Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        ForEach-Object { (Resolve-Path -LiteralPath $_).Path }
    )
}

function Get-WslDistributionInfo {
    $registryRoot = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss'
    if (-not (Test-Path -LiteralPath $registryRoot)) {
        throw "WSL registry root '$registryRoot' was not found."
    }

    return @(
        Get-ChildItem -LiteralPath $registryRoot |
        ForEach-Object {
            $item = Get-ItemProperty -LiteralPath $_.PSPath
            if (-not $item.DistributionName) {
                return
            }

            [PSCustomObject]@{
                DistributionName = $item.DistributionName
                Identifier       = $_.PSChildName
                BasePath         = $item.BasePath
                VhdFileName      = $item.VhdFileName
                VhdPaths         = @(Resolve-VhdPaths -BasePath $item.BasePath -VhdFileName $item.VhdFileName)
            }
        }
    )
}

function Format-ByteSize {
    param(
        [long]$SizeBytes
    )

    $units = @('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    $size = [double]$SizeBytes
    $unitIndex = 0

    while ($size -ge 1024 -and $unitIndex -lt ($units.Count - 1)) {
        $size /= 1024
        $unitIndex++
    }

    return '{0:N2} {1}' -f $size, $units[$unitIndex]
}

$distributions = @(Get-WslDistributionInfo)
if (-not $distributions) {
    Write-Verbose 'No WSL distributions were found in the current user registry hive.'
    return
}

$discoveredVhds = @(
    $distributions |
    ForEach-Object { $_.VhdPaths } |
    Where-Object { $_ } |
    Select-Object -Unique
)

if (-not $discoveredVhds) {
    throw 'No VHDX files were resolved from the registered WSL distributions.'
}

if (-not $WhatIfPreference) {
    if (-not (Test-IsAdministrator)) {
        throw 'Run this script from an elevated PowerShell session. Optimize-VHD requires administrator rights.'
    }

    Assert-OptimizeVhdAvailable
}

$runningDistributions = @(Get-RunningWslDistributions)
if ($runningDistributions.Count -gt 0 -and $PSCmdlet.ShouldProcess(($runningDistributions -join ', '), 'Shut down running WSL distributions')) {
    & wsl.exe --shutdown
    if ($LASTEXITCODE -ne 0) {
        throw "wsl.exe --shutdown failed with exit code $LASTEXITCODE."
    }
}

$results = foreach ($distribution in $distributions) {
    if (-not $distribution.VhdPaths) {
        Write-Warning "No VHDX files were found for WSL distribution '$($distribution.DistributionName)'."
        continue
    }

    foreach ($vhdPath in $distribution.VhdPaths) {
        $previousSizeBytes = (Get-Item -LiteralPath $vhdPath).Length
        $optimized = $false

        if ($PSCmdlet.ShouldProcess($vhdPath, "Optimize-VHD -Mode $Mode")) {
            Optimize-VHD -Path $vhdPath -Mode $Mode
            $optimized = $true
        }

        $newSizeBytes = (Get-Item -LiteralPath $vhdPath).Length
        $savedBytes = $previousSizeBytes - $newSizeBytes
        $savingsPercent = if ($previousSizeBytes -gt 0) {
            [math]::Round(($savedBytes / $previousSizeBytes) * 100, 2)
        }
        else {
            0
        }

        Write-Host (
            '{0}: {1} -> {2} ({3:N2}% saved)' -f
            $distribution.DistributionName,
            (Format-ByteSize -SizeBytes $previousSizeBytes),
            (Format-ByteSize -SizeBytes $newSizeBytes),
            $savingsPercent
        )

        [PSCustomObject]@{
            DistributionName  = $distribution.DistributionName
            Identifier        = $distribution.Identifier
            BasePath          = $distribution.BasePath
            VhdPath           = $vhdPath
            PreviousSizeBytes = $previousSizeBytes
            NewSizeBytes      = $newSizeBytes
            SavedBytes        = $savedBytes
            PreviousSize      = Format-ByteSize -SizeBytes $previousSizeBytes
            NewSize           = Format-ByteSize -SizeBytes $newSizeBytes
            SavingsPercent    = $savingsPercent
            Optimized         = $optimized
            Mode              = $Mode
        }
    }
}

$results
