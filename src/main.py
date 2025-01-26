from flask import Flask, jsonify, request
import json,requests,os,time,datetime
import pandas as pd
import messages
from event import Event
from messages import Messages

VERIFY_TOKEN = 'mvp-bot'
app = Flask(__name__)
app.url_map.strict_slashes = False
       
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():

    if request.method == "GET":
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Authentication failed. Invalid Token."

    response = request.get_json()
    print(response)
    event = Event(response)
    event.save_event()
    print(event.type)

    if event.type == 'read' or event.type == 'delivered':
        number = response['entry'][0]['changes'][0]["value"]["statuses"][0]["recipient_id"]
        message = Messages(number,None,None)
        if event.type == 'delivered':
            time.sleep(5)
        message.unblock()
        message.dbConnection.close()

    if event.type == 'receive':
        ## START MSG
        if 'messages' in response['entry'][0]['changes'][0]['value']:
            if 'text' in response['entry'][0]['changes'][0]['value']['messages'][0]:
                for entry in response["entry"]:
                    for change in entry["changes"]:
                        if 'contacts' in change["value"]:
                            type = change["field"]
                            number = change["value"]["contacts"][0]["wa_id"]
                            name = change["value"]['contacts'][0]['profile']['name']
                            msg = change["value"]['messages'][0]['text']['body']
                            wamid = change["value"]['messages'][0]['id']

        ## END MSG

        ## START TEMPLATE
        if 'messages' in response['entry'][0]['changes'][0]['value']:
            if 'button' in response['entry'][0]['changes'][0]['value']['messages'][0]:
                number = response['entry'][0]['changes'][0]["value"]["contacts"][0]["wa_id"]
                name = response['entry'][0]['changes'][0]["value"]['contacts'][0]['profile']['name']            
                msg = response['entry'][0]['changes'][0]['value']['messages'][0]['button']['text']
        ## END TEMPLATE

        message = Messages(number,name,msg, wamid)
        
        if not message.check_block() and not message.check_repeat_msg():
            print('not blocked')
            message.send_msg()
            print('template',message.template)
            print('msg = ',message.msg_to_send)
            if message.template != '':
                message.send_template()
        
        message.dbConnection.close()

    return jsonify({"status": "success"}, 200)

if __name__ == '__main__': 
    app.run(debug=True)
