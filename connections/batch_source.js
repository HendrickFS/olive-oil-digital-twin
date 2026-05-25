function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {
    try {
        var jsonData = null;
        if (bytePayload && bytePayload.length) {
            try {
                var jsonString = String.fromCharCode.apply(null, new Uint8Array(bytePayload));
                jsonData = JSON.parse(jsonString);
            } catch (e) {}
        }
        if (!jsonData && textPayload) {
            try {
                jsonData = JSON.parse(textPayload);
            } catch (e) {}
        }
        if (!jsonData) {
            console.log('Mapper: payload is not JSON - textPayload=', textPayload);
            return null;
        }
        
        var thingId = (jsonData.thingId || '').split(':');
        if (thingId.length < 2) {
            console.log('Mapper: missing or invalid thingId', jsonData.thingId);
            return null;
        }
        var ns = thingId[0];
        var id = thingId[1];
        var messages = [];

        var mapping = [
            {key: 'maturationIndex', feature: 'oliveParameters', property: 'maturationIndex'},
            {key: 'moistureContent', feature: 'oliveParameters', property: 'moistureContent'},
            {key: 'oilContent', feature: 'oliveParameters', property: 'oilContent'},
            {key: 'defectIndex', feature: 'oliveParameters', property: 'defectIndex'},
            {key: 'cultivar', feature: 'oliveParameters', property: 'cultivar'},
            
            {key: 'malaxationTemperature', feature: 'processParameters', property: 'malaxationTemperature'},
            {key: 'malaxationTime', feature: 'processParameters', property: 'malaxationTime'},
            {key: 'waterFlowRate', feature: 'processParameters', property: 'waterFlowRate'},
            {key: 'waterToPasteRatio', feature: 'processParameters', property: 'waterToPasteRatio'},
            
            {key: 'yieldPercentage', feature: 'oliveOilQuality', property: 'yieldPercentage'},
            {key: 'totalPhenols', feature: 'oliveOilQuality', property: 'totalPhenols'},
            {key: 'freeAcidity', feature: 'oliveOilQuality', property: 'freeAcidity'},
            {key: 'peroxideValue', feature: 'oliveOilQuality', property: 'peroxideValue'},
            {key: 'k232', feature: 'oliveOilQuality', property: 'k232'},
            {key: 'k270', feature: 'oliveOilQuality', property: 'k270'},
            {key: 'deltaK', feature: 'oliveOilQuality', property: 'deltaK'},
            {key: 'sensoryFruity', feature: 'oliveOilQuality', property: 'sensoryProfile/fruity'},
            {key: 'sensoryBitter', feature: 'oliveOilQuality', property: 'sensoryProfile/bitter'},
            {key: 'sensoryPungent', feature: 'oliveOilQuality', property: 'sensoryProfile/pungent'},
            {key: 'isEvooCompliant', feature: 'oliveOilQuality', property: 'isEvooCompliant'}
        ];

        for (var i = 0; i < mapping.length; i++) {
            var m = mapping[i];
            if (Object.prototype.hasOwnProperty.call(jsonData, m.key)) {
                var featureValue = jsonData[m.key];
                messages.push(Ditto.buildDittoProtocolMsg(
                    ns, id, 'things', 'twin', 'commands', 'modify',
                    '/features/' + m.feature + '/properties/' + m.property,
                    headers, featureValue
                ));
            }
        }
        
        if (messages.length === 0) {
            return null;
        }
        return messages;
    } catch (ex) {
        console.log('Mapper exception:', ex);
        return null;
    }
}

function mapFromDittoProtocolMsg(namespace, id, group, channel, criterion, action, path, dittoHeaders, value, status, extra) {
    return null;
}
