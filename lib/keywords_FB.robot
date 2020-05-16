*** Keywords ***
Login FB For Normal Interface
    [Documentation]    Login FB for normal interface (blue face)
    Wait Until Element Is Visible    //input[@data-testid="royal_email"]
    Input Text    //input[@data-testid="royal_email"]    ${MY_ACCOUNT}
    Input Text    //input[@data-testid="royal_pass"]    ${MY_PASSWORD}
    Click Element    //input[@data-testid="royal_login_button"]

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
    Wait Until Element Is Visible    //a[@data-testid="left_nav_item_${FB_NAME}"]

Go To Specific Group By Left Nav
    [Documentation]    Click left navigation list to go to specific group
    [Arguments]    ${groupName}    ${groupHeaderLink}=${None}
    Wait Until Element Is Visible    //a[@data-testid="left_nav_item_${groupName}"]
    Wait Until Keyword Succeeds    3s    0.5s    Click Element    //a[@data-testid="left_nav_item_${groupName}"]
    Run Keyword If    '${groupHeaderLink}' != '${None}'    Verify Group Page Header Link    ${groupHeaderLink}

Verify Group Page Header Link
    [Documentation]    Verify or wait page stay on specific group
    [Arguments]    ${groupHeaderLink}
    Wait Until Element Is Visible    //div[@data-testid="group_sidebar_nav"]/div/h1/a[@href="${groupHeaderLink}"]

Active Post Area
    [Documentation]    Active post area to stay ready post stance
    ${status} =    Run Keyword And Return Status    Wait Until Page Contains Element    //table[@class="_4ukb _2j7c uiGrid _51mz"]    2.5s
    Run Keyword If    '${status}' == 'False'    Click Post Area
    Wait Until Page Contains Element    //table[@class="_4ukb _2j7c uiGrid _51mz"]
    Wait Until Element Is Visible    //div[@spellcheck="true"]
    Click Element    //div[@spellcheck="true"]

Click Post Area
    [Documentation]    Click post area
    ${firstPath} =    Set Variable    //textarea[@name="xhpc_message_text"]
    ${secondPath} =    Set Variable    //div[@aria-describedby="placeholder-41rom"]
    ${status} =    Run Keyword And Return Status    Wait Until Page Contains Element    ${firstPath}    10s
    Run Keyword If    '${status}' == 'True'    Click Element    ${firstPath}
    ...    ELSE    Click Element    ${secondPath}

Typeing Message On Post Area
    [Documentation]    Typeing message on post area
    [Arguments]    ${content}
    Active Post Area
    Press Keys    ${None}    ${content}

Upload Image To Post Area
    [Documentation]    Upload image to post area
    [Arguments]    ${attachments}
    Active Post Area
    ${firstPath} =    Set Variable    //li[contains(@class , "fbReactComposerAttachmentSelector_MEDIA")]//input
    ${secondPath} =    Set Variable    //td[contains(@class , "fbReactComposerAttachmentSelector_MEDIA")]//input
    ${status} =    Run Keyword And Return Status    Page Should Contain Element    ${firstPath}
    Run Keyword If    '${status}' == 'True'    Choose File    ${firstPath}    ${attachments[0]}
    ...    ELSE    Choose File    ${secondPath}    ${attachments[0]}
    Wait Until Page Contains Element    //*[@aria-valuenow]
    Wait Until Page Does Not Contain Element    //*[@aria-valuenow]
    Wait Until Page Contains Element    //div[@class="fbScrollableArea"]//img[contains(@alt, "image_${callNode}.png")]/parent::div[@class="_jfc"]
    Wait Until Page Does Not Contain Element    //div[@class="fbScrollableArea"]//img[@alt="${attachments[0]}"]/parent::div[@class="_jfc_jfd"]
    Wait Until Page Does Not Contain Element    //div[@class="fbScrollableArea"]//img[@alt="${attachments[0]}"]/parent::div/div[@class="_jff"]

Click Send Post Button
    [Documentation]    Click send post button
    Wait Until Element Is Enabled    //span[text()="發佈"]/parent::button[@type="submit"]
    Click Element    //span[text()="發佈"]/parent::button[@type="submit"]
    Wait Until Page Does Not Contain Element    //span[text()="發佈"]/parent::button[@type="submit"]

Get Data Via Endpoint API
    [Documentation]    Use call node to get data via endpoint api
    [Arguments]    ${nodeName}
    ${resp} =    Get Request    connectServer    /endpoint/call/${nodeName}
    Dictionary Should Contain Key    ${resp.json()}    data
    [Return]    ${resp.json()}
