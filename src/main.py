from flask import Flask, jsonify, request
import json,requests,os
from sqlalchemy import create_engine  
from sqlalchemy import text
import pandas as pd


app = Flask(__name__)
app.url_map.strict_slashes = False
VERIFY_TOKEN = 'mvp-bot'
perm_token = os.getenv('perm_token')
db_name = os.getenv('db_name')
db_user = os.getenv('db_user')
db_pass = os.getenv('db_pass')

def send_msg(msg,number):
    url = "https://graph.facebook.com/v17.0/116826464720753/messages/"
    print(perm_token)

    payload = json.dumps({
    "messaging_product": "whatsapp",
    "to": number,
    "type": "text",
    "template": {
        "name": "next"
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+perm_token

    }
    print(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    # response = httpx.post(url, data=payload, headers=headers)
    # print(response.text)
    return response

def send_template(template,number):
    pass


def get_last_msg(number):
    sqlEngine       = create_engine(f'mysql+pymysql://{db_user}:@{db_name}/bot_mvp?password={db_pass}', pool_recycle=3600)
    dbConnection    = sqlEngine.connect()
    df = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                     WHERE phone_number = {number} ORDER BY id DESC LIMIT 1;"),dbConnection)

    return df

def next_msg(last_msg,name):
    if last_msg.empty:
        msg_response = f"Olá {name}, seja bem vindo ao bookBot "
        return msg_response
    
    if last_msg['chap'].values[0] > 0:
        last_cap = last_msg['chap'].values[0]
        print(last_cap)
        sqlEngine       = create_engine(f'mysql+pymysql://{db_user}:@{db_name}/bot_mvp?password={db_pass}', pool_recycle=3600)
        dbConnection    = sqlEngine.connect()
        df = pd.read_sql(text(f"SELECT * FROM bot_mvp.memoriasBras ml \
                     WHERE cap = {last_cap + 1} ORDER BY line asc;"),dbConnection)
        
        msg = ''
        for index, row in df.iterrows():
            msg += row['content'] + '\n'
        return msg
            
    if last_msg['chap'].values[0] == 0:

        return 

# def update_log(number):
#     df = pd.DataFrame({'c1': , 'c2': [100, 110, 120]})
#     pd.to_sql(df, 'bot_mvp', dbConnection, if_exists='append')

# last_msg = get_last_msg('116826464720753')
# print(next_msg(last_msg,'nameez'))

# exit()

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
    
    data = {}
    for entry in response["entry"]:
        for change in entry["changes"]:
            if 'contacts' in change["value"]:
                data['type'] = change["field"]
                data['number'] = change["value"]["contacts"][0]["wa_id"]
                data['name'] = change["value"]['contacts'][0]['profile']['name']
                data['msg'] = change["value"]['messages'][0]['text']['body']
    
    if 'number' in data:
        last_msg = get_last_msg(data['number'])
        next_msg = next_msg(last_msg)

        if data['msg'] == '1':
            msg_response = " teste 1  |o|"

        if data['msg'] == '2':
            msg_response = "teste 2 =D "
        # Do anything with the response
        # print(msg_response)
        # print(str( data['number']))
        send_msg(msg_response,str( data['number']))

    return jsonify({"status": "success"}, 200)

if __name__ == '__main__': 
    app.run(debug=True)
