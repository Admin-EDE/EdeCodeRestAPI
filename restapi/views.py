import json

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from . import models
from . import otp_model


from .process_file import upload_file_view
from django.conf import settings
# Create your views here.


@api_view(["GET"])
def check(request):
    return render(request, 'restapi/form.html')


@api_view(["GET"])
def check_result(request, report_id):
    rr = models.Report.objects.get(id=report_id)
    rjson = rr.reportestr.replace("\u0022", "'")
    # print(rjson)
    return render(request, 'restapi/check.html', {"tojson": rjson, "folder": "", "file": ""})


@api_view(["POST"])
def upload(request):
    file = request.FILES.get("file", None)
    run = request.POST.get("run", None)
    otp = request.POST.get("otp", None)
    rbd = request.POST.get("rbd", None)
    if not (file is None and run is None and otp is None and rbd is None):
        print(file)
        print(run)
        print(otp)
        print(rbd)
        query_rbd = models.QuerysRbds(filename=file.name, run=run, otp=otp, rbd=rbd)
        query_rbd.save()
        r_cmd = otp_model.RouteCommand()  # set session
        print("a validar formulario")
        if not r_cmd.validarFormulario(file, run, otp, rbd):
            print("error al validar el formulario")
            raise Http404("Error al validar el formulario")  # Check form data
        print("a init enviroment")
        r_cmd.init_enviroment()  # Crea ambiente de trabajo
        print("a extraer")
        r_cmd.extractAll(r_cmd.file)  # extract file from form
        if not otp_model.login_otp(run, otp):
            return Http404(
                "El 'verificador de identidad' ingresado no es correcto!")  # Chequea verificador de Identidad del form
        print("a firmar reporte")
        r_cmd.firmar_reporte()  # Genera la firma del reporte
        print("check reporte")
        cmd = r_cmd.getCheckCommand()
        print(cmd)
        if r_cmd.cmd == "NO_SE_PUDO_REALIZAR_DESENCRIPTACION":
            return Http404(
                u"No se pudo desencriptar el archivo. Recuerde usar: parseCSVtoEDE.py insert -e admin@ede.mineduc.cl")
        print("to upload file view")
        json_dump, functions_and_result = upload_file_view(r_cmd)
        print("finished")
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

        return redirect(f"check_result/{r_cmd.hash_}")
    else:
        return Http404("Faltan campos en el formulario")

