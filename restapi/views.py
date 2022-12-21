

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from . import models
from .lib_route_command import RouteCommand
from .lib_login_otp import login_otp
from .tasks_check_database import check_database
from .tasks import q

from django.db.models import Max

# Create your views here.


import threading


@api_view(["GET"])
def check(request):
    return render(request, 'restapi/form.html')


@api_view(["GET"])
def check_result(request, report_id):
    try:
        rr = models.Report.objects.get(id=report_id)
        rjson = rr.reportestr.replace("\u0022", "'")
        return render(request, 'restapi/check.html', {"tojson": rjson, "folder": "", "file": ""})
    except Exception as e:
        return JsonResponse({"error": f"Ocurrió un error al procesar la solicitud. {e}"})


def success_view(request):
    return render(request, 'restapi/success.html')
    # return HttpResponse("Se enviará el resultado a su correo electrónico", status=200)


@api_view(["POST"])
def upload(request):
    file = request.FILES.get("file", None)
    run = request.POST.get("run", None)
    otp = request.POST.get("otp", None)
    rbd = request.POST.get("rbd", None)
    email = request.POST.get("email", None)
    if not (file is None or run is None or otp is None or rbd is None or email is None):
        print(file)
        print(run)
        print(otp)
        print(rbd)
        print(email)
        is_valid = login_otp(run, otp)
        try:
            max_id = models.QuerysRbds.objects.aggregate(Max('id'))['id__max']
            print(max_id)
            max_id = max_id+1 if max_id is not None else 0
            filename = file.name
            if len(filename) > 40:
                filename = filename[:40]
            query_rbd = models.QuerysRbds(id=max_id,
                                          filename=filename,
                                          run=run,
                                          otp=otp,
                                          otp_is_valid=is_valid,
                                          rbd=rbd,
                                          email=email)
            query_rbd.save()
        except Exception as e:
            return JsonResponse({"error": f"Error en almacenar en la base de datos la petición. {e}"})
        print(f"to delay, is valid: {is_valid}")
        r_cmd = RouteCommand()  # set session
        if not r_cmd.validar_formulario(file, run, otp, rbd):
            print("error al validar el formulario")
            return JsonResponse({"error": "Error al validar el formulario"})  # Check form data
        print("a init enviroment")
        r_cmd.init_enviroment()  # Crea ambiente de trabajo
        print("a extraer")
        try:
            r_cmd.extract_all(r_cmd.file)  # extract file from form
        except Exception as e:
            return JsonResponse({"error": f"Error al descomprimir el archivo. {e}"})
        if not is_valid:  # Chequea verificador de Identidad del form
            return JsonResponse({"error": "El 'verificador de identidad' ingresado no es correcto!"})
        print("a firmar reporte")
        r_cmd.firmar_reporte()  # Genera la firma del reporte
        domain = request.get_host()
        # domain = 'localhost:8000'
        print(domain)

        t = threading.Thread(target=check_database, args=(query_rbd.id, r_cmd, domain, run, rbd, email, query_rbd.t_stamp))
        q.put(t)
        print("delayed")
        return redirect(f"success/")
    else:
        return JsonResponse({"error": "Faltan campos en el formulario"}, status=404)
