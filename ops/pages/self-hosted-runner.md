# Self-hosted Windows runner (Plan A)

Target: move the three compute-heavy refreshes off hosted minutes and onto
Richard's Windows box, then (after a week of stability) flip the repo private.

The switch is a repository **variable**, not a code change:

```
CL_RUNNER = self-hosted        # or delete the variable to fall back
```

`runs-on: ${{ vars.CL_RUNNER || 'ubuntu-latest' }}` in
`update_evaluations.yml`, `update_weather.yml`, `b169_kv_sync.yml`. Unset =
today's behaviour, so the rollback is a settings change, not a revert.

## Not yet switched

`v2-integration.yml` stays hosted for now: it installs Playwright + Chromium,
needs `sudo apt-get` for CJK fonts, and its sparse checkout is a bash script.
Porting it to Windows needs a Linux runner or a WSL install — separate ticket.

## Registering the runner (once, on the owner's box)

Registration token comes from
`Settings → Actions → Runners → New self-hosted runner` (or
`POST /repos/:owner/:repo/actions/runners/registration-token`, expires in 1h).

```powershell
# 1. download + unpack (version pin: check the New runner page for the current one)
New-Item -ItemType Directory -Force C:\actions-runner-chaselights | Out-Null
cd C:\actions-runner-chaselights
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-win-x64-2.321.0.zip -OutFile runner.zip
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::ExtractToDirectory("$PWD\runner.zip", "$PWD")

# 2. unattended configure (no prompts; --replace-safe avoids a stale .runner file)
.\config.cmd --unattended --replace `
  --url https://github.com/gdrabbit137-ai/ChaseLights `
  --token <REGISTRATION_TOKEN> `
  --name chaselights-pc `
  --labels self-hosted,windows `
  --work C:\actions-runner-chaselights\_work

# 3. install as a Windows service (survives logout/reboot)
.\svc.cmd install
.\svc.cmd start
```

### Priority: BelowNormal

The runner must never starve the desktop. Set it on the service process, not the
CI job:

```powershell
# 1. lower the service's own priority at start
.\svc.cmd status        # confirm it is running

# 2. every job runs under the service's process tree, so renicing the service
#    is enough; verify with the runner's own process id
Get-Process -Name "Runner.Listener" | ForEach-Object { $_.PriorityClass = "BelowNormal" }
```

The `Get-Process` line is a one-shot — after a service restart the class resets.
Make it permanent with a scheduled task triggered at boot:

```powershell
schtasks /create /tn "chaselights-runner-belownormal" /sc onstart /ru SYSTEM /rl HIGHEST `
  /tr "powershell -NoProfile -Command \"Get-Process -Name 'Runner.Listener','Runner.Worker' -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'BelowNormal' }\""
```

### Requirements on the box

- Python 3.12 on PATH (the evaluator imports `jsonschema`, `PyYAML`, `tzdata`)
- Node 24+ (`node --version`) for the artifact-coupled test gate
- Git for Windows (checkout uses the bundled git)
- Disk: the evaluations job writes ~250 MB per run; keep 5 GB free

## Verification after the runner is online

1. `Settings → Actions → Runners` shows `chaselights-pc` **Idle**.
2. Set `CL_RUNNER=self-hosted`, run `Update V2 Opportunity Evaluations` via
   *Run workflow*, and confirm the log says
   `Runner name: chaselights-pc` and the job finishes in the same wall time.
3. Confirm `weather_details/` objects in R2 changed timestamp (the direct
   upload step now runs on this box).
4. Delete `CL_RUNNER` to fall back if anything regresses.
