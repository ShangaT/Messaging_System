from http.server import HTTPServer, CGIHTTPRequestHandler
import ssl

httpd = HTTPServer(('localhost', 5000), CGIHTTPRequestHandler)

ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ctx.load_cert_chain('ssl/server.crt', keyfile='ssl/server.key')
httpd.socket = ctx.wrap_socket(httpd.socket)

httpd.serve_forever()
