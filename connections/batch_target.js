function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {
    return null;
}

function mapFromDittoProtocolMsg(namespace, id, group, channel, criterion, action, path, dittoHeaders, value, status, extra) {
    let payload = {
        thingId: namespace + ':' + id,
        oliveParameters: value.oliveParameters ? value.oliveParameters.properties : {},
        processParameters: value.processParameters ? value.processParameters.properties : {},
        oliveOilQuality: value.oliveOilQuality ? value.oliveOilQuality.properties : {}
    };
    
    let textPayload = JSON.stringify(payload);
    let bytePayload = null; 
    let contentType = 'application/json; charset=UTF-8'; 
    return Ditto.buildExternalMsg(dittoHeaders, textPayload, bytePayload, contentType);
}
