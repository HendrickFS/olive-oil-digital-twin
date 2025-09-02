function mapToDittoProtocolMsg(headers, textPayload, bytePayload, contentType) {
    const jsonString = String.fromCharCode.apply(null, new Uint8Array(bytePayload));
    const jsonData = JSON.parse(jsonString);
    const thingId = (jsonData.thingId ?? 'olive.centrifuges:centrifuge001').split(':');

    const features = [
        { key: 'temperature', name: 'temperature' },
        { key: 'waterTemperature', name: 'waterTemperature' },
        { key: 'waterFatContent', name: 'waterFatContent' },
        { key: 'inputTemperature', name: 'inputTemperature' }
    ];

    const now = new Date().toISOString();

    const messages = features
        .filter(f => f.key in jsonData)
        .flatMap(f => {
            const featureValue = jsonData[f.key];
            return [
                Ditto.buildDittoProtocolMsg(
                    thingId[0],
                    thingId[1],
                    'things',
                    'twin',
                    'commands',
                    'modify',
                    `/features/${f.name}/properties/value`,
                    headers,
                    featureValue
                ),
                Ditto.buildDittoProtocolMsg(
                    thingId[0],
                    thingId[1],
                    'things',
                    'twin',
                    'commands',
                    'modify',
                    `/features/${f.name}/properties/timestamp`,
                    headers,
                    now
                )
            ];
        });
    return messages.length === 1 ? messages[0] : messages;
}


function mapFromDittoProtocolMsg(namespace, id, group, channel, criterion, action, path, dittoHeaders, value, status, extra) {
    return null;
}