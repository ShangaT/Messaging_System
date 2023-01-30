import cgi
import sqlite3
import random, string
import html, hashlib
import datetime, time
import rsa, gostcrypto

form = cgi.FieldStorage() #получаем данные из форм

send = form.getfirst("send") #кнопки
open = form.getfirst("open")
registration = form.getfirst("registration")
db = sqlite3.connect("Users.db") #подключаемся к базе данных

def Show_in_browser(text):
    print ("Content-type:text/html; charset=PyCharm")
    print()
    content = f"""
        <html lang = "ru">
            <head>
                <title>Ответ сервера</title>
                <meta charset="PyCharm">
                <link rel="stylesheet" href="/css/style_answer.css">
            </head>

            <body>
            <h3 class = "text"> {text} </h3>
            </body> """
    print(content)

class BaseDate(object):
    """Работа с базой данных"""
    def Check_db(self, select, fromm, where, value):
        db = sqlite3.connect("Users.db")
        db.row_factory = lambda cursor, row: row[0]
        db_req = f'SELECT {select} FROM {fromm} WHERE {where} == "{value}";' #ищем есть ли в базе
        db_value = db.cursor().execute(db_req).fetchone() #записываем в переменную
        return db_value

    def Verification_existence(func):
        def Check(self, arg):
            if self.__class__.__name__ == 'Users':
                if self.Check_db('login', 'users', 'login', arg) != None:
                    func(self, arg)
                    return True
                else: return False
            elif self.__class__.__name__ == 'Messages':
                if self.Check_db('key', 'secrets', 'key', arg) != None:
                    func(self, arg)
                    return True
                else: return False
        return Check

    def Delete_db(self, fromm, where, value):
        db = sqlite3.connect("Users.db")
        db.row_factory = lambda cursor, row: row[0]
        db_req = f"DELETE FROM {fromm} WHERE {where} == '{value}';"
        db_value = db.cursor().execute(db_req)
        db.commit()

    def Add_User(self, login, password, salt, time, public_key, private_key):
        value = login, password, salt, time, public_key, private_key
        db.cursor().execute("INSERT INTO users (login, password, salt, time, public, private) VALUES (?, ?, ?, ?, ?, ?)", (value)) #кортеж от SQL-инъекций
        db.commit() #сохраняем базу

    def Add_Message (self, id, recipient, sender, message, time):
        value = id, recipient, sender, message, time
        db.cursor().execute("INSERT INTO secrets (key, recipient, sender, message, time) VALUES (?, ?, ?, ?, ?)", (value))
        db.commit()

class Users(BaseDate):
    """Описание пользователя"""
    password = None
    time = None
    salt = None
    public_key = None
    private_key = None

    def __init__(self, login):
        self.login = login

    def RSA(self, password):
        key = password.rjust(32, '0').encode('utf-8') #добавляем к паролю символы до нужной длинный
        (public_key, private_key) = rsa.newkeys(2048) #формирование ключей для RSA
        pub_k = public_key.save_pkcs1()
        pr_k = private_key.save_pkcs1()

        obj = gostcrypto.gostcipher.new('kuznechik', key, gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
        encrypted_private_key = obj.encrypt(pr_k) #шифруем приватный ключ кузнечиком

        keys = dict() #создаем словарь
        keys['public'] = pub_k
        keys['private'] = encrypted_private_key
        return keys

    def Write(self, login, password):
        self.salt = ''.join([random.choice(string.ascii_lowercase + string.digits) for i in range(64)]).encode('utf-8')
        self.password = hashlib.sha256(password.encode('utf-8') + self.salt).hexdigest()
        self.time = datetime.datetime.now() + datetime.timedelta(days = 365)
        keys = self.RSA(password)
        self.public_key = keys['public']
        self.private_key = keys['private']

    @BaseDate.Verification_existence
    def Read(self, login):
        self.salt = self.Check_db('salt', 'users', 'login', login)
        self.password = self.Check_db('password', 'users', 'login', login)
        time_del_login_str = self.Check_db('time', 'users', 'login', login) #получаем время хранения учетной записи
        self.time =  datetime.datetime.strptime(time_del_login_str, '%Y-%m-%d %H:%M:%S.%f') #преобразуем строку в формат даты и времени
        self.public_key = self.Check_db('public', 'users', 'login', login)
        self.private_key = self.Check_db('private', 'users', 'login', login)

class Messages(BaseDate):
    """Описание сообщения"""
    id = None
    sender = None
    resipient = None
    message = None
    time = None

    def Encryption (self, message, key):
        ks = rsa.PublicKey.load_pkcs1(key)
        encrypted_secret = rsa.encrypt(message, ks)
        return encrypted_secret

    def Decryption (self, password, key_RSA_encript, message_encrypt):
        key_kuznechik = password.rjust(32, '0').encode('utf-8')
        obj = gostcrypto.gostcipher.new('kuznechik', key_kuznechik, gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
        key_RSA = obj.decrypt(key_RSA_encript).decode('utf-8')
        key_rsa_import = rsa.PrivateKey.load_pkcs1(key_RSA)
        decryption_message = rsa.decrypt(message_encrypt, key_rsa_import).decode('utf-8')
        return decryption_message

    def Write(self, sender, resipient, message):
        self.id = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])
        self.sender = sender
        self.resipient = resipient
        self.message = message
        self.time = datetime.datetime.now() + datetime.timedelta(days = 7)

    @BaseDate.Verification_existence
    def Read(self, id):
        self.id = id
        self.sender = self.Check_db('sender', 'secrets', 'key', id)
        self.resipient = self.Check_db('recipient', 'secrets', 'key', id)
        self.message = self.Check_db('message', 'secrets', 'key', id)
        time_del_message_str = self.Check_db('time', 'secrets', 'key', id)
        self.time = datetime.datetime.strptime(time_del_message_str, '%Y-%m-%d %H:%M:%S.%f')

