from django.core.mail import EmailMessage
import os
from . import models

from .lib_process_file import upload_file_view

from django.db.models import Max
import json


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


def send_email(filepath, rut, json_data, functions_and_result, _hash="", to_emails: list = [], domain="", t_stamp=None):
    msg = EmailMessage(subject=f"Resultado de verificación LCD",
                       body="",  # 'Body of the email',
                       from_email=None,  # 'from@email.com',
                       to=[*to_emails])

    msg.content_subtype = "html"
    msg.attach_file(filepath)  # 'pdfs/Instructions.pdf')

    str_check = create_report_check_html(json_data)
    msg.attach("reporte.html", str_check)
    msg.body = f"Sr(a). con rut {rut}\n<br>\
    Se adjunta la revisión del Libro de Clases Digital que realizó el día {t_stamp}. \
    También se envía un registro log con la revisión.<br>\
    Puede ver el resultado en el archivo adjunto o haciendo click \
    <a href=http://{domain}/check_result/{_hash}>Aquí</a>\
    \n\n<br><br>Atte\
    \n<br>EDE – MINEDUC<br><br>"
    with open("static/funciones_implementadas.json", "r") as func_list_handler:
        func_list = func_list_handler.read()
        func_list = json.loads(func_list)
    # Create table with functions and result to append in email
    n_aprobado = 0
    n_sdatos = 0
    n_rechazado = 0
    n_noverificado = 0
    table_str = "<table style='border:1px solid black;'><tr>\
    <th style='border:1px solid black;'>Función</th>\
    <th style='border:1px solid black;'>Resultado</th></tr>"
    for x in functions_and_result:
        if x in func_list:
            func_list.remove(x)
        color_style = 'style="background-color:'
        y = functions_and_result[x]
        if y == "Aprobado":
            color_style += 'blue;"'
            n_aprobado += 1
        elif y == "Rechazado":
            color_style += 'red;"'
            n_rechazado += 1
        else:
            color_style += 'gray;"'
            n_sdatos += 1
        table_str += f"<tr {color_style}><td style='border:1px solid black;'>{x}</td>\
        <td style='border:1px solid black;'>{y}</td></tr>"
    print(f"Funciones no verificadas: {func_list}")
    for x in func_list:
        n_noverificado += 1
        table_str += f"<tr style='background-color:orange;'><td style='border:1px solid black;'>{x}</td>\
        <td style='border:1px solid black;'>No Verificado</td></tr>"
    table_str += "</table><br>\n"
    msg.body += f"El resultado de las verificaciones arroja un total de \
        {n_aprobado} Aprobado, {n_rechazado} Rechazado, {n_sdatos} Sin datos y {n_noverificado} No verificados.."
    if n_rechazado == 0 and n_noverificado == 0:
        msg.body += "<br>¡Felicitaciones! Usted cumple todas de las verificaciones.<br>"
    else:
        msg.body += f"<br>Usted cumple con el \
{round((n_aprobado+n_sdatos)/float(n_rechazado+n_sdatos+n_aprobado+n_noverificado)*100.0, 2)}%\
         del total de verificaciones, aún le faltan {n_rechazado} rechazados y {n_noverificado} sin verificar.<br><br>"
    msg.body += table_str
    msg.send()


def send_email_error(e: Exception, body_msg: str, to_emails: list):
    msg = EmailMessage(subject=f"Resultado de verificación LCD [ERROR]",
                       body="",  # 'Body of the email',
                       from_email=None,  # 'from@email.com',
                       to=[*to_emails])

    msg.content_subtype = "html"
    msg.body = "Lo sentimos, ha ocurrido un error,\
     lo revisaremos lo más pronto posible. A continuación el código del error: <br>"
    msg.body = msg.body + "<br>" + body_msg
    msg.body = msg.body + "<br><br>" + str(e) + "<br><br>" + str(e.__traceback__)
    msg.send()


def check_database(idquery, r_cmd, domain, run, rbd, email, t_stamp):
    try:
        print("check reporte")
        cmd = r_cmd.get_check_command()
        print(cmd)
        if r_cmd.cmd == "NO_SE_PUDO_REALIZAR_DESENCRIPTACION":
            raise Exception("Error No se pudo desencriptar el archivo. \
                                     Recuerde usar: parseCSVtoEDE.py insert -e admin@ede.mineduc.cl")
        print("to upload file view")
        try:
            json_dump, functions_and_result = upload_file_view(r_cmd)
        except Exception as e:
            raise Exception(f"Error en la ejecución del comando. {e}") from e
        print("finished")
        if json_dump is None or functions_and_result is None:
            raise Exception("Error en procesamiento del resultado del chequeo")  # 500
        data_file = [f for f in sorted(os.listdir(r_cmd.pathRootDirectory)) if (str(f))[-9:] == "_Data.zip"]
        if len(data_file) > 0:
            print(f"datafile en view: {data_file}")
            print("to write in database")
            try:
                rep = models.Report(
                    id=r_cmd.hash_,
                    rbd=rbd,
                    run=run,
                    reportestr=json_dump,
                    queryid=idquery
                )
                rep.save()
                for x in functions_and_result:
                    max_id = models.ResultReport.objects.aggregate(Max('id'))['id__max']
                    print(max_id)
                    max_id = max_id + 1 if max_id is not None else 0
                    rr = models.ResultReport(
                        id=max_id,
                        report_id=r_cmd.hash_,
                        func_name=x,
                        result=functions_and_result[x]
                    )
                    rr.save()
            except Exception as e:
                raise Exception(f"Error al guardar en la base de datos. {e}") from e
            try:
                send_email(os.path.join(r_cmd.pathRootDirectory, data_file[0]),
                           json_data=json_dump,
                           functions_and_result=functions_and_result,
                           _hash=r_cmd.hash_,
                           to_emails=[email],
                           domain=domain,
                           rut=run,
                           t_stamp=t_stamp)
                print("sended email")
            except Exception as e:
                raise Exception(f"Error enviando el correo electrónico. {e}") from e
        else:
            raise Exception("No hay archivo de resultados")
    except Exception as e:
        send_email_error(e, "", [email])
    r_cmd.delete_folder()
