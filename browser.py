import socket
import ssl

class RequestHeaders:
    def __init__(self, path, host, conn="close"):
        self.path = path
        self.host = host
        self.conn = conn
        
    def createRequestHeaders(self):
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: {}\r\n".format(self.conn)
        request += "User-Agent: Py-Browser/1.0\r\n" 
        # essential to put two \r\n newlines, otherwise 
        # the other computer will keep waiting for them
        request += "\r\n"

        return request

class URL: 
    def __init__(self, url=""):

        self.scheme, url = url.split("://", 1)
        
        assert self.scheme in ["http", "https", "file"]

        if self.scheme in ["http", "file"]:
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)            
            self.port = int(port)

        self.path = "/" + url

    def request(self):
        s = socket.socket(
            family = socket.AF_INET,
            type = socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
      
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = RequestHeaders(self.path, self.host).createRequestHeaders()
        print(request)
        s.send(request.encode("utf8"))
        
        response = s.makefile("r", encoding="utf-8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        
        assert "transfer-enconding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close()
        return content
    
def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")    

def load(url):
    body = url.request()
    show(body)