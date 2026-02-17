# run_local.ps1
# This script automates the local setup and running of the backend and frontend.

$ErrorActionPreference = "Stop"

# --- Configuration ---
$BackendDir = "backend"
$FrontendDir = "frontend"
$BackendHealthCheckUrl = "http://localhost:8000/" # Using the root endpoint for health check
$FrontendPort = 3000

# --- Helper Functions ---
function Write-Log {
    Param (
        [string]$Message,
        [string]$Level = "INFO" # INFO, WARNING, ERROR, SUCCESS
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Prefix = ""
    switch ($Level) {
        "INFO" { $Prefix = "[INFO]" }
        "WARNING" { $Prefix = "[WARNING]" }
        "ERROR" { $Prefix = "[ERROR]" }
        "SUCCESS" { $Prefix = "[SUCCESS]" }
    }
    Write-Host "$Prefix [$Timestamp] $Message"
}

function Test-BackendHealth {
    Param (
        [string]$Url
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSeconds 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200 -and $response.Content -like "*healthy*") {
            return $true
        }
    } catch {
        # Ignore errors for now, as the server might not be up yet
    }
    return $false
}

# --- Backend Setup and Run ---
Write-Log "Starting backend setup and run..."
Push-Location $BackendDir

Write-Log "Checking for Python virtual environment..."
if (-not (Test-Path "venv/Scripts/activate.ps1")) {
    Write-Log "Virtual environment not found. Creating..."
    python -m venv venv
    Write-Log "Virtual environment created."
} else {
    Write-Log "Virtual environment found."
}

Write-Log "Activating virtual environment..."
# Execute the activate script directly using '.' operator for current scope
. .\venv\Scripts\activate.ps1
Write-Log "Virtual environment activated."

Write-Log "Installing backend dependencies..."
pip install -r requirements.txt
Write-Log "Backend dependencies installed."

Write-Log "Starting backend server in the background..."
# Start-Job runs in a separate process, which is good for detaching.
# We need to capture the job object to stop it later if needed.
# Redirect stdout and stderr to a log file for debugging.
$backendJob = Start-Job -ScriptBlock { uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 *>&1 | Out-File -FilePath "uvicorn_startup.log" }
Start-Sleep -Seconds 2 # Give it a moment to start
Write-Log "Backend server started. Checking health. Check 'backend/uvicorn_startup.log' for details."

$MaxRetries = 30
$RetryInterval = 5
for ($i = 0; $i -lt $MaxRetries; $i++) {
    if (Test-BackendHealth $BackendHealthCheckUrl) {
        Write-Log "Backend is healthy." "SUCCESS"
        break
    }
    Write-Log "Waiting for backend to be healthy (attempt $($i+1)/$MaxRetries)..."
    Start-Sleep -Seconds $RetryInterval
    if ($i -eq $MaxRetries - 1) {
        Write-Log "Backend did not become healthy after multiple retries. Aborting frontend startup." "ERROR"
        # Stop the backend job before exiting
        Stop-Job -Job $backendJob -ErrorAction SilentlyContinue | Out-Null
        Remove-Job -Job $backendJob -ErrorAction SilentlyContinue | Out-Null
        Pop-Location # Go back to original directory
        exit 1
    }
}
Pop-Location # Go back to original directory

# --- Frontend Setup and Run ---
Write-Log "Starting frontend setup and run..."
Push-Location $FrontendDir

Write-Log "Installing frontend dependencies..."
npm install
Write-Log "Frontend dependencies installed."

Write-Log "Starting frontend development server..."
# Using Start-Process for frontend as it's typically foreground for development.
# -NoNewWindow keeps it from opening a new console window if run from powershell ISE or similar.
# This process will be tied to the current powershell window, so closing this window will close npm.
Start-Process -FilePath "npm" -ArgumentList "run dev" -NoNewWindow

Write-Log "Frontend server started. Access at http://localhost:$FrontendPort" "SUCCESS"

Write-Log "Local environment setup complete. Backend and Frontend are running." "SUCCESS"
Write-Log "To stop the backend, you may need to find and kill the uvicorn process."
Write-Log "To stop the frontend, close the console window where 'npm run dev' is running, or find and kill the node process."

<#
Keep the script running if the user wants to keep the terminal open and monitor logs
If the script exits, the Start-Process for npm might close.
For simplicity, we'll let it exit after launching, as the user can then monitor the npm window.
If this was a more robust orchestration, we would manage these processes.
#>
