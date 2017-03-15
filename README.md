# email_utils
enhance email parser/SMTP/POP3

# 1. email parser
add attributes and match functions to Message:
 - subject
 - body_plain
 - body_html
 - attachments
 - is_header_value_contain
 - is_plain_body_contain
 - is_html_body_contain
 - is_contain_attachment
 - is_attachment_contain
 - is_equal

Usage:
```
message_from_file = IMSMessageParser().message_from_file(email_file)
message_from_string = IMSMessageParser().message_from_string(email_string)
```

# 2. SMTP
support to collect SMTP response code and description after each SMTP command

# 3. POP3
support SSL connection to POP3 server via HTTP proxy
