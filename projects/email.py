import threading
from threading import Thread
from django.core.mail import EmailMultiAlternatives

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run (self):
        from_email = 'pms@alchemdigital.com'
        text_content = self.html_content
        html_content = self.html_content
        msg = EmailMultiAlternatives('Registered with PMS', text_content, from_email, self.recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()