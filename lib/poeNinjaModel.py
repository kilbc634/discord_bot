import requests
import json
import re

def pickUp_ClusterJewel(apiUrl):
    resp = requests.get(apiUrl)
    characterData = resp.json()

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
    urlData = re.findall('https://poe.ninja/(.+)/builds/char/(.+)/(.+)\?', ninjaUrl)[0]
    pageName = urlData[0]
    playerAccount = urlData[1]
    playerName = urlData[2]

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

    return apiUrl
