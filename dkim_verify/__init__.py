from dkim_lib import dkim
"""
you can specify DNS server which holds TXT record for DKIM domain when do DKIM verification:

dkim.my_dns_server("you dns server")

with StringIO.StringIO() as fp:
    res = dkim.verify(open("email file", 'r').read(), debuglog=fp)
    fp.seek(0)
    print fp.read()
"""