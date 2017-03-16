import os


email_path = os.path.dirname(os.path.abspath(__file__))
email_plain = os.path.join(email_path, "email_plain.eml")
email_html_attachment = os.path.join(email_path, "email_html_attachment.eml")