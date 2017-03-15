import dkim

dkim.my_dns_server = None


# will overwrite old one in dkim
def dnstxt(name):
    """Return a TXT record associated with a DNS name."""
    import dns.resolver

    ### Start - add by abner
    my_resolver = dns.resolver.Resolver()
    if getattr(dkim, 'my_dns_server', None):
        my_resolver.nameservers = [dkim.my_dns_server, ]
    a = my_resolver.query(name, dns.rdatatype.TXT)
    ### End - add by abner

    # original code
    # a = dns.resolver.query(name, dns.rdatatype.TXT)
    for r in a.response.answer:
        if r.rdtype == dns.rdatatype.TXT:
            return "".join(r.items[0].strings)
    return None


dkim.dnstxt = dnstxt