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
    urlData = re.findall('https://poe.ninja/(.+)/builds/char/(.+)/(.+)\?', ninjaUrl)[0]
    pageName = urlData[0]
    playerAccount = urlData[1]
    playerName = urlData[2]

    resp = requests.get(ninjaUrl)
    docText = resp.text

    buildLeaguesText = re.findall('window\.buildLeagues[\s]*=[\s]*(\[.+\]);', docText)[0]
    buildLeagues = json.loads(buildLeaguesText)
    for obj in buildLeagues:
        if obj['url'] == pageName:
            leagueName = obj['name']
    
    snapshotVersionsText = re.findall('window\.snapshotVersions[\s]*=[\s]*(\[.+\]);', docText)[0]
    snapshotVersions = json.loads(snapshotVersionsText)
    for obj in snapshotVersions:
        if obj['url'] == pageName and obj['type'] == 'exp' and obj['name'] == leagueName:
            versionText = obj['version']

    apiUrl = 'https://poe.ninja/api/data/{version}/GetCharacter?account={account}&name={name}&overview={league}&type=exp&language=en'.format(version=versionText, account=playerAccount, name=playerName, league=leagueName.lower())

    return apiUrl
