from django.core.mail import EmailMessage
import os
from . import models

from .lib_process_file import upload_file_view

from django.db.models import Max


def create_report_check_html(json_data):
    with open("static/check.html", "r") as check_handler:
        str_check = check_handler.read()
    with open("static/js/d3.v4.js", "r") as d3h:
        strkd3 = d3h.read()
    with open("static/css/style.css", "r") as cssh:
        strcss = cssh.read()
    str_check = str_check.replace("asdf_toreplace_replacing", str(json_data))
    str_check = str_check.replace("toreplace_d3_toreplace", str(strkd3))
    str_check = str_check.replace("toreplace_css_toreplace", str(strcss))
    return str_check


def send_email(filepath, rut, data = {}, _hash="", to_emails: list = [], domain=""):
    msg = EmailMessage(subject=f"Resultado de verificación LCD",
                       body="",  # 'Body of the email',
                       from_email=None,  # 'from@email.com',
                       to=[*to_emails])

    msg.content_subtype = "html"
    msg.attach_file(filepath)  # 'pdfs/Instructions.pdf')

    str_check = create_report_check_html(data)
    msg.attach("reporte.html", str_check)
    msg.body = f"Sr(a). rut no {rut}\n<br>\
    Se adjunta la revisión del Libro de Clases Digital que realizó el día (día de la subida del archivo). \
    También se envía un registro log con la revisión.<br>\
    Puede ver el resultado en el archivo adjunto o la dirección: \
    <a href=http://{domain}/check_result/{_hash}>http://{domain}/check_result/{_hash}</a>\
    \n\n<br><br>Atte\
    \n<br>EDE – MINEDUC<br><br>"
    msg.send()


def send_email_error(e: Exception, body_msg: str, to_emails: list):
    msg = EmailMessage(subject=f"Resultado de verificación LCD [ERROR]",
                       body="",  # 'Body of the email',
                       from_email=None,  # 'from@email.com',
                       to=[*to_emails, "admin@ede.mineduc.cl"])

    msg.content_subtype = "html"
    msg.body = "Lo sentimos, ha ocurrido un error,\
     lo revisaremos lo más pronto posible. A continuación el código del error: <br>"
    msg.body = msg.body + "<br>" + body_msg + "<br><br>" + str(e) + "<br><br>" + str(e.__traceback__)
    msg.send()


def check_database(idquery, r_cmd, domain, run, rbd, email):
    try:
        print("check reporte")
        cmd = r_cmd.getCheckCommand()
        print(cmd)
        if r_cmd.cmd == "NO_SE_PUDO_REALIZAR_DESENCRIPTACION":
            raise Exception({"error":
                                     u"No se pudo desencriptar el archivo. \
                                     Recuerde usar: parseCSVtoEDE.py insert -e admin@ede.mineduc.cl"})
        print("to upload file view")
        json_dump, functions_and_result = upload_file_view(r_cmd)
        print("finished")
        if json_dump is None or functions_and_result is None:
            raise Exception("Error en procesamiento del resultado del chequeo")  # 500
        data_file = [f for f in sorted(os.listdir(r_cmd.pathRootDirectory)) if (str(f))[-9:] == "_Data.zip"]
        if len(data_file) > 0:
            print(f"datafile en view: {data_file}")
            send_email(os.path.join(r_cmd.pathRootDirectory, data_file[0]),
                       data=json_dump,
                       _hash=r_cmd.hash_,
                       to_emails=[email],
                       domain=domain,
                       rut=run)
            print("sended email")
        else:
            raise Exception("No hay archivo de resultados")
        rep = models.Report(
            id=r_cmd.hash_,
            rbd=rbd,
            run=run,
            reportestr=json_dump,
            queryid=idquery
        )
        rep.save()
        for x, y in functions_and_result:
            max_id = models.ResultReport.objects.aggregate(Max('id'))['id__max']
            print(max_id)
            max_id = max_id + 1 if max_id is not None else 0
            rr = models.ResultReport(
                id=max_id,
                report_id=r_cmd.hash_,
                func_name=x,
                result=y
            )
            rr.save()
    except Exception as e:
        send_email_error(e, "", [email])
