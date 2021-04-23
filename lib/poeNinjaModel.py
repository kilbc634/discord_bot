import requests
import json

def pickUp_ClusterJewel(apiUrl):
    resp = requests.get(apiUrl)
    characterData = resp.json()

    pickUpDatas = list()
    for jewelData in characterData['jewels']:
        if 'Cluster Jewel' in jewelData['itemData']['typeLine']:
            # get Jewel Type
            jewelType = jewelData['itemData']['typeLine']
            for mod in jewelData['itemData']['enchantMods']:
                if 'Added Small Passive Skills grant:' in mod:
                    # get Enchant Mod
                    enchantMod = mod
            passiveSkillMods = list()
            for mod in jewelData['itemData']['explicitMods']:
                if '1 Added Passive Skill is' in mod:
                    # get Passive Skill Mods
                    passiveSkillMods.append(mod)
            jewelData = {
                'jewelType': jewelType,
                'enchantMod': enchantMod,
                'passiveSkillMods': passiveSkillMods
            }
            pickUpDatas.append(jewelData)

    #print(json.dumps(pickUpDatas, sort_keys=True, indent=4))
    return pickUpDatas
