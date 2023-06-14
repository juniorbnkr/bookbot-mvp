from flask import Flask, jsonify, request
import json,requests,os,httpx

app = Flask(__name__)
app.url_map.strict_slashes = False
VERIFY_TOKEN = 'mvp-bot'
perm_token = os.getenv('perm_token')

def send_msg(msg,number):
   url = "http://104.198.41.165:5000/webhook"
   payload = json.dumps({
        "msg": msg,
        "to": str(number)
    })
   headers = {
    'Content-Type': 'application/json'
    }
   response = requests.request("POST", url, headers=headers, data=payload)
   return response.text

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
    
    data = {}
    for entry in response["entry"]:
        for change in entry["changes"]:
            if 'contacts' in change["value"]:
                data['type'] = change["field"]
                data['number'] = change["value"]["contacts"][0]["wa_id"]
                data['name'] = change["value"]['contacts'][0]['profile']['name']
                data['msg'] = change["value"]['messages'][0]['text']['body']
    
    if 'number' in data:
        if data['msg'] not in ['1','2']:
            msg_response = f"Olá {data['name']}, seja bem vindo ao bookBot \ndigite 1 para teste 1, digite 2 para teste 2 "
            
        if data['msg'] == '1':
            msg_response = " teste 1  |o|"

        if data['msg'] == '2':
            msg_response = "teste 2 =D "
        # Do anything with the response
        print(msg_response)
        print(str( data['number']))
        send_msg(msg_response,str( data['number']))

    return jsonify({"status": "success"}, 200)

if __name__ == '__main__': 
    app.run(debug=True)

    [{'id': '118314817903665', 'changes':
       [{'value': {'messaging_product': 'whatsapp', 'metadata':
                    {'display_phone_number': '5511997274105', 'phone_number_id': '116826464720753'}, 
                    'statuses': 
                    [{'id': 'wamid.HBgNNTUxMTk3MDk3NTUyORUCABEYEkIyRjA4NDlGRkVDRkIyQjNFMAA=',
                       'status': 'delivered', 'timestamp': '1686760037', 'recipient_id': '5511970975529', 'conversation':
                         {'id': '336b569ea96fe1f647e038fde911997b', 'origin': {'type': 'service'}}, 'pricing':
                           {'billable': True, 'pricing_model': 'CBP', 'category': 'service'}}]}, 
                                            'field': 'messages'}]}]