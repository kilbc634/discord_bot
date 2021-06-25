*** Settings ***
Library         SeleniumLibrary    30    10
Library         OperatingSystem
Library         RequestsLibrary
Library         Collections
Variables       ../setting.py
Resource        ./keywords_telegram.robot

Suite Setup    SuiteSetup
Suite Teardown    Close All Browsers

*** Test Cases ***
Listen Telegram By Discord Author Id
    [Tags]    listen_telegram_A
    [Timeout]    NONE
    Click Button For Login By Phone Number
    Login Telegram By Phone Number    ${phoneNumber}
    Wait Until Verify Code Is Got And Input    ${authorId}
    Wait Until Page Contains Element    //div[@class="ListItem-button"]/div[@class="info"]/div[@class="subtitle"]/p
    Start Listen Telegram Contact Status    ${authorId}
    [Teardown]    Delete Bind Data Via Telegram API    ${authorId}

*** Keywords ***
SuiteSetup
    ${workDir} =    Evaluate    os.getcwd()    os
    Set Suite Variable    ${WORKDIR}    ${workDir}
    ${options}=    Evaluate  sys.modules['selenium.webdriver.chrome.options'].Options()    sys
    Call Method     ${options}    add_argument    --no-sandbox
    Call Method     ${options}    add_argument    --headless
    Call Method     ${options}    add_argument    --disable-dev-shm-usage
    Call Method     ${options}    add_argument    --disable-notifications
    ${myOS} =    Evaluate    platform.system()    platform
    Run Keyword If    '${myOS}' == 'Windows'
    ...    Set Suite Variable    ${chromedriverPath}    ${WORKDIR}/lib/chromedriver_win.exe
    Run Keyword If    '${myOS}' == 'Linux'
    ...    Set Suite Variable    ${chromedriverPath}    ${WORKDIR}/lib/chromedriver_linux
    ${driver}=    Create Webdriver    Chrome    options=${options}    executable_path=${chromedriverPath}
    Go To    https://web.telegram.org/z/
    Set Window Size    1440    900
    Create Session    telegramAPI    http://127.0.0.1:21090/telegram
    ${phoneNumber} =    Get Phone Number Via Telegram API    ${authorId}
    Set Suite Variable    ${phoneNumber}
    Set Suite Variable    ${authorId}
