# -*- coding: UTF-8 -*-
import subprocess
import os
import time
import requests

def exeFunction(functionType, functionArg=None, attachments=list()):
    if functionType == '開車':
        # create server endpoint
        nodeName = str(int(time.time()))
        endpointData = dict()
        endpointData['message'] = functionArg
        if len(attachments) > 0:
            endpointData['image'] = attachments[0].url
        else:
            endpointData['image'] = ''
        res = requests.post('http://127.0.0.1:21099/endpoint/create/{nodeName}'.format(**locals()), json=endpointData)

        # run robot to send post
        myDir = os.getcwd()
        subprocess.call('robot -d {myDir}/report -v callNode:"{nodeName}" lib/upload_to_FB.robot'.format(**locals()))
