from http.server import HTTPServer, CGIHTTPRequestHandler
from threading import Thread
import cx_Oracle, time, datetime, ssl

class FirstHandler(CGIHTTPRequestHandler):
    def do_GET(self):             
        self.send_response(200, "OK")
        self.send_header('X-Frame-Options', 'deny')
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header("Content-Security-Policy", "default-src 'self'")
        self.send_header('Strict-Transport-Security', 'max-age=3600; includeSubDomains')
        
        if '&' in self.path:
            self.path = 'open_message.html'           
        if 'ssl' in self.path:
            self.path = 'index.html'
        if self.path == '/':
            self.path = 'index.html'        
        return CGIHTTPRequestHandler.do_GET(self)
    
class BaseDate(object):
    def connect_db(self):
        with open ('auth_db.txt', 'r') as db_file:
            text = db_file.readlines()
            login = text[0]
            password = text[1]
        return cx_Oracle.connect(f'{login[:-1]}/{password}@localhost:1521/xe')
    
    def del_db(self, fromm, value):        
        db = self.connect_db()
        db.cursor().execute(f"DELETE FROM {fromm} WHERE time < '%s'" %value)
        db.commit()
        db.close()

def start_server():
    with HTTPServer(('192.168.0.101', 5000), FirstHandler) as httpd:        
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain('ssl/server.crt', keyfile='ssl/server.key')
        httpd.socket = ctx.wrap_socket(httpd.socket)
        httpd.serve_forever()

def timer():
    while True:
        time.sleep(86400)
        time_now = datetime.datetime.now()
        BaseDate.del_db('users', time_now)
        BaseDate.del_db('secrets', time_now)

Thread(target=timer).start()
Thread(target=start_server).start()
