*** Keywords ***
Login Telegram By Phone Number
    [Documentation]    Login Telegram by phone number, default for Taiwan(+886) phone
    [Arguments]    ${phone}
    Input Phone Data    ${phone}
    Sleep    1s
    Submit And Confirm Phone Data    

Input Phone Data
    [Documentation]    Input phone data, default for Taiwan(+886) phone
    [Arguments]    ${phone}    ${phoneCountry}=+886
    Wait Until Element Is Visible    //input[@name="phone_country"]
    Wait Until Element Is Visible    //input[@name="phone_number"]
    Input Text    //input[@name="phone_country"]    ${phoneCountry}    clear=${true}
    Input Text    //input[@name="phone_number"]    ${phone}

Submit And Confirm Phone Data
    [Documentation]    Submit and confirm phone data
    Wait Until Element Is Visible    //a[@class="login_head_submit_btn"]
    Click Element    //a[@class="login_head_submit_btn"]
    Wait Until Element Is Visible    //div[@class="confirm_modal_wrap md_simple_modal_wrap"]/div[@class="md_simple_modal_footer"]/button/span[@my-i18n="modal_ok"]
    Click Element    //div[@class="confirm_modal_wrap md_simple_modal_wrap"]/div[@class="md_simple_modal_footer"]/button/span[@my-i18n="modal_ok"]

Wait Until Verify Code Is Got And Input
    [Documentation]    Wait until verify code is got, and return this verify code
    [Arguments]    ${authorId}    ${timeout}=600s
    Wait Until Element Is Visible    //input[@name="phone_code"]
    ${verifyCode} =    Wait Until Keyword Succeeds    ${timeout}    5s    Try To Get Verify Code With Data    ${authorId}
    Input Text    //input[@name="phone_code"]    ${verifyCode}

Try To Get Verify Code With Data
    [Documentation]    Try to get verify code with data, keyword will fail when no data
    [Arguments]    ${authorId}
    ${verifyCode} =    Get Verify Code Via Telegram API    ${authorId}
    Should Not Be Equal As Strings    ${verifyCode}    ${EMPTY}
    [Return]    ${verifyCode}

Start Listen Telegram Contact Status
    [Documentation]    Start listen telegram contact status, will call API to update status in every loop
    [Arguments]    ${authorId}    ${loopTime}=60s
    FOR    ${times}    IN RANGE    3600
        Sleep    ${loopTime}
        ${total} =    Get Total Active Count On Contact Sidebar
        Update Contact Status Via Telegram API    ${authorId}    ${total}
    END

Get Total Active Count On Contact Sidebar
    [Documentation]    Get total active count on contact sidebar
    ${total} =    Set Variable    ${0}
    @{elements} =    Get WebElements    //span[contains(@class, "im_dialog_badge badge")]
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
