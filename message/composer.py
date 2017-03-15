import time
from email.header import Header
from message import IMSMessage, IMSMessageAttachment, IMSMIMEMultipartAlternative, \
    IMSMIMEMultipartMixed, IMSMIMEBase, IMSCharset
from email.utils import formatdate, make_msgid
from logger import logger


class IMSMessageComposer(IMSMessage):
    def __init__(self):
        IMSMessage.__init__(self)

    def set_subject(self, subject, encoding="base64", charset="utf-8"):
        charset = IMSCharset(charset)
        charset.set_header_encoding(encoding)
        self.set_header("Subject", str(Header(subject, charset)))

    def set_messageid(self, messageid=None):
        if messageid is None:
            messageid = make_msgid()
        self.set_header("Message-ID", messageid)

    def set_date(self, date=None):
        if date is None:
            date = formatdate(localtime=time.time())
        self.set_header("Date", date)

    def add_plain_body(self, body, encoding="base64", charset="utf-8"):
        if isinstance(body, IMSMIMEBase):
            self._body_plain_payload = body
        else:
            self._body_plain_payload = IMSMIMEBase('text', 'plain')
            self._body_plain_payload.set_payload(body)
            _charset = IMSCharset(charset)
            _charset.set_body_encoding(encoding)
            self._body_plain_payload.set_charset(_charset)

    def add_html_body(self, body, encoding="base64", charset="utf-8"):
        if isinstance(body, IMSMIMEBase):
            self._body_html_payload = body
        else:
            self._body_html_payload = IMSMIMEBase('text', 'html')
            self._body_html_payload.set_payload(body)
            _charset = IMSCharset(charset)
            _charset.set_body_encoding(encoding)
            self._body_html_payload.set_charset(_charset)

    def append_attachment(self, attachment, encoding="base64", charset="utf-8"):
        if self.attachments_payload is None:
            self._attachments_payload = {}
        if not isinstance(attachment, IMSMessageAttachment):
            attachment = IMSMessageAttachment(attachment, encoding, charset)
        self._attachments_payload[attachment.filename] = attachment.make_payload()

    def __str__(self):
        # keep structure of original email
        if getattr(self, "is_parsed", False):
            logger.debug("re-compose email")
            try:
                return self.as_string()
            except Exception as error:
                logger.debug("fail to compose parsed email: %s:%s" % (type(error), str(error)))

        # output email with new structure
        #  - fails to compose original email
        #  - if email is new created
        logger.debug("compose a new email")
        m = None
        if self.body_plain_payload:
            m = self.body_plain_payload
            logger.debug("added plain body")

        if self.attachments_payload:
            if self._payload:
                body_bound = self._payload[0].get_boundary()  # with attachment
            else:
                body_bound = None  # create a new one
        else:
            body_bound = self.get_boundary()  # no attachment

        if self.body_html_payload:
            if m:
                _m = IMSMIMEMultipartAlternative(boundary=body_bound)
                _m.attach(m)
                _m.attach(self._body_html_payload)
                m = _m
            else:
                m = self.body_html_payload
            logger.debug("added HTML body")

        if m is None:
            raise ValueError("no plain body or html body is specified")

        if self.attachments_payload:
            _m = IMSMIMEMultipartMixed(boundary=self.get_boundary())
            _m.attach(m)
            for n, v in self.attachments_payload.items():
                _m.attach(v)
                logger.debug("added attachment: %s" % n)
            m = _m

        # keep same order of header
        for k, v in m._headers:
            self.set_header(k, v)
        m._headers = self._headers
        return str(m)
