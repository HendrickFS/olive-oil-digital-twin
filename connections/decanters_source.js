function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {
    const jsonString = String.fromCharCode.apply(null, new Uint8Array(bytePayload)); 
    const jsonData = JSON.parse(jsonString); 
    const thingId = (jsonData.thingId ?? 'olive.decanters:decanter001').split(':');
    const value = {
        temperature: {
            properties: {
                value: jsonData.temperature ?? 0
            }
        },
        waterQuantity: {
            properties: {
                value: jsonData.waterQuantity ?? 0
            }
        }
    }; 
    return Ditto.buildDittoProtocolMsg(thingId[0], thingId[1], 'things', 'twin', 'commands', 'modify', '/features', headers, value);
}

function mapFromDittoProtocolMsg(namespace, id, group, channel, criterion, action, path, dittoHeaders, value, status, extra) {
    return null;
}