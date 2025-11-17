#!/usr/bin/env bash
set -euo pipefail

# setup_mosquitto_vm.sh
# Gera CA e certificado do servidor (self-signed), cria arquivo de senhas
# usando o utilitário mosquitto_passwd dentro do container e ajusta
# permissões. Projetado para rodar dentro da VM onde o compose será executado.

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

CERTS_DIR="$BASE_DIR/certs"
PASSWD_FILE="$BASE_DIR/passwd"
CA_KEY="$CERTS_DIR/ca.key"
CA_CRT="$CERTS_DIR/ca.crt"
SERVER_KEY="$CERTS_DIR/server.key"
SERVER_CSR="$CERTS_DIR/server.csr"
SERVER_CRT="$CERTS_DIR/server.crt"
CA_SERIAL="$CERTS_DIR/ca.srl"

DOCKER_IMAGE="eclipse-mosquitto:1.6"

OVERWRITE_PASSWD=false
NONINTERACTIVE=false
USERNAME=""
PASSWORD=""
CN="mosquitto"

usage() {
  cat <<EOF
Usage: $0 [-u username] [-p password] [-c commonName] [-o] [-n]

  -u username      Username to add to mosquitto passwd (will prompt if omitted)
  -p password      Password for the user (if omitted, will prompt securely)
  -c commonName    Common Name for server certificate (default: mosquitto)
  -o               Overwrite existing passwd file (passes -c to mosquitto_passwd)
  -n               Non-interactive: requires -u and -p
  -h               Show this help

This script must be run inside the VM where Docker is available (to run mosquitto_passwd).
Generated files are placed in: $BASE_DIR/certs and $BASE_DIR/passwd
Do NOT commit private keys or passwd to git. Ensure these paths are in .gitignore.
EOF
}

while getopts ":u:p:c:onh" opt; do
  case ${opt} in
    u ) USERNAME="$OPTARG" ;;
    p ) PASSWORD="$OPTARG" ;;
    c ) CN="$OPTARG" ;;
    o ) OVERWRITE_PASSWD=true ;;
    n ) NONINTERACTIVE=true ;;
    h ) usage; exit 0 ;;
    \? ) echo "Invalid Option: -$OPTARG" 1>&2; usage; exit 1 ;;
  esac
done

if ! command -v openssl >/dev/null 2>&1; then
  echo "Warning: openssl not found. Install openssl to generate certificates." >&2
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is required to run mosquitto_passwd (install or enable docker)." >&2
  exit 1
fi

mkdir -p "$CERTS_DIR"

echo "[1/5] Gerando certificados (se não existirem)"
if [[ ! -f "$CA_KEY" || ! -f "$CA_CRT" ]]; then
  echo " - Criando CA privada e certificado CA"
  openssl genrsa -out "$CA_KEY" 4096
  openssl req -x509 -new -nodes -key "$CA_KEY" -sha256 -days 3650 -out "$CA_CRT" -subj "/CN=LocalMosquittoCA"
else
  echo " - CA já existe, pulando geração"
fi

if [[ ! -f "$SERVER_KEY" || ! -f "$SERVER_CRT" ]]; then
  echo " - Criando chave do servidor e assinando com CA"
  openssl genrsa -out "$SERVER_KEY" 2048
  openssl req -new -key "$SERVER_KEY" -out "$SERVER_CSR" -subj "/CN=${CN}"
  openssl x509 -req -in "$SERVER_CSR" -CA "$CA_CRT" -CAkey "$CA_KEY" -CAcreateserial -out "$SERVER_CRT" -days 3650 -sha256
else
  echo " - Certificado do servidor já existe, pulando geração"
fi

echo "[2/5] Ajustando permissões de chaves"
chmod 600 "$SERVER_KEY" || true

echo "[3/5] Criando/atualizando arquivo de senhas mosquitto"
if [[ -z "$USERNAME" ]]; then
  if $NONINTERACTIVE; then
    echo "Non-interactive requested but no username provided" >&2
    exit 1
  fi
  read -rp "Username to create: " USERNAME
fi

if [[ -z "$PASSWORD" ]]; then
  if $NONINTERACTIVE; then
    echo "Non-interactive requested but no password provided" >&2
    exit 1
  fi
  read -rs -p "Password for $USERNAME: " PASSWORD
  echo
fi

PASSWD_PATH="/mosquitto/config/passwd"
MOSQUITTO_PASSWD_ARGS=()
if $OVERWRITE_PASSWD; then
  # create (overwrite) and provide password non-interactively
  MOSQUITTO_PASSWD_ARGS=( -c -b )
else
  # add user non-interactively
  MOSQUITTO_PASSWD_ARGS=( -b )
fi

echo " - Usando imagem: $DOCKER_IMAGE para gerar passwd"
docker run --rm -it -v "$BASE_DIR":/mosquitto/config "$DOCKER_IMAGE" mosquitto_passwd ${MOSQUITTO_PASSWD_ARGS[*]} "$PASSWD_PATH" "$USERNAME" "$PASSWORD"

echo "[4/5] Ajustando permissões do passwd"
chmod 600 "$PASSWD_FILE" || true

echo "[5/5] Finalizado"
cat <<EOF
Arquivos gerados (não commite estes arquivos):
  - $CERTS_DIR/
    - ca.crt
    - server.crt
    - server.key
  - $PASSWD_FILE

Para subir o serviço mosquitto (na VM, dentro do diretório do compose):
  docker compose up -d mosquitto

Testar com mosquitto_pub/sub (na VM):
  mosquitto_sub -h localhost -p 8883 -t 'test/topic' -u '$USERNAME' -P '$PASSWORD' --cafile $CERTS_DIR/ca.crt
  mosquitto_pub -h localhost -p 8883 -t 'test/topic' -m 'hello' -u '$USERNAME' -P '$PASSWORD' --cafile $CERTS_DIR/ca.crt

Lembre-se: não rode 'docker compose down -v' se você quer manter volumes bind-mounted; os arquivos que importam são bind mounts no repositório (persistem no filesystem da VM).
EOF

exit 0
