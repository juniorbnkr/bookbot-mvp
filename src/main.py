from flask import Flask, jsonify, request
import json,requests,os,time,datetime
import pandas as pd
import messages


VERIFY_TOKEN = 'mvp-bot'
app = Flask(__name__)
app.url_map.strict_slashes = False
       
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    """__summary__: Get message from the webhook"""
    if request.method == "GET":
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Authentication failed. Invalid Token."

    response = request.get_json()
    print(response)
    messages.save_event(response)
    
    return jsonify({"status": "success"}, 200)
    data = {}
    
    ## START MSG
    if 'messages' in response['entry'][0]['changes'][0]['value']:
        if 'text' in response['entry'][0]['changes'][0]['value']['messages'][0]:
            for entry in response["entry"]:
                for change in entry["changes"]:
                    if 'contacts' in change["value"]:
                        data['type'] = change["field"]
                        data['number'] = change["value"]["contacts"][0]["wa_id"]
                        data['name'] = change["value"]['contacts'][0]['profile']['name']
                        data['msg'] = change["value"]['messages'][0]['text']['body']
            
            if 'number' in data:
                last_msg = messages.get_last_msg(data['number'])
                next_msg = messages.next_msg(data['number'],data['name'],data['msg'])
            return jsonify({"status": "success"}, 200)
    ## END MSG

    ## START TEMPLATE
    if 'messages' in response['entry'][0]['changes'][0]['value']:
        if 'button' in response['entry'][0]['changes'][0]['value']['messages'][0]:
            number = response['entry'][0]['changes'][0]["value"]["contacts"][0]["wa_id"]
            name = response['entry'][0]['changes'][0]["value"]['contacts'][0]['profile']['name']            
            msg = response['entry'][0]['changes'][0]['value']['messages'][0]['button']['text']
            msg_response = messages.next_msg(number,name,msg)
    ## END TEMPLATE

    return jsonify({"status": "success"}, 200)

if __name__ == '__main__': 
    app.run(debug=True)
