function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {
    const jsonString = String.fromCharCode.apply(null, new Uint8Array(bytePayload)); 
    const jsonData = JSON.parse(jsonString); 
    const thingId = (jsonData.thingId ?? 'olive.deposits:deposit001').split(':'); //Uses a default deposit if not received via MQTT
    const value = {
        temperature: {
            properties: {
                value: jsonData.temperature ?? jsonData.temperatura ?? 0
            }
        },
        humidity: {
            properties: {
                value: jsonData.humidity ?? jsonData.umidade ?? 0
            }
        },
        mq: {
            properties: {
                value: jsonData.mq
            }
        }
    }; 
    return Ditto.buildDittoProtocolMsg(thingId[0], thingId[1], 'things', 'twin', 'commands', 'modify', '/features', headers, value);
}

function mapFromDittoProtocolMsg(namespace, id, group, channel, criterion, action, path, dittoHeaders, value, status, extra) {
    return null;
}