function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {
    return null;
}

function mapFromDittoProtocolMsg(namespace, id, group, channel, criterion, action, path, dittoHeaders, value, status, extra) {
    let textPayload = '{\"thingId\": \"' + namespace + ':' + id + '\", \"temperature\": ' + value.temperature.properties.value + ', \"humidity\": ' + value.humidity.properties.value + '}'; 
    let bytePayload = null; 
    let contentType = 'text/plain; charset=UTF-8'; 
    return Ditto.buildExternalMsg(dittoHeaders, textPayload, bytePayload, contentType);
}