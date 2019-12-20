# -*- coding: UTF-8 -*-
from flask import Flask, jsonify, request
import traceback
import json

app = Flask('connectServer')

EndPointStock = dict()

@app.route("/")
def index():
    return "Please don't come here" , 200

@app.route("/endpoint/create/<nodeName>" , methods=["POST"])
def createNode(nodeName):
    '''
    resp:
        {
            "data": {
                    "created": {
                        "id": "nodeName"
                    }
            }
        }
    '''
    if nodeName in EndPointStock:
        return jsonify({"error":{"message":"Node name already exists"}}) , 200
    try:
        EndPointStock[nodeName] = request.json
    except:
        print(traceback.format_exc())
        return "ERRORS" , 200
    return jsonify({"data":{"created":{"id":nodeName}}}) , 200

@app.route("/endpoint/call/<nodeName>" , methods=["GET"])
def callNode(nodeName):
    '''
    resp:
        {
            "data": {
                "nodeContent": {dict....} ,
                "id": "nodeName"
            }
        }
    '''
    if nodeName not in EndPointStock:
        return jsonify({"error":{"message":"Node name does not exist"}}) , 200
    res = EndPointStock[nodeName]
    return jsonify({"data":{"nodeContent":res,"id":nodeName}})

def run():
    app.run(host='127.0.0.1', debug=True, port=21099, use_reloader=False)

if __name__=='__main__':
    run()
