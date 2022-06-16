*** Keywords ***
Click Button For Login By Phone Number
    [Documentation]    Click button for login by phone number
    Wait Until Page Contains Element    //div[@class="auth-form qr"]//*[@class="qr-loading"]//*[@class="Loading"]
    Wait Until Page Does Not Contain Element    //div[@class="auth-form qr"]//*[@class="qr-loading"]//*[@class="Loading"]
    Wait Until Element Is Visible    //div[@class="auth-form qr"]/button
    Click Element    //div[@class="auth-form qr"]/button

Login Telegram By Phone Number
    [Documentation]    Login Telegram by phone number, default for Taiwan(+886) phone
    [Arguments]    ${phone}
    Input Phone Data    ${phone}
    Sleep    1s
    Submit To Next

Input Phone Data
    [Documentation]    Input phone data, default for Taiwan(+886) phone
    [Arguments]    ${phone}    ${phoneCountry}=+886
    Wait Until Element Is Visible    //input[@id="sign-in-phone-number"]
    Input Text    //input[@id="sign-in-phone-number"]    ${phoneCountry}${phone}    clear=${true}

Submit To Next
    [Documentation]    Submit to next
    Wait Until Element Is Visible    //button[@type="submit"]/div
    Click Element    //button[@type="submit"]/div

Wait Until Verify Code Is Got And Input
    [Documentation]    Wait until verify code is got, and return this verify code
    [Arguments]    ${authorId}    ${timeout}=600s
    Wait Until Element Is Visible    //input[@id="sign-in-code"]
    ${verifyCode} =    Wait Until Keyword Succeeds    ${timeout}    5s    Try To Get Verify Code With Data    ${authorId}
    Input Text    //input[@id="sign-in-code"]    ${verifyCode}

Try To Get Verify Code With Data
    [Documentation]    Try to get verify code with data, keyword will fail when no data
    [Arguments]    ${authorId}
    ${verifyCode} =    Get Verify Code Via Telegram API    ${authorId}
    Should Not Be Equal As Strings    ${verifyCode}    ${EMPTY}
    [Return]    ${verifyCode}

Start Listen Telegram Contact Status
    [Documentation]    Start listen telegram contact status, will call API to update status in every loop
    [Arguments]    ${authorId}    ${loopTime}=60s
    FOR    ${times}    IN RANGE    6000
        ${total} =    Get Total Active Count On Contact Sidebar
        Update Contact Status Via Telegram API    ${authorId}    ${total}
        Sleep    ${loopTime}
    END

Get Total Active Count On Contact Sidebar
    [Documentation]    Get total active count on contact sidebar
    ${total} =    Set Variable    ${0}
    @{elements} =    Get WebElements    //div[@class="ListItem-button"]/div[@class="info"]/div[@class="title"]/h3[text()!="A.G.M.P. Information"][text()!="AGMP-版本通知"]/parent::*/parent::*/div[@class="subtitle"]//div[@class="Badge unread"]
    FOR    ${element}    IN    @{elements}
        ${count} =    Get Element Attribute    ${element}    textContent
        ${total} =    Evaluate    ${total} + ${count}
    END
    [Return]    ${total}

Get Verify Code Via Telegram API
    [Documentation]    Get verify code via telegram API
    [Arguments]    ${authorId}
    ${resp} =    Get Request    telegramAPI    /${authorId}/verify
    Dictionary Should Contain Key    ${resp.json()}    verifyCode
    [Return]    ${resp.json()['verifyCode']}

Get Phone Number Via Telegram API
    [Documentation]    Get phone number via telegram API
    [Arguments]    ${authorId}
    ${resp} =    Get Request    telegramAPI    /${authorId}
    Dictionary Should Contain Key    ${resp.json()}    data
    [Return]    ${resp.json()['data']['phoneNumber']}

Update Contact Status Via Telegram API
    [Documentation]    Update contact status via telegram API, trigger test failed when response without contactCount
    [Arguments]    ${authorId}    ${contactCount}
    &{headers} =    Create Dictionary    Content-Type=application/json
    &{data} =    Create Dictionary    contactCount=${contactCount}
    ${resp} =    Post Request    telegramAPI    /${authorId}/contact    json=${data}    headers=${headers}
    Dictionary Should Contain Key    ${resp.json()}    contactCount

Delete Bind Data Via Telegram API
    [Documentation]    Delete bind data via telegram API
    [Arguments]    ${authorId}
    ${resp} =    Delete Request    telegramAPI    /${authorId}
