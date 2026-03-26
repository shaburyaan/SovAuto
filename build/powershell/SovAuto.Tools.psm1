Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$script:RepoSlug = "shaburyaan/SovAuto"
$script:RemoteUrl = "https://github.com/shaburyaan/SovAuto.git"
$script:RepoHomepage = "https://github.com/shaburyaan/SovAuto"
$script:RepoDescription = "SovAuto is a Windows desktop application for capturing live 1C windows, recording reusable scenarios, and replaying them with controlled delays. | SovAuto — Windows-приложение для захвата окон 1С, записи сценариев и их воспроизведения с управляемыми задержками."

function Get-SovAutoVersion {
    $versionFile = Join-Path $script:RepoRoot "build\version\version.txt"
    return (Get-Content $versionFile -Raw).Trim()
}

function Set-SovAutoVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Version
    )

    $version = $Version.Trim()
    if (-not $version) {
        throw "Version is required."
    }

    $versionFile = Join-Path $script:RepoRoot "build\version\version.txt"
    $pyprojectPath = Join-Path $script:RepoRoot "pyproject.toml"
    $issPath = Join-Path $script:RepoRoot "SovAuto.iss"

    Set-Content -Path $versionFile -Value $version -Encoding utf8

    $pyprojectLines = Get-Content $pyprojectPath
    $pyprojectLines = $pyprojectLines | ForEach-Object {
        if ($_ -match '^version = ".*"$') {
            "version = `"$version`""
        } else {
            $_
        }
    }
    Set-Content -Path $pyprojectPath -Value $pyprojectLines -Encoding utf8

    $iss = Get-Content $issPath -Raw
    $iss = [regex]::Replace($iss, '(?m)^AppVersion=.*$', "AppVersion=$version")
    $iss = [regex]::Replace($iss, '(?m)^OutputBaseFilename=.*$', "OutputBaseFilename=SovAuto-Setup-$version")
    Set-Content -Path $issPath -Value $iss -Encoding utf8
}

function Invoke-SovAutoScript {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath
    )

    $scriptPath = Join-Path $script:RepoRoot $RelativePath
    if (-not (Test-Path $scriptPath)) {
        throw "Script not found: $scriptPath"
    }

    & $scriptPath
}

function Copy-SovAutoInstallerToDesktop {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Version
    )

    $desktop = [Environment]::GetFolderPath("Desktop")
    $targetDir = Join-Path $desktop "SovAuto-Installer-$Version"
    $installerPath = Join-Path $script:RepoRoot "dist_installer\SovAuto-Setup-$Version.exe"
    $readmePath = Join-Path $targetDir "README.txt"

    if (-not (Test-Path $installerPath)) {
        throw "Installer not found: $installerPath"
    }

    if (Test-Path $targetDir) {
        Remove-Item $targetDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    Copy-Item $installerPath $targetDir -Force

    @(
        "SovAuto installer package / Установочный пакет SovAuto"
        "Version / Версия: $Version"
        ""
        "Contents / Содержимое:"
        "- SovAuto-Setup-$Version.exe"
        ""
        "Install flow / Установка:"
        "1. Run the installer. / Запустите установщик."
        "2. Finish setup. / Завершите установку."
        "3. Launch SovAuto from Start Menu or Desktop. / Запустите SovAuto из меню Пуск или с рабочего стола."
    ) | Set-Content -Path $readmePath -Encoding utf8

    return $targetDir
}

function buildAuto {
    [CmdletBinding()]
    param(
        [string]$Version
    )

    Push-Location $script:RepoRoot
    try {
        if ($Version) {
            Set-SovAutoVersion -Version $Version
        }

        $resolvedVersion = Get-SovAutoVersion
        Invoke-SovAutoScript -RelativePath "build\scripts\build_app.ps1"
        Invoke-SovAutoScript -RelativePath "build\scripts\build_installer.ps1"
        $targetDir = Copy-SovAutoInstallerToDesktop -Version $resolvedVersion
        Write-Host "SovAuto installer prepared at $targetDir"
    } finally {
        Pop-Location
    }
}

function Initialize-SovAutoGitRepo {
    $gitDir = Join-Path $script:RepoRoot ".git"
    if (-not (Test-Path $gitDir)) {
        git -C $script:RepoRoot init -b main
        if ($LASTEXITCODE -ne 0) {
            throw "git init failed."
        }
    }

    $remoteExists = git -C $script:RepoRoot remote
    if ($remoteExists -notcontains "origin") {
        git -C $script:RepoRoot remote add origin $script:RemoteUrl
    } else {
        git -C $script:RepoRoot remote set-url origin $script:RemoteUrl
    }
}

function Update-SovAutoGitHubMetadata {
    gh repo edit $script:RepoSlug `
        --description $script:RepoDescription `
        --homepage $script:RepoHomepage `
        --add-topic windows `
        --add-topic pyqt6 `
        --add-topic desktop-automation `
        --add-topic 1c-enterprise
    if ($LASTEXITCODE -ne 0) {
        throw "gh repo edit failed."
    }
}

function Resolve-SovAutoBootstrapMergeConflict {
    $conflicts = git -C $script:RepoRoot diff --name-only --diff-filter=U
    if ($LASTEXITCODE -ne 0) {
        throw "git conflict inspection failed."
    }
    if (@($conflicts).Count -eq 1 -and $conflicts[0] -eq "README.md") {
        git -C $script:RepoRoot checkout --ours -- README.md
        if ($LASTEXITCODE -ne 0) {
            throw "git checkout --ours README.md failed."
        }
        git -C $script:RepoRoot add README.md
        if ($LASTEXITCODE -ne 0) {
            throw "git add README.md failed."
        }
        git -C $script:RepoRoot commit --no-edit
        if ($LASTEXITCODE -ne 0) {
            throw "git merge commit failed."
        }
        return
    }
    throw "git pull failed."
}

function pushAuto {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $commitMessage = $Message.Trim()
    if (-not $commitMessage) {
        throw "Commit message is required."
    }

    Push-Location $script:RepoRoot
    try {
        Initialize-SovAutoGitRepo
        $remoteMain = git ls-remote --heads origin main

        git -C $script:RepoRoot add .
        if ($LASTEXITCODE -ne 0) {
            throw "git add failed."
        }

        git -C $script:RepoRoot commit -m $commitMessage
        if ($LASTEXITCODE -ne 0) {
            $status = git -C $script:RepoRoot status --short
            if (-not $status) {
                Write-Host "No changes to commit."
            } else {
                throw "git commit failed."
            }
        }

        if ($remoteMain) {
            git -C $script:RepoRoot pull origin main --allow-unrelated-histories --no-rebase --no-edit
            if ($LASTEXITCODE -ne 0) {
                Resolve-SovAutoBootstrapMergeConflict
            }
        }

        git -C $script:RepoRoot push -u origin main
        if ($LASTEXITCODE -ne 0) {
            throw "git push failed."
        }

        Update-SovAutoGitHubMetadata
    } finally {
        Pop-Location
    }
}

Export-ModuleMember -Function buildAuto, pushAuto
