*** Keywords ***
Login FB For Normal Interface
    [Documentation]    Login FB for normal interface (blue face)
    Wait Until Element Is Visible    //input[@data-testid="royal_email"]
    Input Text    //input[@data-testid="royal_email"]    ${MY_ACCOUNT}
    Input Text    //input[@data-testid="royal_pass"]    ${MY_PASSWORD}
    Click Element    //button[@data-testid="royal_login_button"]

Login FB For Another Interface
    [Documentation]    Login FB for another interface (white face)
    Wait Until Element Is Visible    //input[@name="email"]/parent::div
    Input Text    //input[@name="email"]    ${MY_ACCOUNT}
    Input Text    //input[@name="pass"]    ${MY_PASSWORD}
    Click Element    //button[@name="login"]

Login FB
    [Documentation]    Login facebook by bot account
    ${status} =    Run Keyword And Return Status    Wait Until Page Contains Element    //input[@data-testid="royal_email"]    5s
    Run Keyword If    '${status}' == 'True'    Login FB For Normal Interface
    ...    ELSE    Login FB For Another Interface
    Verify Login Account Is Correct    ${FB_NAME}

Go To Specific Group By Left Nav
    [Documentation]    Click left navigation list to go to specific group
    [Arguments]    ${groupName}
    Wait Until Element Is Visible    //span[@class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7"][text()="${groupName}"]
    Wait Until Keyword Succeeds    3s    0.5s    Click Element    //span[@class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7"][text()="${groupName}"]
    Verify Group Page Header Name Is Correct    ${groupName}

Verify Group Page Header Name Is Correct
    [Documentation]    Verify group page header name is correct
    [Arguments]    ${groupName}
    Wait Until Element Is Visible    //span[@class="oi732d6d ik7dh3pa d2edcug0 hpfvmrgz qv66sw1b c1et5uql a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d3f4x2em fe6kdd0r mau55g9w c8b282yb h6olsfn3 m6dqt4wy h7mekvxk hnhda86s oo9gr5id hzawbc8m"][text()="${groupName}"]

Verify Login Account Is Correct
    [Documentation]    Verify login account is correct
    [Arguments]    ${accountName}
    Wait Until Element Is Visible    //span[@class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7"][text()="${accountName}"]

Active Post Area
    [Documentation]    Click post area to stay ready post stance
    Wait Until Element Is Visible    //div[@class="oajrlxb2 b3i9ofy5 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 j83agx80 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x cxgpxx05 d1544ag0 sj5x9vvc tw6a2znq i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh p8dawk7l bp9cbjyn orhb3f3m czkt41v7 fmqxjp7s emzo65vh btwxx1t3 buofh1pr idiwt2bm jifvfom9 ni8dbmo4 stjgntxs kbf60n1y"][@role="button"]
    Click Element    //div[@class="oajrlxb2 b3i9ofy5 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 j83agx80 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x cxgpxx05 d1544ag0 sj5x9vvc tw6a2znq i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh p8dawk7l bp9cbjyn orhb3f3m czkt41v7 fmqxjp7s emzo65vh btwxx1t3 buofh1pr idiwt2bm jifvfom9 ni8dbmo4 stjgntxs kbf60n1y"][@role="button"]

Typeing Message On Post Area
    [Documentation]    Typeing message on post area
    [Arguments]    ${content}
    Wait Until Element Is Visible    //div[@class="j83agx80 cbu4d94t lzcic4wl ni8dbmo4 stjgntxs oqq733wu l9j0dhe7 du4w35lb cwj9ozl2 ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi nwpbqux9"][@role="dialog"]//div[@class="notranslate _5rpu"][@role="textbox"]
    Click Element    //div[@class="j83agx80 cbu4d94t lzcic4wl ni8dbmo4 stjgntxs oqq733wu l9j0dhe7 du4w35lb cwj9ozl2 ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi nwpbqux9"][@role="dialog"]//div[@class="notranslate _5rpu"][@role="textbox"]
    Press Keys    ${None}    ${content}

Upload Image To Post Area
    [Documentation]    Upload image to post area
    [Arguments]    ${attachments}
    Wait Until Element Is Visible    //i[@class="hu5pjgll bixrwtb6 sp_XRoMnlkJWss sx_63c3b4"]
    Click Element    //i[@class="hu5pjgll bixrwtb6 sp_XRoMnlkJWss sx_63c3b4"]
    Wait Until Page Contains Element    //div[@class="n99xedck ecm0bbzt e5nlhep0"]/input[contains(@accept, image/*)]
    Choose File    //div[@class="n99xedck ecm0bbzt e5nlhep0"]/input[contains(@accept, image/*)]    ${attachments[0]}
    Wait Until Element Is Visible    //div[@class="j83agx80 cbu4d94t lzcic4wl ni8dbmo4 stjgntxs oqq733wu l9j0dhe7 du4w35lb cwj9ozl2 ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi nwpbqux9"][@role="dialog"]//i[@class="hu5pjgll m6k467ps sp_6vYwcjvw5IC sx_971d14"]
    Click Element    //div[@class="j83agx80 cbu4d94t lzcic4wl ni8dbmo4 stjgntxs oqq733wu l9j0dhe7 du4w35lb cwj9ozl2 ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi nwpbqux9"][@role="dialog"]//i[@class="hu5pjgll m6k467ps sp_6vYwcjvw5IC sx_971d14"]

Click Send Post Button
    [Documentation]    Click send post button
    Wait Until Element Is Visible    //div[@class="j83agx80 cbu4d94t lzcic4wl ni8dbmo4 stjgntxs oqq733wu l9j0dhe7 du4w35lb cwj9ozl2 ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi nwpbqux9"][@role="dialog"]//div[@class="oajrlxb2 s1i5eluu gcieejh5 bn081pho humdl8nn izx4hr6d rq0escxv nhd2j8a9 j83agx80 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys d1544ag0 qt6c0cv9 tw6a2znq i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh p8dawk7l beltcj47 p86d2i9g aot14ch1 kzx2olss cbu4d94t taijpn5t ni8dbmo4 stjgntxs k4urcfbm tv7at329"][@role="button"]
    Click Element    //div[@class="j83agx80 cbu4d94t lzcic4wl ni8dbmo4 stjgntxs oqq733wu l9j0dhe7 du4w35lb cwj9ozl2 ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi nwpbqux9"][@role="dialog"]//div[@class="oajrlxb2 s1i5eluu gcieejh5 bn081pho humdl8nn izx4hr6d rq0escxv nhd2j8a9 j83agx80 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys d1544ag0 qt6c0cv9 tw6a2znq i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh p8dawk7l beltcj47 p86d2i9g aot14ch1 kzx2olss cbu4d94t taijpn5t ni8dbmo4 stjgntxs k4urcfbm tv7at329"][@role="button"]
    Wait Until Page Does Not Contain Element    //div[@class="j83agx80 cbu4d94t lzcic4wl ni8dbmo4 stjgntxs oqq733wu l9j0dhe7 du4w35lb cwj9ozl2 ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi nwpbqux9"][@role="dialog"]

Get Data Via Endpoint API
    [Documentation]    Use call node to get data via endpoint api
    [Arguments]    ${nodeName}
    ${resp} =    Get Request    connectServer    /endpoint/call/${nodeName}
    Dictionary Should Contain Key    ${resp.json()}    data
    [Return]    ${resp.json()}