def Registration():
    login = html.escape(form.getfirst("login_new")) # html.escape - экранируем от XXS-атак через форму ввода
    password = html.escape(form.getfirst("password1"))

    user = Users(login)
    if user.Check_db('login', 'users', 'login', user.login) == None:
        user.Write(user.login, password)
        user.Add_User(user.login, user.password, user.salt, user.time, user.public_key, user.private_key)
        Show_in_browser ('Вы зарегистрированы')
    else: Show_in_browser ('Пользователь с таким логином уже зарегистрирвоан, придумайте другой')
    del user

def Send():
    login_sender = html.escape(form.getfirst("login_sender"))
    password_sender = html.escape(form.getfirst("password_sender")).encode('utf-8')
    login_recipient = html.escape(form.getfirst("login_recipient"))
    secret = html.escape(form.getfirst("secret")).encode('utf-8')

    sender = Users(login_sender)
    sender_read = sender.Read(sender.login)
    resipient = Users(login_recipient)
    resipient_read = resipient.Read(resipient.login)

    #проверяем отправителя
    if sender_read == False: Show_in_browser('Вы ввели несуществующий логин или время действия вашей учетной записи истекло')
    elif datetime.datetime.now() > sender.time:
        sender.Delete_db('users', 'login', sender.login)
        Show_in_browser('Вы ввели несуществующий логин или время действия вашей учетной записи истекло')
    elif sender.password != hashlib.sha256(password_sender + sender.salt).hexdigest():
        Show_in_browser('Вы ввели неправильный пароль')
    # #проверяем получателя
    elif resipient_read == False: Show_in_browser('Вы ввели несуществующий логин получателя или время действия его учетной записи истекло')
    elif datetime.datetime.now() > sender.time:
        resipient.Delete_db('users', 'login', resipient.login)
        Show_in_browser('Вы ввели несуществующий логин получателя или время действия его учетной записи истекло')
    else:
        message = Messages()
        encrypted_message = message.Encryption (secret, resipient.public_key) #шифруем сообщение
        message.Write(login_sender, login_recipient, encrypted_message)
        message.Add_Message(message.id, message.resipient, message.sender, message.message, message.time)
        Show_in_browser(f"Для пользователя {resipient.login} сформерован идентификатор: {message.id}")
    del sender
    del resipient
    del message


def Open():
    login = form.getfirst("login") #поля для получения
    password = form.getfirst("password")
    id = form.getfirst("key")

    resipient = Users(login)
    resipient_read = resipient.Read(resipient.login)
    message = Messages()
    message_read = message.Read(id)

    #проверяем получателя
    if resipient_read == False: Show_in_browser('Вы ввели несуществующий логин или время действия вашей учетной записи истекло')
    elif datetime.datetime.now() > resipient.time:
        resipient.Delete_db('users', 'login', resipient.login)
        Show_in_browser('Вы ввели несуществующий логин или время действия вашей учетной записи истекло')
    elif resipient.password != hashlib.sha256(password.encode('utf-8') + resipient.salt).hexdigest():
        Show_in_browser('Вы ввели неправильный пароль')
    #проверяем сообщение
    elif message_read == False: Show_in_browser('Сообщения с таким идентификатором не существует или его срок хранения истек')
    elif datetime.datetime.now() > message.time:
        message.Delete_db('secrets', 'key', message.id)
        Show_in_browser('Сообщения с таким идентификатором не существует или его срок хранения истек')
    elif resipient.login != message.resipient: Show_in_browser('Сообщение предназначено другому пользователю')
    else:
        secret = message.Decryption(password, resipient.private_key, message.message)
        Show_in_browser(f"Пользователь {message.sender} отправил Вам сообщение: {secret}")
        secret.Delete_db('secrets', 'key', message.id)
    del resipient
    del message


if send != None: Send()
elif open != None: Open()
elif registration != None: Registration()

#rsa.pkcs1.DecryptionError
