from flask import Flask, jsonify, request

app = Flask(__name__)
app.url_map.strict_slashes = False
VERIFY_TOKEN = 'mvp-bot'

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
            data['name'] = change["value"]['contacts']['profile']['name']
            data['msg'] = change["value"]['messages']['text']['body']

    if data['msg'] not in ['1','2']:
        print(f'''Olá{data['name']}, seja bem vindo ao bookBot \n
                digite 1 para teste 1, digite 2 para teste 2 :)''')
                 
    # Do anything with the response
    # Sending a message to a phone number to confirm the webhook is working

    return jsonify({"status": "success"}, 200)

if __name__ == '__main__': 
    app.run(debug=True)