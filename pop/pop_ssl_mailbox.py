import StringIO


POP3_SSL_PORT = 995


class POP3_SSL_Mailbox:
    def __init__(self, pop3_host, port=POP3_SSL_PORT):
        self.host = pop3_host
        self.port = port
        self.user = None
        self.password = None
        self._pop3_connection = None
        self.http_proxy = None

    def set_account(self, user, password):
        self.user = user
        self.password = password

    def set_proxy(self, http_proxy):
        self.http_proxy = http_proxy

    @property
    def pop3_connection(self):
        if self._pop3_connection is None:
            host = self.host
            if isinstance(self.host, basestring):
                host = [self.host, ]

            from .pop_ssl_connection import POP3_SSL_WithProxy
            for o in host:
                try:
                    self._pop3_connection = POP3_SSL_WithProxy(o, http_proxy=self.http_proxy)
                except Exception as error:
                    print "Exception when connect %s: %s" % (o, error)
                else:
                    break
        return self._pop3_connection

    def fetch_all_emails(self):
        emails_fp = []
        resp, items, octets = self.pop3_connection.list()
        for item in items:
            _id, size = item.split()
            resp, text, octets = self.pop3_connection.retr(_id)
            emails_fp.append(StringIO.StringIO(text))
        return emails_fp

    def delete_all_emails(self):
        """will delete all unread emails"""
        resp, items, octets = self.pop3_connection.list()
        for item in items:
            _id, size = item.split()
            self.pop3_connection.dele(_id)
