#!/usr/bin/python
import os, cgi, html, http.cookies
import check_api, html_pages

def main():
    form = cgi.FieldStorage()
    button = form.getfirst("button") #кнопки

    if button == 'enter':
        login = html.escape(form.getfirst("login"))
        password = html.escape(form.getfirst("password"))
        check = check_api.check_user(login, password)
        if check == True: html_pages.send_message(login)
        elif check == False: html_pages.response('Ошибка входа')

    if button == 'registration':
        login = html.escape(form.getfirst("login_new"))
        password = html.escape(form.getfirst("password1"))
        registration = check_api.add_user(login, password)
        if registration == True: html_pages.response('Вы зарегистрированы')
        else: html_pages.response('Пользователь с таким логином уже существует, придумайте другой')

    if button == 'send':
        cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
        sender = cookie.get("user")
        recipient = html.escape(form.getfirst("recipient"))
        secret = html.escape(form.getfirst("secret"))        
        if form.getfirst("secret") == '':
            f = form["secret_file"]   
            if f.filename:   
                fn = os.path.basename(f.filename)           
                open_text = f.file.read()
                data = dict()
                data['file_name'] = fn
                data['text_b'] = open_text
                check = check_api.send_message(data, 'file', sender.value, recipient)            
                if check == False: html_pages.response('Ошибка проверки получателя')
                else: html_pages.response(f"Отправьте полльзователю {recipient} ссылкку: {check}")
        else:
            check = check_api.send_message(secret, 'text', sender.value, recipient)            
            if check == False: html_pages.response('Ошибка проверки получателя')
            else: html_pages.response(f"Отправьте полльзователю {recipient} ссылкку: {check}")

    if button == 'open':
        login = html.escape(form.getfirst("login"))
        password = html.escape(form.getfirst("password"))
        url = os.environ.get("HTTP_REFERER")[27:]
        check = check_api.check_user(login, password)
        text = check_api.open_message(url, login)        
        if check == False: html_pages.response('Ошибка входа')
        elif text == False: html_pages.response('Ошибочная ссылка или сообщение предназначено другому пользователю')
        elif text['type'] == 'text': html_pages.response(text['text'])
        elif text['type'] == 'file': 
            html_pages.mes(text['file_name'], text['value'])

if __name__ == "__main__":
    main()