import unittest
from message import IMSMessageParser
from message import IMSMessage
from email_resource import email_plain
from email_resource import email_html_attachment



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

        self.assertTrue(m.is_header_value_contain("From", "sender@test.com"))
        self.assertTrue(m.is_plain_body_contain("test email"))

    def test_parse_email_with_html_body_and_attachment(self):
        m = IMSMessageParser().message_from_file(email_html_attachment)
        self.assertEqual('plain and html body', m.subject)
        self.assertIn('hello world', m.body_plain)
        self.assertIn('<h1>hello world<h1>', m.body_html)
        self.assertDictEqual({'hello.txt': "hello"}, m.attachments)

        self.assertTrue(m.is_html_body_contain("<h1>hello world<h1>"))
        self.assertTrue(m.is_contain_attachment("hello.txt"))
        self.assertFalse(m.is_contain_attachment("hello01.txt"))
        self.assertTrue(m.is_attachment_contain("hello.txt", "hello"))


if __name__ == '__main__':
    unittest.main()