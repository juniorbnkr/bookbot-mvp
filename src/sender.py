from flask import Flask, jsonify, request
import json,requests,os,httpx

app = Flask(__name__)
app.url_map.strict_slashes = False
VERIFY_TOKEN = 'mvp-bot'
perm_token = os.getenv('perm_token')


def send_msg(msg,number):
    url = "https://graph.facebook.com/v17.0/116826464720753/messages/"
    print(perm_token)

    payload = json.dumps({
    "messaging_product": "whatsapp",
    "to": number,
    "type": "text",
    "text": {
        "preview_url": False,
        "body": msg} 
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+perm_token
    
    }
    print(payload)

    response = requests.request("POST", url, headers=headers, data=payload)
    # response = httpx.post(url, data=payload, headers=headers)

    print(response.text)
    return response


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_sender_whatsapp():
    """__summary__: Get message from the webhook"""
    if request.method == "POST":
        print(request.get_json())
        response = send_msg(request.get_json()['msg'],str(request.get_json()['to']))
        return jsonify({"status": "success","data":request.get_json(),"response":response.text}, 200)
    else:
        return jsonify({"status": "USE POST, NOT GET"}, 403)
    

if __name__ == '__main__': 
    app.run(debug=True)