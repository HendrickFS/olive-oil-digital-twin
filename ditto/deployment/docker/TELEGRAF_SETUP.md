# Configuração do Telegraf para MQTT → InfluxDB

## 📋 O que foi configurado

O Telegraf foi adicionado ao seu stack Docker para:

1. **Ler dados MQTT** diretamente do Mosquitto
2. **Fazer parsing correto** dos valores JSON
3. **Converter tipos de dados** adequadamente (0/1 como inteiros, temperatures como floats)
4. **Gravar no InfluxDB** com tipos corretos

## 🏗️ Arquitetura Atualizada

```
IoT Sensors
    ↓
MQTT Broker (Mosquitto:1884)
    ├─→ Ditto (Digital Twin)
    └─→ Telegraf (Data Ingestion)
        ↓
    InfluxDB (Time Series)
        ↓
    Flask API
```

## 🚀 Como executar

### 1. Certifique-se que o `.env` está configurado

Edite `dev.env` ou crie um `.env` com as variáveis:

```bash
DOCKER_INFLUXDB_INIT_MODE=setup
DOCKER_INFLUXDB_INIT_USERNAME=admin
DOCKER_INFLUXDB_INIT_PASSWORD=admin123
DOCKER_INFLUXDB_INIT_ORG=SustainOlive
DOCKER_INFLUXDB_INIT_BUCKET=DigitalTwin
DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=seu-token-aqui
```

### 2. Iniciar os serviços

```bash
docker-compose up -d
```

### 3. Verificar logs do Telegraf

```bash
docker logs telegraf
```

## 📊 Que dados são coletados

O Telegraf coleta dos seguintes tópicos MQTT:

- `bin/incoming/#`
- `mill/incoming/#`
- `centrifuge/incoming/#`
- `decanter/incoming/#`
- `mixer/incoming/#`
- `deposit/incoming/#`
- `auger/incoming/#`
- `pump/incoming/#`
- `sieve/incoming/#`
- `belt/incoming/#`

## 🔧 Configuração de Mensagens MQTT

As mensagens devem estar no formato JSON com a estrutura abaixo:

```json
{
  "thingId": "olive.production:bin001",
  "temperature": 23.5,
  "state": 1,
  "timestamp": "2025-12-15T10:30:45.000Z"
}
```

**Campos obrigatórios:**
- `thingId`: Identificador único do dispositivo
- Pelo menos um campo numérico (temperatura, umidade, estado, etc)

**Campos opcionais:**
- `timestamp`: Horário da medição (ISO 8601)

## 📈 Verificar dados no InfluxDB

1. Abra: http://localhost:9999
2. Login: `admin` / `admin123`
3. Vá para **Data Explorer**
4. Selecione bucket **DigitalTwin**
5. Filtre por tag `thingId`

## ⚙️ Ajustar tópicos MQTT

Se seus tópicos MQTT são diferentes, edite `telegraf.conf`:

```toml
[[inputs.mqtt_consumer]]
  servers = ["tcp://mosquitto:1884"]
  topics = ["seu/topico/aqui/#"]  # ← Mudar aqui
  username = "sustainolive"
  password = "sustainolive"
  # ... resto da config
```

## 🛠️ Troubleshooting

### Telegraf não conecta ao Mosquitto

```bash
# Verificar conectividade
docker exec telegraf mosquitto_pub -h mosquitto -u sustainolive -P sustainolive -t test -m "teste"
```

### Dados não aparecem no InfluxDB

1. Verificar logs: `docker logs telegraf`
2. Verificar formato JSON das mensagens MQTT
3. Confirmar que o token do InfluxDB está correto

### Valores ainda com tipo errado

Edite a seção `[processors.converter]` em `telegraf.conf`:

```toml
[[processors.converter]]
  [processors.converter.fields]
    float = ["temperature", "humidity"]
    int = ["state", "count"]
```

## 💡 Próximos passos

1. **Desativar o serviço Java** `influxdb_connection` para evitar conflitos
2. **Executar testes** com dados MQTT reais
3. **Monitorar performance** em produção

## 📚 Recursos

- [Documentação Telegraf](https://docs.influxdata.com/telegraf/)
- [Plugin MQTT Consumer](https://docs.influxdata.com/telegraf/latest/plugins/#input-mqtt-consumer)
- [InfluxDB v2 Output](https://docs.influxdata.com/telegraf/latest/plugins/#output-influxdb-v2)
