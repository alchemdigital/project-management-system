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
        print('email run method')
        from_email = 'alchemsmtp@gmail.com'
        text_content = self.html_content
        html_content = self.html_content
        msg = EmailMultiAlternatives('New Alchem Digital Lead', text_content, from_email, self.recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()