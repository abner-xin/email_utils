from email.charset import Charset, QP, BASE64, DEFAULT_CHARSET


class IMSCharset(Charset):
    charset_encoding = {"base64": BASE64, "qp": QP}

    def __init__(self, input_charset=DEFAULT_CHARSET):
        Charset.__init__(self, input_charset=input_charset)

    def set_header_encoding(self, encoding):
        if self.charset_encoding.get(encoding, None):
            self.header_encoding = self.charset_encoding[encoding]

    def set_body_encoding(self, encoding):
        if self.charset_encoding.get(encoding, None):
            self.body_encoding = self.charset_encoding[encoding]
