import os
import unittest
import tempfile
from message import IMSMessageComposer
from message import IMSMessageParser
from email_resource import email_plain
from email_resource import email_html_attachment


class TestIMSMessageComposer(unittest.TestCase):
    def test_compose_a_plain_email(self):
        c = IMSMessageComposer()
        c.set_subject("test email")
        c.add_plain_body("test email")
        d = IMSMessageParser().message_from_string(str(c))
        self.assertTrue(d.is_equal(IMSMessageParser().message_from_file(email_plain)))

    def test_compose_a_html_email_with_attachment(self):
        c = IMSMessageComposer()
        c.set_subject("plain and html body")
        c.add_plain_body("hello world")
        c.add_html_body("<h1>hello world<h1>")

        attach = os.path.join(tempfile.mkdtemp(), "hello.txt")
        with open(attach, 'w') as f:
            f.write("hello")
        c.append_attachment(attach)
        os.remove(attach)

        d = IMSMessageParser().message_from_string(str(c))
        self.assertTrue(d.is_equal(IMSMessageParser().message_from_file(email_html_attachment)))

    def test_compose_email_based_on(self):
        m = IMSMessageParser(_class=IMSMessageComposer).message_from_file(email_html_attachment)
        m.set_subject("hello 123")

        d = IMSMessageParser().message_from_string(str(m))
        self.assertEqual("hello 123", d.subject)
        self.assertEqual([False, True, True], d.is_equal(IMSMessageParser().message_from_file(email_html_attachment)))


if __name__ == '__main__':
    unittest.main()
