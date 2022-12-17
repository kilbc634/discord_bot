import requests
import json
import re
from urllib.parse import urlparse, parse_qs

def pickUp_ClusterJewel(apiUrl):
    print('[INFO] Getting URL {apiUrl}'.format(**locals()))
    resp = requests.get(apiUrl)
    print('[INFO] Done')
    print(resp)
    characterData = resp.json()
    print(characterData)

    pickUpDatas = list()
    for jewelData in characterData['jewels']:
        if 'Cluster Jewel' in jewelData['itemData']['typeLine']:
            # get Jewel Type
            jewelType = jewelData['itemData']['typeLine']
            # get Enchant Mod. If item match unique rule, will set the special Enchant Mod
            if jewelData['itemData']['name'] == 'Megalomaniac':
                enchantMod = 'Unique Jewel: {}'.format('Megalomaniac'.upper())
            else:
                for mod in jewelData['itemData']['enchantMods']:
                    if 'Added Small Passive Skills grant:' in mod:
                        # get Enchant Mod
                        enchantMod = mod
            passiveSkillMods = list()
            for mod in jewelData['itemData']['explicitMods']:
                if '1 Added Passive Skill is' in mod:
                    # get Passive Skill Mods
                    passiveSkillMods.append(mod)
            jewelDataOutput = {
                'jewelType': jewelType,
                'enchantMod': enchantMod,
                'passiveSkillMods': passiveSkillMods
            }
            pickUpDatas.append(jewelDataOutput)

    return pickUpDatas

def get_apiUrl_from_ninjaUrl(ninjaUrl):
    # parser url data
    parseResult = urlparse(ninjaUrl)
    print('[INFO] Parser url object:')
    print(parseResult)
    urlData = re.findall('/(.+)/builds/char/(.+)/(.+)', parseResult.path)[0]
    pageName = urlData[0]
    playerAccount = urlData[1]
    playerName = urlData[2]
    print('[INFO] Parser pageName={pageName} playerAccount={playerAccount} playerName={playerName} From {urlData}'.format(**locals()))
    # with time-machine
    queryData = parse_qs(parseResult.query)
    timeMachine = ''
    if 'time-machine' in queryData:
        timeMachine = queryData['time-machine'][0]
        print('[INFO] Parser timeMachine={timeMachine} From {queryData}'.format(**locals()))

    # get indexState to complate Character api URL
    indexStateUrl = 'https://poe.ninja/api/data/getindexstate?'
    resp = requests.get(indexStateUrl)
    indexStateData = resp.json()

    # buildLeague from indexState
    for obj in indexStateData['buildLeagues']:
        if obj['url'] == pageName:
            buildLeague = obj['name']
    # snapshotVersion and snapshotName from indexState
    for obj in indexStateData['snapshotVersions']:
        if obj['url'] == pageName and obj['type'] == 'exp' and obj['name'] == buildLeague:
            snapshotVersion = obj['version']
            snapshotName = obj['snapshotName']

    # complate Character api URL
    apiUrl = 'https://poe.ninja/api/data/{version}/GetCharacter?account={account}&name={name}&overview={overview}&type=exp&language=en'.format(version=snapshotVersion, account=playerAccount, name=playerName, overview=snapshotName)
    print('[INFO] Create URL {apiUrl}'.format(**locals()))
    if timeMachine:
        apiUrl = apiUrl + '&timeMachine={}'.format(timeMachine)
        print('[INFO] Add timeMachine={timeMachine} For URL'.format(**locals()))

    return apiUrl
