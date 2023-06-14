from flask import Flask, jsonify, request
import json

app = Flask(__name__)
app.url_map.strict_slashes = False
VERIFY_TOKEN = 'mvp-bot'

def send_msg(msg,number):
    url = f"https://graph.facebook.com/v17.0/{number}/messages/"

    payload = json.dumps({
    "messaging_product": "whatsapp",
    "to": number,
    "type": "text",
    "text":msg
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer EAAJoLQ0uknEBACZCwDkE7ifkF5Mv7YuEa1aKJpNbDmRxuqCKYY951wprXJLfzkmRxXc2VgX83G88unWXg8SY82DLavDTp64SITqvcEX0Q7rg9HaVTaBts57dTZAysoZCTADErwOcpms6KYVNriwZCi67CpW5LcdoyIeFsGS1rzZBqwFDP7mJoG7JEB1z1fMl26ZBBtk9rG5mDZC9e18SRsL'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return None

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
            data['type'] = change["field"]
            data['number'] = change["value"]["metadata"]["display_phone_number"]
            data['name'] = change["value"]['contacts'][0]['profile']['name']
            data['msg'] = change["value"]['messages'][0]['text']['body']

    if data['msg'] not in ['1','2']:
        msg_response = f'''Olá {data['name']}, seja bem vindo ao bookBot
digite 1 para teste 1, digite 2 para teste 2 :)'''
        
    if data['msg'] == '1':
        msg_response = '''Esse é o teste 1:
░░░░░█░░░░░
░░░░██░░░░░
░░░░░█░░░░░
░░░░███░░░░
'''

    if data['msg'] == '2':
        msg_response = '''Esse é o teste 2:
                  
       .-''-.     
     .' .-.  )    
    / .'  / /     
   (_/   / /      
        / /       
       / /        
      . '         
     / /    _.-') 
   .' '  _.'.-''  
  /  /.-'_.'      
 /    _.'         
( _.-'            
'''
                 
    # Do anything with the response
    send_msg(msg_response,data['number'])

    return jsonify({"status": "success"}, 200)

if __name__ == '__main__': 
    app.run(debug=True)