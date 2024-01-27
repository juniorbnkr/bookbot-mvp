import json,requests,os,time
from sqlalchemy import create_engine  
from sqlalchemy import text
import pandas as pd

class Messages():

    def __init__(self,number,name,received_msg,wamid='') -> None:
        self.perm_token = os.getenv('perm_token')
        self.db_name = os.getenv('db_name')
        self.db_user = os.getenv('db_user')
        self.db_pass = os.getenv('db_pass')
        self.number = number
        self.name = name
        self.received_msg = received_msg
        self.template = ''
        self.msg_to_send = ''
        self.wamid = wamid
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
        # print(self.msg_
        # to_send)
        url = "https://graph.facebook.com/v17.0/116826464720753/messages/"
        
        if isinstance(self.msg_to_send,list):
            response = []
            for msg in self.msg_to_send:
                payload = json.dumps({
                "messaging_product": "whatsapp",
                "to": self.number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": msg
                }
                })
                headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+self.perm_token

                }
                response.append(requests.request("POST", url, headers=headers, data=payload))
        else:
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
                            WHERE cap = 0 AND content NOT LIKE '<%' ORDER BY line asc;"),dbConnection)    
                msg = ''
                for index, row in df.iterrows():
                    msg += row['content'] + '\n'
                msgs = [msg,' \n \n Digite: \n 1 para receber o capítulo seguinte \n 2 para ver o índice. \n \n ']
                self.msg_to_send = msgs
                #self.template = 'next'
                self.add_log(chap=0)
                return msgs

        if self.received_msg == '2':
            msg = 'O índice está em desenvolvimento 🚧 \n Digite 1 para o próximo capítulo'
            self.msg_to_send = msg
            return msg
        
        if self.received_msg.lower().replace('í', 'i').replace('ó', 'o') == 'proximo capitulo' \
            or self.received_msg == '1':
            msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} AND chap IS NOT NULL ORDER BY created_at DESC;"),dbConnection)
            if not msgs.empty:
                last_msg = msgs.iloc[0]
            else:
                last_msg = {'chap': None}

            if last_msg['chap'] is not None:
                last_cap = last_msg['chap']
                print(last_cap)
                df = pd.read_sql(text(f"SELECT * FROM bot_mvp.memoriasBras ml \
                            WHERE cap = {last_cap + 1} ORDER BY line asc;"),dbConnection)    
            else:
                last_cap = -1
                df = pd.read_sql(text(f"SELECT * FROM bot_mvp.memoriasBras ml \
                            WHERE cap = 0 AND content NOT LIKE '<%'ORDER BY line asc;"),dbConnection)
            
            msg = ''
            for index, row in df.iterrows():
                msg += row['content'] + '\n'

            # msg += "\n Envie 'Próximo Capítulo' para ver o capítulo seguinte"
            #self.template = 'next'
            if len(msg) > 4096:
                msgs = []
                for i in range(0,len(msg),4096):
                    msgs.append(msg[i:i+4096])
                msgs.append(' \n \n Digite: \n 1 para receber o capítulo seguinte \n 2 para ver o índice. \n \n ')
            else:
                msgs = [msg,' \n \n Digite: \n 1 para receber o capítulo seguinte \n 2 para ver o índice. \n \n ']
            self.msg_to_send = msgs
            self.add_log(chap=last_cap+1)
            return msgs

        msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} ORDER BY created_at DESC;"),dbConnection)

        if msgs.empty:
            msg = f"Olá {self.name}, seja bem vindo ao bookBot!"
            msgs = [msg,'Digite 1 para iniciar a leitura do livro Memórias Póstumas de Brás Cubas']
            self.msg_to_send = msgs
            # self.template = 'initial'
            self.add_log(template='initial')
            return msgs
        else:
            msgs = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} AND chap IS NOT NULL ORDER BY created_at DESC;"),dbConnection)
            if msgs.empty:
                msg = f"Olá {self.name}, seja bem vindo ao bookBot!"
                msgs = [msg,'Digite 1 para iniciar a leitura do livro Memórias Pósstumas de Brás Cubas']
                self.msg_to_send = msgs
                # self.template = 'initial'
                self.add_log(template='initial')
                return msgs
            else: 
                msg = f'''Olá {self.name}, seja bem vindo de volta ao bookBot! \n 
                    Você parou no capítulo {msgs.iloc[0]['chap']} \n Digite 1 para continuar'''
                self.msg_to_send = msg
                # self.template = 'return'
                self.add_log(template='return')
                return msg

    def add_log(self,chap=None,template=None):
        
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        if chap is None and template is None:
            raise Exception('One of chap or template is required')
        if chap is not None:
            dbConnection.execute(text(f"INSERT INTO bot_mvp.msg_log (phone_number, chap,block,wamid) VALUES ({self.number},{chap},1,'{self.wamid}');"))
            dbConnection.commit()
        elif template is not None:
            dbConnection.execute(text(f"INSERT INTO bot_mvp.msg_log (phone_number, template,block,wamid) VALUES ({self.number},'{template}',1,'{self.wamid}');"))
            dbConnection.commit()
        return None
    
    def check_repeat_msg(self):
        sqlEngine       = create_engine(f'mysql+pymysql://{self.db_user}:@{self.db_name}/bot_mvp?password={self.db_pass}', pool_recycle=3600, future=True)
        dbConnection    = sqlEngine.connect()
        df = pd.read_sql(text(f"SELECT * FROM bot_mvp.msg_log ml \
                        WHERE phone_number = {self.number} AND wamid = '{self.wamid}';"),dbConnection)
        if df.empty:
            return False
        else:
            print('repeated wamid')
            return True

