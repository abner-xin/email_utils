import ssl
import socket
import poplib



POP3_SSL_PORT = 995


class POP3_SSL_WithProxy(poplib.POP3_SSL):
    """support http proxy for pop3 connection"""

    def __init__(self, host, port=POP3_SSL_PORT, keyfile=None, certfile=None, http_proxy=None):
        self.host = host
        self.port = port
        self.keyfile = keyfile
        self.certfile = certfile
        self.buffer = ""
        self.my_http_proxy = http_proxy
        msg = "getaddrinfo returns an empty list"
        self.sock = None
        for res in socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                # self.sock = socket.socket(af, socktype, proto)
                import socks
                self.sock = socks.socksocket()
                if self.my_http_proxy:
                    addr, port = self.my_http_proxy.split(':')
                    self.sock.setproxy(socks.PROXY_TYPE_HTTP, addr=addr, port=int(port))
                self.sock.connect(sa)
            except socket.error, msg:
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg
        self.file = self.sock.makefile('rb')
        self.sslobj = ssl.wrap_socket(self.sock, self.keyfile, self.certfile)
        self._debugging = 0
        self.welcome = self._getresp()