<#
Setup script for Mosquitto: generates a local CA, server certs and creates a password file.
Run this on the VM where the compose will run. The script requires either `openssl` installed
or Docker (to run an openssl container). It also uses Docker to run `mosquitto_passwd`.

Usage examples:
.
# Interactive username prompt
#  .\setup-mosquitto.ps1

# Non-interactive with password (PowerShell):
#  .\setup-mosquitto.ps1 -Username myuser -Password mypassword

# WARNING: This script writes private keys to ./certs in this directory. Do NOT commit them.
# Add ./certs and ./passwd to your .gitignore.
#>

param(
    [string]$Username = $(Read-Host "Enter MQTT username"),
    [string]$Password = $(Read-Host "Enter MQTT password" -AsSecureString)
)

Set-StrictMode -Version Latest

$base = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $base

if (-not (Test-Path -Path .\certs)) { New-Item -ItemType Directory -Path .\certs | Out-Null }

# convert secure string to plain if provided as secure string
if ($Password -is [System.Security.SecureString]) {
    $pwPtr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
    try { $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($pwPtr) } finally { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pwPtr) }
} else { $plainPassword = $Password }

function Run-OpenSSL {
    param($args)
    if (Get-Command openssl -ErrorAction SilentlyContinue) {
        openssl $args
    } else {
        Write-Host "openssl not found locally — using docker image frapsoft/openssl to run openssl"
        docker run --rm -v "${PWD}:/work" -w /work frapsoft/openssl openssl $args
    }
}

Write-Host "Generating CA and server certificate (self-signed for testing) in ./certs ..."

# CA key and cert
Run-OpenSSL 'genrsa -out certs/ca.key 4096'
Run-OpenSSL 'req -x509 -new -nodes -key certs/ca.key -sha256 -days 3650 -out certs/ca.crt -subj "/CN=LocalMosquittoCA"'

# Server key and CSR
Run-OpenSSL 'genrsa -out certs/server.key 2048'
Run-OpenSSL 'req -new -key certs/server.key -out certs/server.csr -subj "/CN=mosquitto"'

# Sign server cert with CA
Run-OpenSSL 'x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/server.crt -days 3650 -sha256'

Write-Host "Certificates created: certs/ca.crt certs/server.crt certs/server.key"

if (-not (Test-Path -Path .\passwd)) {
    Write-Host "Creating password file (passwd) with user: $Username"
    # prefer using mosquitto_passwd inside docker image
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker not available — cannot create password file automatically. Install Docker or create passwd manually with mosquitto_passwd."
        Pop-Location
        exit 1
    }
    # use -b to provide password non-interactively
    docker run --rm -v "${PWD}:/mosquitto/config" eclipse-mosquitto:1.6 mosquitto_passwd -c -b /mosquitto/config/passwd $Username $plainPassword | Out-Null
    Write-Host "Password file created at ./passwd"
} else {
    Write-Host "./passwd already exists — skipping creation. To add user run: docker run --rm -v \"${PWD}:/mosquitto/config\" eclipse-mosquitto:1.6 mosquitto_passwd /mosquitto/config/passwd newuser"
}

Write-Host "Remember to add ./certs and ./passwd to .gitignore to avoid committing secrets."
Pop-Location
