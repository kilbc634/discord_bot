*** Settings ***
Library         SeleniumLibrary    15    10
Library         OperatingSystem
Library         RequestsLibrary
Library         Collections
Resource        ./keywords_FB.robot
Suite Setup    SuiteSetup
Suite Teardown    Close All Browsers

*** Variables ***
${MY_ACCOUNT}    k******34@gmail.com
${MY_PASSWORD}    *********
${FB_NAME}    七波 シロネ
${FB_GROUP}    暫時不知道做什麼用的社團
${FB_GROUP_LINK}    /groups/422981628065868/?ref=group_header

*** Test Cases ***
Upload to HU group by user acconut
    [Tags]    upload_to_FB_A
    Login FB
    Go To Specific Group By Left Nav    ${FB_GROUP}    ${FB_GROUP_LINK}
    Typeing Message On Post Area    ${postMessage}
    ${attachmentsLen} =    Get Length    ${postAttachments}
    Run Keyword If    ${attachmentsLen} > ${0}    Upload Image To Post Area    ${postAttachments}
    Click Send Post Button

*** Keywords ***
SuiteSetup
    ${workDir} =    Evaluate    os.getcwd()    os
    Set Suite Variable    ${WORKDIR}    ${workDir}
    ${options}=    Evaluate  sys.modules['selenium.webdriver.chrome.options'].Options()    sys
    Call Method     ${options}    add_argument    --disable-notifications
    ${myOS} =    Evaluate    platform.system()    platform
    Run Keyword If    '${myOS}' == 'Windows'
    ...    Set Suite Variable    ${chromedriverPath}    ${WORKDIR}/lib/chromedriver_win.exe
    Run Keyword If    '${myOS}' == 'Linux'
    ...    Set Suite Variable    ${chromedriverPath}    ${WORKDIR}/lib/chromedriver_linux
    #Call Method     ${options}    add_argument    --headless    # run chrome in background
    ${driver}=    Create Webdriver    Chrome    options=${options}    executable_path=${chromedriverPath}
    Go To     https://zh-tw.facebook.com/
    Create Session    connectServer    http://127.0.0.1:21099
    ${resp} =    Get Data Via Endpoint API    ${callNode}
    Set Suite Variable    ${postMessage}    ${resp['data']['nodeContent']['message']}
    ${len} =    Get Length    ${resp['data']['nodeContent']['image']}
    Run Keyword If    ${len} > ${0}    Download And Save Image To Local    ${resp['data']['nodeContent']['image']}
    ...    ELSE    Set Suite Variable    ${postAttachments}    ${None}

Download And Save Image To Local
    [Arguments]    ${url}
    Create Session    imageUrl    ${url}
    ${imageBin} =    Get Request    imageUrl    ${None}
    Create Binary File    ${WORKDIR}/res/image/image_${callNode}.png    ${imageBin.content}
    @{imageList} =    Create List    ${WORKDIR}/res/image/image_${callNode}.png
    Set Suite Variable    ${postAttachments}    ${imageList}
