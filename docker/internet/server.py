from http.server import HTTPServer, BaseHTTPRequestHandler

class HelloWorldHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        
        html_content = """Hello, World !"""
        
        self.wfile.write(html_content.encode("utf-8"))

server_address = ("", 8000)

httpd = HTTPServer(server_address, HelloWorldHandler)
httpd.serve_forever()
