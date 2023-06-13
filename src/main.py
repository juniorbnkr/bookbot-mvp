from flask import Flask, jsonify, request

app = Flask(__name__)
VERIFY_TOKEN = 'mvp-bot'

def process_webhook_notification(self, data):
        """_summary_: Process webhook notification
        For the moment, this will return the type of notification
        """
        response = []

        for entry in data["entry"]:
            for change in entry["changes"]:
                response.append(
                    {
                        "type": change["field"],
                        "from": change["value"]["metadata"]["display_phone_number"],
                    }
                )
        # Do whatever with the response
        return response

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

    print (request.get_json())
    print (request)
    # response = process_webhook_notification(request.get_json())
    # print(response) 
    # Do anything with the response
    # Sending a message to a phone number to confirm the webhook is working

    return jsonify({"status": "success"}, 200)

if __name__ == '__main__': 
    app.run(debug=True)