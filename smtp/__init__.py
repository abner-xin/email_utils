from .res_smtp import ResSMTP


def sendmail(server, port, sender, recipients, email, starttls=None, key=None, cert=None):
    if isinstance(port, basestring):
        port = int(port)

    if isinstance(recipients, basestring):
        recipients = recipients.split(';')

    s = ResSMTP()
    s.connect(server, port)
    if starttls:
        s.starttls(key, cert)
    s.sendmail(sender, recipients, email)
    s.quit()

    print "email is sent OK"
    return s
