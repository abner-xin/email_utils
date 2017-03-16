import os
import tempfile
import unittest
from message import IMSMessageParser
from message import IMSMessage


plain_email="""Date: Wed, 09 Nov 2016 13:21:59 +0800
From: Sender <sender@test.com>
To: rcpt@test.com
Message-ID: <20170316-001@test.com>
Subject: test email

test email
"""


email_html_attachment="""Date: Thu, 16 Mar 2017 16:13:19 +0800
From: test <test@test.com>
To: test <test@qq.com>
Subject: plain and html body
Mime-Version: 1.0
Message-ID: <201703161613194387643@xinj.com>
Content-Type: multipart/mixed;
	boundary="----=_001_NextPart630834548414_=----"

This is a multi-part message in MIME format.

------=_001_NextPart630834548414_=----
Content-Type: multipart/alternative;
	boundary="----=_002_NextPart644813647362_=----"


------=_002_NextPart644813647362_=----
Content-Type: text/plain;
	charset="us-ascii"
Content-Transfer-Encoding: base64

aGVsbG8gd29ybGQNCg0KDQoNCg0KeGluIHZpYSBmb3htYWls

------=_002_NextPart644813647362_=----
Content-Type: text/html;
	charset="us-ascii"
Content-Transfer-Encoding: quoted-printable

<h1>hello world<h1>

------=_002_NextPart644813647362_=------

------=_001_NextPart630834548414_=----
Content-Type: application/octet-stream;
	name="hello.txt"
Content-Transfer-Encoding: base64
Content-Disposition: attachment;
	filename="hello.txt"

aGVsbG8=

------=_001_NextPart630834548414_=------
"""

class TestIMSMessageParser(unittest.TestCase):
    def setUp(self):
        self.email_file = tempfile.mktemp()
        with open(self.email_file, 'w') as f:
            f.write(plain_email)

    def tearDown(self):
        if os.access(self.email_file, os.R_OK):
            os.remove(self.email_file)

    def test_message_from_string(self):
        m = IMSMessageParser().message_from_string(plain_email)
        self.assertIsInstance(m, IMSMessage)

    def test_message_from_file(self):
        m = IMSMessageParser().message_from_file(self.email_file)
        self.assertIsInstance(m, IMSMessage)


class TestIMSMessage(unittest.TestCase):
    def test_parse_plain_mail(self):
        m = IMSMessageParser().message_from_string(plain_email)
        self.assertEqual('<20170316-001@test.com>', m.messageId)
        self.assertEqual('rcpt@test.com', m.get_header_value('To'))
        self.assertEqual('Sender <sender@test.com>', m.get_header_value('From'))
        self.assertEqual('test email', m.subject)
        self.assertIn('test email', m.body_plain)
        self.assertIsNone(m.body_html)

    def test_parse_email_with_html_body_and_attachment(self):
        m = IMSMessageParser().message_from_string(email_html_attachment)
        self.assertEqual('plain and html body', m.subject)
        self.assertIn('hello world', m.body_plain)
        self.assertIn('<h1>hello world<h1>', m.body_html)
        self.assertDictEqual({'hello.txt': "hello"}, m.attachments)



if __name__ == '__main__':
    unittest.main()