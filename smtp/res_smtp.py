import smtplib
import collections


class ResSMTP(smtplib.SMTP):
    def __init__(self, *args):
        smtplib.SMTP.__init__(self, *args)
        self.results = collections.OrderedDict()

    def connect(self, host='localhost', port=0):
        self.results['connect_args'] = "%s:%s" % (host, port)
        self.results['connect_response'] = smtplib.SMTP.connect(self, host, port)

    def starttls(self, keyfile=None, certfile=None):
        self.results['starttls_args'] = (keyfile, certfile)
        try:
            self.results['starttls_response'] = smtplib.SMTP.starttls(self, keyfile, certfile)
        except smtplib.SMTPResponseException, err:
            self.results['starttls_response'] = err.args
            raise
        else:
            return self.results['starttls_response']

    def helo(self, name=''):
        self.results['helo_args'] = name
        self.results['helo_response'] = smtplib.SMTP.helo(self, name)
        return self.results['helo_response']

    def ehlo(self, name=''):
        self.results['ehlo_args'] = name
        self.results['ehlo_response'] = smtplib.SMTP.ehlo(self, name)
        return self.results['ehlo_response']

    def mail(self, sender, options=[]):
        self.results['mail_args'] = sender
        self.results['mail_response'] = smtplib.SMTP.mail(self, sender, options)
        return self.results['mail_response']

    def rcpt(self, recip, options=[]):
        if not self.results.get('rcpt_args', None):
            self.results['rcpt_args'] = []
            self.results['rcpt_response'] = []
        self.results['rcpt_args'].append(recip)
        self.results['rcpt_response'].append(smtplib.SMTP.rcpt(self, recip, options))
        return self.results['rcpt_response'][-1]

    def data(self, msg):
        self.results['data_args'] = msg if len(msg) < 100 else "contains %d chars" % len(msg)
        self.results['data_response'] = smtplib.SMTP.data(self, msg)
        return self.results['data_response']

    def quit(self):
        self.results['quit_response'] = smtplib.SMTP.quit(self)
        return self.results['quit_response']
