from django.core.mail import EmailMessage
import os
from . import models
from . import otp_model

from .process_file import upload_file_view
from celery import shared_task
from celery.utils.log import get_logger
import logging


logger = logging.getLogger(__name__)


def send_email(filepath, to_emails: list = []):
    msg = EmailMessage(subject='Subject of the Email',
                       body='Body of the email',
                       from_email = None, #'from@email.com',
                       to =['erick.merino@mineduc.cl', *to_emails])

     # fail_silently = False )
    # Set this to False so that you will be noticed in any exception raised)

    msg.content_subtype = "html"
    msg.attach_file(filepath)#'pdfs/Instructions.pdf')
    msg.send()


logger.info("*-*"*40)


#@shared_task()
def check_database(r_cmd, run, otp, rbd):
    #print("print enter the check func")
    #print(fileid)
    #logger.info("enter the check function")
    #file = models.QuerysRbds.objects.filter(id=fileid).values("tmpfile")
    #logger.info(dir(file))
    #file  = models.models.FileField(file)
    #print(type(file))
    #print(file)
    #file  = file
    #logger.info(file)

    print("check reporte")
    cmd = r_cmd.getCheckCommand()
    print(cmd)
    if r_cmd.cmd == "NO_SE_PUDO_REALIZAR_DESENCRIPTACION":
        return Exception({"error":
                                 u"No se pudo desencriptar el archivo. Recuerde usar: parseCSVtoEDE.py insert -e admin@ede.mineduc.cl"}
                        )
    print("to upload file view")
    json_dump, functions_and_result = upload_file_view(r_cmd)
    print("finished")
    if json_dump is None or functions_and_result is None:
        return Exception({"error": "Error en procesamiento del resultado del chequeo"}) #500
    dataFile = [f for f in sorted(os.listdir(r_cmd.pathRootDirectory)) if (str(f))[-9:] == "_Data.zip"]
    if len(dataFile) > 0:
        print(f"datafile en view: {dataFile}")
        send_email(os.path.join(r_cmd.pathRootDirectory, dataFile[0]))
        print("sended email")
    rep = models.Report(
        id=r_cmd.hash_,
        rbd=rbd,
        run=run,
        reportestr=json_dump
    )
    rep.save()
    for x, y in functions_and_result:
        rr = models.ResultReport(
            report_id=r_cmd.hash_,
            func_name=x,
            result=y
        )
        rr.save()