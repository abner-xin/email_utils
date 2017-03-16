import os
import tempfile
import unittest
from message import IMSMessageParser
from message import IMSMessage


email_path = os.path.dirname(os.path.abspath(__file__))
email_plain = os.path.join(email_path, "email_plain.eml")
email_html_attachment = os.path.join(email_path, "email_html_attachment.eml")


class TestIMSMessageParser(unittest.TestCase):

    def test_message_from_string(self):
        with open(email_plain, 'r') as f:
            m = IMSMessageParser().message_from_string(f.read())
        self.assertIsInstance(m, IMSMessage)

    def test_message_from_file(self):
        m = IMSMessageParser().message_from_file(email_plain)
        self.assertIsInstance(m, IMSMessage)


class TestIMSMessage(unittest.TestCase):
    def test_parse_plain_mail(self):
        m = IMSMessageParser().message_from_file(email_plain)
        self.assertEqual('<20170316-001@test.com>', m.messageId)
        self.assertEqual('rcpt@test.com', m.get_header_value('To'))
        self.assertEqual('Sender <sender@test.com>', m.get_header_value('From'))
        self.assertEqual('test email', m.subject)
        self.assertIn('test email', m.body_plain)
        self.assertIsNone(m.body_html)

    def test_parse_email_with_html_body_and_attachment(self):
        m = IMSMessageParser().message_from_file(email_html_attachment)
        self.assertEqual('plain and html body', m.subject)
        self.assertIn('hello world', m.body_plain)
        self.assertIn('<h1>hello world<h1>', m.body_html)
        self.assertDictEqual({'hello.txt': "hello"}, m.attachments)


if __name__ == '__main__':
    unittest.main()