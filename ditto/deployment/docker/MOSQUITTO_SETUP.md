# Configuração básica do Mosquitto com Username/Password e TLS (para VM)

Este guia descreve como habilitar autenticação por usuário/senha e TLS (SSL) para o serviço `mosquitto` usado pelo ambiente Ditto. As instruções presumem que você vai executar os comandos dentro da VM onde o compose será executado.

Local de trabalho (no repositório):

- `ditto/deployment/docker` — aqui existem `docker-compose.yml` e será criado `mosquitto.conf`.

Resumo das ações:

- Criar diretório `certs/` e gerar CA e certificado do servidor (self-signed para testes).
- Criar `passwd` com `mosquitto_passwd` (via container) e colocá-lo em `./passwd`.
- Garantir que `docker-compose.yml` monte `./passwd` e `./certs` em `/mosquitto/config/` (persistência no host/VM).
- Subir o serviço `mosquitto` e testar com `mosquitto_pub`/`mosquitto_sub` usando `--cafile`.

Observações importantes sobre persistência:

- O `passwd` e os certificados ficam em diretório no host/VM (`ditto/deployment/docker/passwd` e `ditto/deployment/docker/certs`). Como são arquivos montados no container, ao executar `docker compose down` os arquivos permanecem no disco da VM e não são removidos automaticamente. Não use `docker compose down -v` se você tiver volumes named e quer mantê-los — neste setup os arquivos estão montados como bind mounts, então persistem.
- NÃO comite chaves privadas (`server.key`) no repositório. Coloque `certs/` e `passwd` no `.gitignore` se não quiser versionar.

Gerar certificados (exemplo com OpenSSL) — dentro da VM (Bash):

```bash
# vá para o diretório do compose
cd /path/to/repo/ditto/deployment/docker
mkdir -p certs

# gerar CA (privada) e certificado CA
openssl genrsa -out certs/ca.key 4096
openssl req -x509 -new -nodes -key certs/ca.key -sha256 -days 3650 -out certs/ca.crt -subj "/CN=LocalMosquittoCA"

# gerar chave do servidor e CSR
openssl genrsa -out certs/server.key 2048
openssl req -new -key certs/server.key -out certs/server.csr -subj "/CN=mosquitto"

# assinar CSR com a CA
openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/server.crt -days 3650 -sha256
```

Se você estiver em PowerShell no host (e a VM usa compartilhamento de pastas), adapte caminhos. É preferível executar os comandos acima dentro da VM (Linux).

Criar `passwd` (usar utilitário `mosquitto_passwd` dentro do container):

```bash
# cria/ sobrescreve passwd com um usuário
docker run --rm -it -v "${PWD}:/mosquitto/config" eclipse-mosquitto:1.6 mosquitto_passwd -c /mosquitto/config/passwd myuser

# ou criar sem interação (não recomendado deixar senha no histórico):
docker run --rm -it -v "${PWD}:/mosquitto/config" eclipse-mosquitto:1.6 mosquitto_passwd -b /mosquitto/config/passwd myuser mypassword

# para adicionar mais usuários (sem -c):
docker run --rm -it -v "${PWD}:/mosquitto/config" eclipse-mosquitto:1.6 mosquitto_passwd /mosquitto/config/passwd anotheruser
```

Configuração do compose

- O `docker-compose.yml` já está preparado para montar `./mosquitto.conf`, `./passwd` e `./certs` em `/mosquitto/config/`. A porta TLS `8883` também está mapeada para o host/VM.

Subir apenas o Mosquitto (após gerar `certs` e `passwd`):

```bash
cd /path/to/repo/ditto/deployment/docker
docker compose up -d mosquitto
```

Testes (no VM):

Assumindo que você gerou `certs/ca.crt` e criou `passwd` com usuário `myuser`:

```bash
# abrir um subscriber usando TLS
mosquitto_sub -h localhost -p 8883 -t 'test/topic' -u 'myuser' -P 'mypassword' --cafile ./certs/ca.crt

# publicar
mosquitto_pub -h localhost -p 8883 -t 'test/topic' -m 'hello' -u 'myuser' -P 'mypassword' --cafile ./certs/ca.crt
```

Se você não tiver `mosquitto_pub/sub` instalado na VM, pode usar o cliente dentro do container:

```bash
docker run --rm -it --network host eclipse-mosquitto:1.6 mosquitto_pub -h localhost -p 8883 -t 'test/topic' -m 'hello' -u 'myuser' -P 'mypassword' --cafile /mosquitto/config/certs/ca.crt
```

Notas finais e segurança

- Em produção, use certificados emitidos por CA pública (Let’s Encrypt, etc.).
- Proteja as chaves privadas e não as armazene em repositórios públicos.
- Considere usar `acl_file` para controlar acesso a tópicos (ex.: permitir que um usuário apenas publique em um tópico específico).
