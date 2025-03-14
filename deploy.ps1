# BuzzTracker TweetBot Dashboard Deployment Script for Windows (PowerShell)
# Run this script from your project root directory

Write-Host "=== BuzzTracker TweetBot Dashboard Deployment ===" -ForegroundColor Cyan

# Step 1: Check for .env file or create it
if (-not (Test-Path -Path ".env")) {
    Write-Host "MongoDB connection information required" -ForegroundColor Cyan
    Write-Host "Enter your MongoDB URI:" -ForegroundColor Cyan
    $mongodb_uri = Read-Host -AsSecureString
    $mongodb_uri_plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($mongodb_uri))
    
    Write-Host "Enter your MongoDB Database name:" -ForegroundColor Cyan
    $mongodb_database = Read-Host
    
    # Create .env file
    "MONGODB_URI=$mongodb_uri_plain" | Out-File -FilePath ".env"
    "MONGODB_DATABASE=$mongodb_database" | Add-Content -Path ".env"
    Write-Host "Created .env file with MongoDB credentials" -ForegroundColor Green
} else {
    Write-Host "Found existing .env file" -ForegroundColor Green
}

# Step 2: Add .env to .gitignore if not already there
if (-not (Test-Path -Path ".gitignore")) {
    ".env" | Out-File -FilePath ".gitignore"
    Write-Host "Created .gitignore file and added .env to it" -ForegroundColor Green
} elseif (-not (Select-String -Path ".gitignore" -Pattern ".env" -SimpleMatch -Quiet)) {
    ".env" | Add-Content -Path ".gitignore"
    Write-Host "Added .env to .gitignore" -ForegroundColor Green
} else {
    Write-Host ".env already in .gitignore" -ForegroundColor Green
}

# Step 3: Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Cyan
docker build -t tweetbot-analytics-dashboard .

# Step 4: Check for existing containers and remove them
Write-Host "Checking for existing containers..." -ForegroundColor Cyan
docker stop tweetbot-analytics-dashboard 2>$null
docker rm tweetbot-analytics-dashboard 2>$null

# Step 5: Run container with environment variables from .env file
Write-Host "Starting container..." -ForegroundColor Cyan
# Read values from .env file
$env_content = Get-Content -Path ".env"
$mongodb_uri = ($env_content | Where-Object { $_ -match "MONGODB_URI=" }) -replace "MONGODB_URI=", ""
$mongodb_database = ($env_content | Where-Object { $_ -match "MONGODB_DATABASE=" }) -replace "MONGODB_DATABASE=", ""

# Run Docker container with environment variables
docker run -d `
  --name tweetbot-analytics-dashboard `
  -p 8080:8080 `
  -e MONGODB_URI="$mongodb_uri" `
  -e MONGODB_DATABASE="$mongodb_database" `
  tweetbot-analytics-dashboard

# Step 6: Check if container is running
$container_running = docker ps -q -f name=tweetbot-analytics-dashboard
if ($container_running) {
    Write-Host "BuzzTracker TweetBot Dashboard deployed successfully!" -ForegroundColor Green
    Write-Host "Access the dashboard at http://localhost:8080" -ForegroundColor Green
} else {
    Write-Host "Deployment failed. Check Docker logs with: docker logs tweetbot-analytics-dashboard" -ForegroundColor Red
}