#!/usr/bin/python
import random, string
import gostcrypto, hashlib
import os, glob, datetime
import cx_Oracle

class BaseDate(object):
    """Работа с базой данных"""
    def connect_db(self):
        with open ('auth_db.txt', 'r') as db_file:
            text = db_file.readlines()
            login = text[0]
            password = text[1]
        return cx_Oracle.connect(f'{login[:-1]}/{password}@localhost:1521/xe')        

    def add_message(self, id, recipient, sender, message, time, key):
        db = self.connect_db()       
        sql = 'INSERT INTO secrets (id, recipient, sender, message, time, key) VALUES (:id, :recipient, :sender, :message, :time, :key)'
        db.cursor().execute(sql, [id, recipient, sender, message, time, key])
        db.commit()
        db.close()

    def cheсk_message(self, id):
        db = self.connect_db()
        db_value = db.cursor().execute("SELECT id, recipient, sender, message, time, key FROM secrets WHERE id = '%s'" %id).fetchone()
        try:
            values = dict()
            values['id'] = db_value[0]
            values['recipient'] = db_value[1]
            values['sender'] = db_value[2]
            values['message'] = db_value[3]
            values['time'] = datetime.datetime.strptime(db_value[4], '%Y-%m-%d %H:%M:%S.%f')
            values['key'] = db_value[5]
            return values
        except TypeError: return False
        finally: db.close()       
    
    def add_user(self, login, password, salt, time):
        db = self.connect_db()       
        sql = 'INSERT INTO users (login, password, salt, time) VALUES (:login, :password, :salt, :time)'
        db.cursor().execute(sql, [login, password, salt, time])
        db.commit()
        db.close()

    def cheсk_users(self, login):
        db = self.connect_db()
        db_value = db.cursor().execute("SELECT login, password, salt, time FROM users WHERE login = '%s'" %login).fetchone()
        try:                    
            values = dict() #создаем словарь
            values['login'] = db_value[0]
            values['password'] = db_value[1]
            values['salt'] = db_value[2]
            values['time'] = datetime.datetime.strptime(db_value[3], '%Y-%m-%d %H:%M:%S.%f')            
            return values
        except: return False
        finally: db.close()

    def del_db(self, id):
        db = self.connect_db()
        db.cursor().execute("DELETE FROM secrets WHERE id = '%s'" %id)
        db.commit()
        db.close()
    
def encryption(message, key):
    obj = gostcrypto.gostcipher.new('kuznechik', key.encode('utf-8'), gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
    encrypted_text = obj.encrypt(message.encode('utf-8'))
    return encrypted_text
    
def decryption(message, key):
    obj = gostcrypto.gostcipher.new('kuznechik', key.encode('utf-8'), gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
    decryption_text = obj.decrypt(message).decode('utf-8')
    return decryption_text

db = BaseDate()
def add_user(login, password):
    login = str(login)
    password = str(password)
    if db.cheсk_users(login) != False: return False
    else:
        salt = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])       
        hash_password = hashlib.sha256(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        time = str(datetime.datetime.now() + datetime.timedelta(days = 365))        
        db.add_user(login, hash_password, salt, time)
        return True

def check_user(login, password):
    login = str(login)
    password = str(password)
    user = db.cheсk_users(login)
    if user != False:        
        hash_password = hashlib.sha256(password.encode('utf-8') + user['salt'].encode('utf-8')).hexdigest()        
        if hash_password != user['password']: return False
        elif datetime.datetime.now() > user['time']: return False
        else: return True
    else: return False

def check_recipient(login):
    user = db.cheсk_users(str(login))
    time_del = datetime.datetime.strptime(user['time'], '%Y-%m-%d %H:%M:%S.%f')    
    if user == False: return False
    elif datetime.datetime.now() > time_del: return False
    else: return True

def send_message(data, type, sender, recipient):    
    user = db.cheсk_users(recipient)
    id = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])
    if user != False and db.cheсk_users(sender) != False:
        time = str(datetime.datetime.now() + datetime.timedelta(days = 7))
        key = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(32)])    
        kye_db = key[16:]
        link = 'https://192.168.0.101:5000/' + id + '&' + key[:16]
        if type == 'text':
            data = str(data)
            encryption_message = encryption(data, key) #шифруем сообщение
            with open ('messages/' + id + '.txt', 'wb') as new_file:
                new_file.write(encryption_message)
            db.add_message(id, recipient, sender, type, time, kye_db)
            return link
        elif type == 'file':
            with open ('files/' + id + '_' + data['file_name'], 'wb') as new_file:            
                encription_text = encryption(data['text_b'].decode('utf-8'), key)
                new_file.write(encription_text)                    
            db.add_message(id, recipient, sender, type, time, kye_db)
            return link
        else: return False
    else: return False

def open_message(link, recipient):
    try:
        id = link[:16]
    except TypeError: return False
    message = db.cheсk_message(id)    
    if message == False: return False
    elif datetime.datetime.now() > message['time']: return False
    elif message['recipient'] != recipient: return False
    else:
        key = link[17:] + message['key']
        text = dict()
        text['type'] = message['message']
        if message['message'] == 'text':
            with open ('messages/' + id + '.txt', 'rb') as old_file:
                encryption_text = old_file.read()
                try:
                    open_text = decryption(encryption_text, key)                    
                except gostcrypto.gostcipher.gost_34_13_2015.GOSTCipherError: return False 
                finally: old_file.close()
            os.remove('messages/' + id + '.txt') #удаляем
            db.del_db(id)
            text['text'] = f"Пользователь {message['sender']} отправил вам сообщение: {open_text}"
        
        elif message['message'] == 'file':
            file_name = glob.glob(f'files/{id}*')[0]
            with open(file_name, 'rb') as old_file:                
                encryption_text = old_file.read()
                try:
                    open_text = decryption(encryption_text, key)                    
                except gostcrypto.gostcipher.gost_34_13_2015.GOSTCipherError: return False 
                finally: old_file.close()
            
            file_name_new = file_name[23:]
            text['text'] = f"Пользователь {message['sender']} отправиль вам файл"
            text['value'] = open_text
            text['file_name'] = file_name_new    
        return text

