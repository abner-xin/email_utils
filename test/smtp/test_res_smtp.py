import time
import socket
import unittest
import collections
import multiprocessing
from smtp import ResSMTP
from smtpd import SMTPServer


class MockSMTPServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, message_data):
        self.log_info("message come from: %s" % str(peer))
        self.log_info("message from: %s" % mailfrom)
        self.log_info("message rcpt: %s" % str(rcpttos))
        self.log_info("message length: %s" % len(message_data))
        self.log_info("message data length: %s" % len(message_data))


def start_mock_mail_server():
    import asyncore
    MockSMTPServer(('0.0.0.0', 25), None)
    asyncore.loop()


class TestResSMTP(unittest.TestCase):
    def setUp(self):
        self.smtpd_host = '127.0.0.1'
        self.smtpd_port = 25
        self.sender = "sender@test.com"
        self.rcpt = "rcpt@test.com"
        self.rcpts = "rcpt01@test.com;rcpt02@test.com"
        self.email = "test email"
        self.mock_smtpd = multiprocessing.Process(target=start_mock_mail_server)
        self.mock_smtpd.start()
        time.sleep(1)  # wait for mail server to start

    def tearDown(self):
        if self.mock_smtpd:
            self.mock_smtpd.terminate()
            self.mock_smtpd.join()

    def test_send_email_ok(self):
        s = ResSMTP()
        s.connect(self.smtpd_host, self.smtpd_port)
        s.sendmail(self.sender, self.rcpt, self.email)
        s.quit()

        self.assertIsInstance(s.results, collections.OrderedDict)
        self.assertDictContainsSubset({'connect_args': '%s:%s' % (self.smtpd_host, self.smtpd_port)}, s.results)
        self.assertEqual(220, s.results['connect_response'][0])
        self.assertIn(socket.getfqdn(), s.results['connect_response'][1])

        self.assertDictContainsSubset({'helo_args': '',
                                       'helo_response': (250, socket.getfqdn())}, s.results)
        self.assertDictContainsSubset({'mail_args': self.sender,
                                       'mail_response': (250, 'Ok')}, s.results)
        self.assertDictContainsSubset({'rcpt_args': [self.rcpt, ],
                                       'rcpt_response': [(250, 'Ok'), ]}, s.results)
        self.assertDictContainsSubset({'data_args': self.email,
                                       'data_response': (250, 'Ok')}, s.results)
        self.assertDictContainsSubset({'quit_response': (221, 'Bye')}, s.results)

    def test_send_email_to_rcpts(self):
        rcpts = self.rcpts.split(';')
        s = ResSMTP()
        s.connect(self.smtpd_host, self.smtpd_port)
        s.sendmail(self.sender, rcpts, self.email)
        s.quit()

        self.assertDictContainsSubset({'rcpt_args': list(rcpts),
                                       'rcpt_response': [(250, 'Ok'), ]*len(rcpts)}, s.results)


if __name__ == '__main__':
    unittest.main()
