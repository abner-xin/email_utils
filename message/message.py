import re
from email.header import decode_header
from email.message import Message
from email.errors import HeaderParseError
from email.parser import Parser
from logger import logger


def decode_header_value(value):
    raw_value = re.sub("\r?\n", "", value)  # multiple line headers
    v_charset_list = decode_header(raw_value)
    v_list = []
    for v, charset in v_charset_list:
        if charset:
            v = v.decode(charset)
        v_list.append(v)
    _value = "".join(v_list).strip()
    logger.debug("decoded header value: %s" % _value)
    return _value


class IMSMessage(Message):
    attachment_include_inline = False
    strip_body_end_blank_line = True

    def __init__(self):
        Message.__init__(self)
        self._body_plain = None
        self._body_plain_payload = None
        self._body_html = None
        self._body_html_payload = None
        self._attachments = None
        self._attachments_payload = None

    def my_log(self, msg):
        return "#%s - %s" % (id(self), msg)

    def get_header_value(self, header_name):
        raw_value = self.get(header_name)
        logger.debug(self.my_log("primitive header: %s " % raw_value))
        if raw_value is None:
            raise HeaderParseError("header [%s] not exist" % header_name)
        else:
            return decode_header_value(raw_value)

    def set_header(self, _name, _value):
        try:
            self.replace_header(_name, _value)
        except KeyError:
            self.add_header(_name, _value)
        logger.info(self.my_log("set header - %s:%s" % (_name, _value)))

    def del_header(self, _name):
        if self.get(_name):
            del self[_name]

    @property
    def subject(self):
        return self.get_header_value('Subject')

    @property
    def messageId(self):
        return self.get_header_value('Message-ID')

    @classmethod
    def is_payload_match_content_disposition(cls, payload, content_disposition):
        _content_disposition = payload.get('Content-Disposition')
        if _content_disposition:
            if _content_disposition.startswith(content_disposition):
                logger.debug("matched expected content disposition")
                return True
            else:
                logger.debug("content disposition is %s, no matched expected: %s" %
                            (_content_disposition, content_disposition))
        else:
            logger.debug("no content disposition found")
        return False

    @classmethod
    def match_payload(cls, payload, content_type=None, is_attachment=False):
        if content_type and payload.get_content_type() == content_type:
            logger.debug("content type match: %s" % payload.get_content_type())
            return True

        if is_attachment:
            if cls.is_payload_match_content_disposition(payload, 'attachment'):
                return True
        return False

    @classmethod
    def search_payload(cls, payload=None, content_type=None, is_attachment=False):
        matched_entities = []
        logger.debug("search payload: %s" % payload.get_content_type())
        if payload.is_multipart():
            logger.debug("multipart: %s" % payload.get_content_type())
            payload_iterator = cls.walk(payload)
            payload_iterator.next()  # skip current payload
            for _payload in payload_iterator:
                matched_entities += cls.search_payload(_payload, content_type, is_attachment)
        else:
            logger.debug("NOT multipart: %s" % payload.get_content_type())
            if cls.match_payload(payload, content_type, is_attachment):
                matched_entities.append(payload)
        return matched_entities

    @property
    def body_plain_payload(self):
        if self._body_plain_payload is None:
            _body_payload = self.search_payload(self, 'text/plain')
            if _body_payload:
                self._body_plain_payload = _body_payload[0]
            else:
                logger.debug(self.my_log("not find plain body entity"))
        return self._body_plain_payload

    @property
    def body_plain(self):
        if self._body_plain is None:
            self._body_plain = self.decode_body_payload(self.body_plain_payload)
            if self._body_plain:
                logger.info(self.my_log("plain body length: %s" % len(self._body_plain)))
        return self._body_plain

    @property
    def body_html_payload(self):
        if self._body_html_payload is None:
            _body_payload = self.search_payload(self, 'text/html')
            if _body_payload:
                self._body_html_payload = _body_payload[0]
            else:
                logger.debug(self.my_log("not find html body entity"))
        return self._body_html_payload

    @classmethod
    def decode_body_payload(cls, payload):
        if payload:
            decoded_content = payload.get_payload(decode=True)  # it only decode QP or base64
            charset = payload.get_param('charset')  # decode the body to unicode with charset if it exist
            if charset:
                decoded_content = decoded_content.decode(charset)
            if cls.strip_body_end_blank_line:
                decoded_content = decoded_content.strip()
            return decoded_content
        else:
            return None

    @property
    def body_html(self):
        if self._body_html is None:
            self._body_html = self.decode_body_payload(self.body_html_payload)
            if self._body_html:
                logger.info(self.my_log("HTML body length: %s" % len(self._body_html)))
        return self._body_html

    @property
    def body(self):
        _body = []
        if self.body_plain:
            _body.append(self.body_plain)

        if self.body_html:
            _body.append(self.body_html)

        return _body

    @property
    def attachments_payload(self):
        if self._attachments_payload is None:
            self._attachments_payload = {}
            _payloads = self.search_payload(self, is_attachment=True)
            if _payloads:
                for _payload in _payloads:
                    filename = decode_header_value(_payload.get_filename())
                    self._attachments_payload[filename] = _payload
            logger.info(self.my_log("message contains attachments: %s" % self._attachments_payload.keys()))
        return self._attachments_payload

    @property
    def attachments(self):
        if self._attachments is None:
            self._attachments = {}
            for name, payload in self.attachments_payload.items():
                self._attachments[name] = payload.get_payload(decode=True)
        return self._attachments

    @classmethod
    def is_contain(cls, s, d, match_exact):
        if match_exact:
            return s == d
        else:
            return s in d

    def is_header_value_contain(self, header, value, match_exact=False):
        _value = self.get_header_value(header)
        logger.info("message header value: %s" % _value)
        return self.is_contain(value, _value, match_exact)

    def is_plain_body_contain(self, s, match_exact=False):
        return self.is_contain(s, self.body_plain, match_exact)

    def is_html_body_contain(self, s, match_exact=False):
        return self.is_contain(s, self.body_html, match_exact)

    def is_contain_attachment(self, name):
        return name in self.attachments_payload.keys()

    def is_attachment_contain(self, name, s, match_exact=False):
        return self.is_contain(s, self.attachments[name], match_exact)

    def is_equal(self, message, match_subject=True, match_body=True, match_attachment=True):
        """only check subject/body/attachment"""
        assert isinstance(message, IMSMessage)
        match_res = []
        if match_subject:
            is_subject_match = self.is_contain(self.subject, message.subject, True)
            logger.info("subject %s matched" % '' if is_subject_match else 'not')
            match_res.append(is_subject_match)

        if match_body:
            is_plain_match = self.body_plain == message.body_plain
            logger.info("plain body %s matched" % '' if is_plain_match else 'not')

            is_html_match = self.body_html == message.body_html
            logger.info("html body %s matched" % '' if is_html_match else 'not')

            match_res.append(all([is_plain_match, is_html_match]))
        if match_attachment:
            is_attachment_match = self.attachments == message.attachments
            logger.info("attachments %s matched" % '' if is_attachment_match else 'not')
            match_res.append(is_attachment_match)

        return match_res

    def __str__(self):
        return self.as_string(unixfrom=False)


class IMSMessageParser(Parser):
    def __init__(self, *args, **kws):
        if '_class' not in kws:
            kws['_class'] = IMSMessage
        Parser.__init__(self, *args, **kws)

    def message_from_file(self, filename):
        logger.info("parse message from file: %s" % filename)
        with open(filename, 'r') as fp:
        # with codecs.open(filename, 'rb', 'utf-8') as fp:
            m = self.parse(fp)
            setattr(m, "is_parsed", True)
            setattr(m, "file", filename)
            logger.info(m.my_log("parsed message from file: %s" % filename))
            return m

    def message_from_string(self, s):
        m = self.parsestr(s)
        setattr(m, "is_parsed", True)
        logger.info(m.my_log("parsed message from string"))
        return m
