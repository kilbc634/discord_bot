import requests
import json
from lxml import etree

ArchnemesisPageUrl = 'https://poedb.tw/us/Archnemesis_league'
ele_archnemesis_name_texts = '//div[@id="ModArea"]//table/tbody/tr/td[1]//a[@class="item_common"][text()]'
ele_archnemesis_area_texts_withRow = '//div[@id="ModArea"]//table/tbody/tr[{row}]/td[2]/a[text()]'

def autoPick_ArchnemesisArea(target):
    resp = requests.get(ArchnemesisPageUrl)
    doc = etree.HTML(resp.text)

    # list up all Archnemesis Data
    archnemesisData = dict()
    keyElements = doc.xpath(ele_archnemesis_name_texts)
    for index in range(len(keyElements)):
        archnemesisName = keyElements[index].text
        archnemesisMapList = list()
        for element in doc.xpath(ele_archnemesis_area_texts_withRow.format(row=index+1)):
            archnemesisMapList.append(element.text)
        archnemesisData[archnemesisName] = archnemesisMapList
    
    # count map ranking with Target String
    mapRanking = dict()
    for key in archnemesisData.keys():
        if target.lower().__contains__(key.lower()):
            for mapName in archnemesisData[key]:
                if mapName in mapRanking:
                    mapRanking[mapName] = mapRanking[mapName] + 1
                else:
                    mapRanking[mapName] = 1
    
    # pick up best maps
    sortList = sorted(mapRanking.items(), key=lambda v: v[1], reverse=True)
    return sortList

    
if __name__ == "__main__":
    autoPick_ArchnemesisArea('Malediction    Frenzied    Bloodletter    Overcharged    Malediction    Toxic    Bloodletter    Arcane Buffer')
