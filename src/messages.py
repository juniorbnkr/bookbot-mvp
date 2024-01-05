import json,requests,os,time
from sqlalchemy import create_engine  
from sqlalchemy import text
import pandas as pd

class Messages():

    def __init__(self,number,name,received_msg) -> None:
        self.perm_token = os.getenv('perm_token')
        self.db_name = os.getenv('db_name')
        self.db_user = os.getenv('db_user')
        self.db_pass = os.getenv('db_pass')
        self.number = number
        self.name = name
        self.received_msg = received_msg
        self.template = ''
        self.msg_to_send = ''
        return None    

    def check_block(self):
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml WHERE phone_number = {self.number} \
                                AND block = 1 ORDER BY created_at DESC;"),dbConnection)

        print(msgs.empty)
        print(msgs)
        print(len(msgs))
        if not msgs.empty:
            return True
        return False
    
    def unblock(self):
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        dbConnection.execute(text(f'UPDATE bot_mvp.msg_log SET block = 0 WHERE phone_number = {self.number};'))
        dbConnection.commit()
        return None
    
    def send_msg(self):
        self.msg_to_send = self.next_msg()
        print(self.msg_to_send)
        url = "https://graph.facebook.com/v17.0/116826464720753/messages/"

        payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": self.number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": self.msg_to_send
        }
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+self.perm_token

        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print('post feito')
        print(response.status_code)
        print(response.text)
        # response = httpx.post(url, data=payload, headers=headers)
        print('template',self.template)
        if self.template != '':
            self.send_template()
        return response

    def send_template(self):
        
        url = "https://graph.facebook.com/v17.0/116826464720753/messages/"

        payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": self.number,
        "type": "template",
        "template": {
            "name": self.template,
            "language" : {"code":"pt_BR"}
        }
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+self.perm_token

        }

        response = requests.request("POST", url, headers=headers, data=payload)
        # response = httpx.post(url, data=payload, headers=headers)
        # print(response.text)
        return response

    def get_last_msg(self):
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        df = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} AND template IS NULL ORDER BY created_at DESC LIMIT 1;"),dbConnection)

        return df

    def next_msg(self):
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        print(self.received_msg)
        if self.received_msg.lower() == 'sim':
            msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} AND chap IS NOT NULL ORDER BY created_at DESC;"),dbConnection)
            if not msgs.empty:
                self.received_msg = 'Próximo capítulo'
            else:
                df = pd.read_sql(text(f"SELECT * FROM bot_mvp.memoriasBras ml \
                            WHERE cap = 0 ORDER BY line asc;"),dbConnection)    
                msg = ''
                for index, row in df.iterrows():
                    msg += row['content'] + '\n'
                self.msg_to_send = msg
                self.template = 'next'
                self.add_log(chap=0)
                return msg

        if self.received_msg.lower().replace('í', 'i').replace('ó', 'o') == 'proximo capitulo':
            msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} AND chap IS NOT NULL ORDER BY created_at DESC;"),dbConnection)
            last_msg = msgs.iloc[0]
            if last_msg['chap'] is not None:
                last_cap = last_msg['chap']
                print(last_cap)
                df = pd.read_sql(text(f"SELECT * FROM bot_mvp.memoriasBras ml \
                            WHERE cap = {last_cap + 1} ORDER BY line asc;"),dbConnection)    
                msg = ''
                for index, row in df.iterrows():
                    msg += row['content'] + '\n'
                
                # msg += "\n Envie 'Próximo Capítulo' para ver o capítulo seguinte"
                self.template = 'next'
                self.msg_to_send = msg
                self.add_log(chap=last_cap+1)
                return msg
    
        msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} ORDER BY created_at DESC;"),dbConnection)

        if msgs.empty:
            msg = f"Olá {self.name}, seja bem vindo ao bookBot!"
            self.msg_to_send = msg
            self.template = 'initial'
            self.add_log(template='initial')
            return msg
        else:
            msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} AND chap IS NOT NULL ORDER BY created_at DESC;"),dbConnection)
            if msgs.empty:
                msg = f"Olá {self.name}, seja bem vindo ao bookBot!"
                self.msg_to_send = msg
                self.template = 'initial'
                self.add_log(template='initial')
                return msg
            else: 
                msg = f'''Olá {self.name}, seja bem vindo de volta ao bookBot! \n 
                    Você parou no capítulo {msgs.iloc[0]['chap']} \n Digite Sim para continuar'''
                self.msg_to_send = msg
                self.template = 'return'
                self.add_log(template='return')
                return msg

    def add_log(self,chap=None,template=None):
        
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        if chap is None and template is None:
            raise Exception('One of chap or template is required')
        if chap is not None:
            dbConnection.execute(text(f"INSERT INTO bot_mvp.msg_log (phone_number, chap,block) VALUES ({self.number},{chap},1);"))
            dbConnection.commit()
        elif template is not None:
            dbConnection.execute(text(f"INSERT INTO bot_mvp.msg_log (phone_number, template,block) VALUES ({self.number},'{template}',1);"))
            dbConnection.commit()
        return None

