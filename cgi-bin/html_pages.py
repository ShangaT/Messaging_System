#!/usr/bin/python
def response(text):
    print ("Content-type:text/html; charset=utf-8")
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

def send_message(login):
    cookie = f"Set-cookie: user={login}; path=/cgi-bin/; httponly"
    print(cookie)
    print ("Content-type:text/html\n; charset=utf-8")
    content = """
    <html lang = "ru">
    <head>
        <title>Отпарвить сообщение</title>
        <meta charset="utf-8">
        <link rel="stylesheet" href="/css/style_index.css">
    </head>

    <body>
    <form method="post" enctype="multipart/form-data" action = "/cgi-bin/form.py">
        <h3 class="form_title">ОТПРАВИТЬ СООБЩЕНИЕ<br></h3>

        <div class="input_group">  
        <input type="text" placeholder = "Логин получателя" name = "recipient" required//> <br>
        <input type="text" placeholder = "Текст секретного сообщения" name = "secret"/> <br>
        <input type="file" name = "secret_file"/> <br>  
        <small class = "text">Если Вы хотите отправить файл, оставьте поле сообщения пустым </small> <br>
        <button class="big_button" type="submit" name="button" value="send"> ОТПРАВИТЬ </button> <br>
        </div>
    </form> <br>
    </body>
      """
    print(content)

def show_message(file_name):
    print ("Content-type:text/html; charset=utf-8")
    print()
    content = f"""
        <html lang = "ru">
            <head>
                <title>Ответ сервера</title>
                <meta charset="PyCharm">
                <link rel="stylesheet" href="/css/style_index.css">
            </head>

            <body>
            
            <button class="big_button" name="button" value="show" onclick="window.location.href = 'http://localhost:3000/files/{file_name}';"> ОТКРЫТЬ </button> <br>
            
            </body> """
    print(content)

def mes(file_name_new, open_text):
    print('Content-type: application/octet-stream') #отдаем пользователю
    print(f'Content-Disposition: attachment; filename="{file_name_new}"')
    print()
    print(f'{open_text}')
