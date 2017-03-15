import os
import mimetypes

from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from logger import logger

from .message import IMSMessage
from .charset import IMSCharset


class IMSMIMEBase(IMSMessage):
    def __init__(self, _maintype, _subtype, **_params):
        IMSMessage.__init__(self)
        ctype = '%s/%s' % (_maintype, _subtype)
        self.add_header('Content-Type', ctype, **_params)
        self['MIME-Version'] = '1.0'
        self.set_unixfrom("X-Creator: Python Scripts")


class IMSMIMEMultipart(IMSMIMEBase):
    def __init__(self, _subtype='mixed', boundary=None, _subparts=None, **_params):
        IMSMIMEBase.__init__(self, 'multipart', _subtype, **_params)
        self._payload = []

        if _subparts:
            for p in _subparts:
                self.attach(p)
        if boundary:
            self.set_boundary(boundary)


class IMSMIMEMultipartMixed(IMSMIMEBase):
    def __init__(self, boundary=None, _subparts=None, **_params):
        IMSMIMEBase.__init__(self, 'multipart', 'mixed', **_params)
        self._payload = []

        if _subparts:
            for p in _subparts:
                self.attach(p)
        if boundary:
            self.set_boundary(boundary)


class IMSMIMEMultipartAlternative(IMSMIMEBase):
    def __init__(self, boundary=None, _subparts=None, **_params):
        IMSMIMEBase.__init__(self, 'multipart', 'alternative', **_params)
        self._payload = []

        if _subparts:
            for p in _subparts:
                self.attach(p)
        if boundary:
            self.set_boundary(boundary)


class IMSMessageAttachment:
    encoders = {"base64": encoders.encode_base64, "qp": encoders.encode_quopri,
                "8bit": encoders.encode_7or8bit, "7bit": encoders.encode_7or8bit}

    def __init__(self, file, encoding="base64", charset="utf-8", content_disposition="attachment"):
        """encoding: base64/qp/7bit/8bit
            content_disposition: inline/attachment"""
        self.file = file
        self.encoding = encoding
        try:
            self.encoder = self.encoders[self.encoding]
        except KeyError:
            raise KeyError("unsupported encoder: %s" % encoding)

        self.charset = charset
        if isinstance(charset, basestring):
            self.charset = IMSCharset(charset)
        self.charset.set_header_encoding(self.encoding)

        self.content_disposition = content_disposition

        logger.info("attachment - %s: %s, %s, disposition: %s" % (
            self.filename, self.encoding, self.charset, self.content_disposition))

    @property
    def filename(self):
        return os.path.basename(self.file)

    @property
    def filename_encoded(self):
        return str(Header(self.filename, self.charset))

    def _make_payload(self):
        ctype, encoding = mimetypes.guess_type(self.file)

        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(self.file, 'rb') as f:
            msg = MIMEBase(maintype, subtype, filename=self.filename_encoded)
            msg.set_payload(f.read())
            self.encoder(msg)
            msg.set_unixfrom("X-Creator: Python Scripts")
            return msg

    def make_payload(self):
        entity = self._make_payload()
        entity.add_header('Content-Disposition', self.content_disposition, filename=self.filename_encoded)
        return entity

    def __str__(self):
        return str(self.make_payload())
