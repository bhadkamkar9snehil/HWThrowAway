$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/bhadkamkar9snehil/HWThrowAway.git"
$Home = Join-Path $env:LOCALAPPDATA "PrototypeEngineering\HWThrowAway"
$Repo = Join-Path $Home "repo"
$Venv = Join-Path $Home ".venv"
$TaskName = "PrototypeEngineeringRunner-HWThrowAway"

New-Item -ItemType Directory -Force -Path $Home | Out-Null

if (-not (Test-Path (Join-Path $Repo ".git"))) {
    git clone $RepoUrl $Repo
} else {
    git -C $Repo fetch --prune origin
    git -C $Repo checkout main
    git -C $Repo reset --hard origin/main
}

if (-not (Test-Path (Join-Path $Venv "Scripts\python.exe"))) {
    py -3 -m venv $Venv
}

$Python = Join-Path $Venv "Scripts\python.exe"
$PythonW = Join-Path $Venv "Scripts\pythonw.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install -r (Join-Path $Repo "requirements.txt")

# Use an isolated commit identity for evidence commits from the managed clone.
git -C $Repo config user.name "Prototype Engineering Runner"
git -C $Repo config user.email "prototype-runner@localhost"

$Runner = Join-Path $Repo "prototype_runner\daemon.py"
$Action = New-ScheduledTaskAction -Execute $PythonW -Argument ('"{0}" --repo-root "{1}" --interval 30' -f $Runner, $Repo)
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs queued prototype engineering jobs from GitHub prototype/* branches." -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName

Write-Host "Prototype runner installed and started."
Write-Host "Runner repo: $Repo"
Write-Host "Task: $TaskName"
Write-Host "Important: git push from this clone must authenticate with your existing GitHub credentials."
