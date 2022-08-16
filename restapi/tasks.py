from django.core.mail import EmailMessage


def send_email(filepath):
    msg = EmailMessage('Subject of the Email', 'Body of the email', 'from@email.com', ['erick.merino@mineduc.cl'])
    msg.content_subtype = "html"
    msg.attach_file(filepath)#'pdfs/Instructions.pdf')
    msg.send()



