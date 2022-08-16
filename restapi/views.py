import json
import os

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
from .tasks import check_database

from .process_file import upload_file_view
from django.conf import settings
# Create your views here.


import threading


@api_view(["GET"])
def check(request):
    return render(request, 'restapi/form.html')


@api_view(["GET"])
def check_result(request, report_id):
    rr = models.Report.objects.get(id=report_id)
    rjson = rr.reportestr.replace("\u0022", "'")
    # print(rjson)
    return render(request, 'restapi/check.html', {"tojson": rjson, "folder": "", "file": ""})


def success_view(request):
    return HttpResponse("Se enviará el resultado a su correo electrónico", status=200)

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
        is_valid = otp_model.login_otp(run, otp)
        query_rbd = models.QuerysRbds(id=None,
                                      filename=file.name,
                                      run=run,
                                      otp=otp,
                                      otp_is_valid=is_valid,
                                      rbd=rbd)
        query_rbd.save()
        print(f"to delay, is valid: {is_valid}")
        r_cmd = otp_model.RouteCommand()  # set session
        if not r_cmd.validarFormulario(file, run, otp, rbd):
            print("error al validar el formulario")
            return HttpResponse({"error": "Error al validar el formulario"})  # Check form data
        print("a init enviroment")
        r_cmd.init_enviroment()  # Crea ambiente de trabajo
        print("a extraer")
        r_cmd.extractAll(r_cmd.file)  # extract file from form
        if not otp_model.login_otp(run, otp):
            return HttpResponse({"error":
                                  "El 'verificador de identidad' ingresado no es correcto!"})  # Chequea verificador de Identidad del form
        print("a firmar reporte")
        r_cmd.firmar_reporte()  # Genera la firma del reporte

        t = threading.Thread(target=check_database, args=(r_cmd, run, otp, rbd))
        t.start()
        #check_database.delay(query_rbd.id, run, otp, rbd)
        print("delayed")
        return redirect(f"success/")
    else:
        return JsonResponse({"error":"Faltan campos en el formulario"}, status=404)

