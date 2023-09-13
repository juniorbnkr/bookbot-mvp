import json,requests,os,time
from sqlalchemy import create_engine  
from sqlalchemy import text
import pandas as pd

perm_token = os.getenv('perm_token')
db_name = os.getenv('db_name')
db_user = os.getenv('db_user')
db_pass = os.getenv('db_pass')

def send_msg(msg,number):
    url = "https://graph.facebook.com/v17.0/116826464720753/messages/"
    # print(perm_token)

    payload = json.dumps({
    "messaging_product": "whatsapp",
    "to": number,
    "type": "text",
    "text": {
        "preview_url": False,
        "body": msg
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+perm_token

    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # response = httpx.post(url, data=payload, headers=headers)
    # print(response.text)
    return response

def send_template(template,number):
    
    url = "https://graph.facebook.com/v17.0/116826464720753/messages/"

    payload = json.dumps({
    "messaging_product": "whatsapp",
    "to": number,
    "type": "template",
    "template": {
        "name": template,
        "language" : {"code":"pt_BR"}
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+perm_token

    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # response = httpx.post(url, data=payload, headers=headers)
    # print(response.text)
    return response

def get_last_msg(number):
    sqlEngine       = create_engine(f'mysql+pymysql://{db_user}:@{db_name}/bot_mvp?password={db_pass}', pool_recycle=3600, future=True)
    dbConnection    = sqlEngine.connect()
    df = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                     WHERE phone_number = {number} AND template IS NULL ORDER BY created_at DESC LIMIT 1;"),dbConnection)

    return df

def next_msg(number,name,input_msg):
    
    sqlEngine       = create_engine(f'mysql+pymysql://{db_user}:@{db_name}/bot_mvp?password={db_pass}', pool_recycle=3600, future=True)
    dbConnection    = sqlEngine.connect()
    if input_msg == 'Sim':
        msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                     WHERE phone_number = {number} AND chap IS NOT NULL ORDER BY created_at DESC;"),dbConnection)
        if not msgs.empty:
            input_msg = 'Próximo Capítulo'
        else:
            df = pd.read_sql(text(f"SELECT * FROM bot_mvp.memoriasBras ml \
                        WHERE cap = 0 ORDER BY line asc;"),dbConnection)    
            msg = ''
            for index, row in df.iterrows():
                msg += row['content'] + '\n'
            send_msg(msg,number)
            add_log(number,0,None)
            send_template('next',number)
            add_log(number,None,'next')
            return msg

    if input_msg == 'Próximo Capítulo':
        msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                     WHERE phone_number = {number} AND chap IS NOT NULL ORDER BY created_at DESC;"),dbConnection)
        last_msg = msgs.iloc[0]
        if last_msg['chap'] is not None:
            last_cap = last_msg['chap']
            print(last_cap)
            df = pd.read_sql(text(f"SELECT * FROM bot_mvp.memoriasBras ml \
                        WHERE cap = {last_cap + 1} ORDER BY line asc;"),dbConnection)    
            msg = ''
            for index, row in df.iterrows():
                msg += row['content'] + '\n'
            send_msg(msg,number)
            print('-------------------- send_msg 100')
            add_log(number,last_cap+1,None)
            send_template('next',number)
            add_log(number,None,'next')
            return None
   
    msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                     WHERE phone_number = {number} ORDER BY created_at DESC;"),dbConnection)
    print(msgs)
    if msgs.empty:
        msg_response = f"Olá {name}, seja bem vindo ao bookBot!"
        print('-------------------- send_msg 110')
        send_msg(msg_response,number)
        print('-------------------- send template initial 112') 
        send_template('initial',number)
        add_log(number,None,'initial')
        return None
    else:
        msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                     WHERE phone_number = {number} AND chap IS NOT NULL ORDER BY created_at DESC;"),dbConnection)
        if msgs.empty:
            msg_response = f"Olá {name}, seja bem vindo ao bookBot!"
            print('-------------------- send msg 121')
            send_msg(msg_response,number)        
            print('-------------------- send template initial 123')     
            send_template('initial',number)
            add_log(number,None,'initial')
            return None
        else: 
            msg_response = f'''Olá {name}, seja bem vindo de volta ao bookBot! \n 
                Você parou no capítulo {msgs.iloc[0]['chap']}'''
            print('-------------------- send msg 130')
            send_msg(msg_response,number)        
            print('-------------------- send template return 133')     
            send_template('return',number)
            add_log(number,None,'return')
            return None

def add_log(number,chap=None,template=None):
    
    sqlEngine       = create_engine(f'mysql+pymysql://{db_user}:@{db_name}/bot_mvp?password={db_pass}', pool_recycle=3600, future=True)
    dbConnection    = sqlEngine.connect()
    if chap is None and template is None:
        raise Exception('One of chap or template is required')
    if chap is not None:
        dbConnection.execute(text(f"INSERT INTO bot_mvp.msg_log (phone_number, chap) VALUES ({number},{chap});"))
        dbConnection.commit()
    elif template is not None:
        dbConnection.execute(text(f"INSERT INTO bot_mvp.msg_log (phone_number, template) VALUES ({number},'{template}');"))
        dbConnection.commit()
    return None

def save_event(event):
    sqlEngine       = create_engine(f'mysql+pymysql://{db_user}:@{db_name}/bot_mvp?password={db_pass}', pool_recycle=3600, future=True)
    dbConnection    = sqlEngine.connect()
    dbConnection.execute(text(f'INSERT INTO bot_mvp.events_received (event) VALUES ("{event}");'))
    dbConnection.commit()
    return None
