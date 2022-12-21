from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from django.contrib.auth.forms import AuthenticationForm


from datetime import datetime, timedelta

from django.conf import settings
import jwt

from rest_framework.decorators import api_view

from . import models
from .lib_login_otp import login_otp
from .serializers import UserSigninSerializer

from .auth_token import token_required


def login_view(request):
    if request.method == "GET":
        form = AuthenticationForm()
        return render(request, 'restapi/login.html', {'form': form})
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        signin_serializer = UserSigninSerializer(data={"username": username, "password": password})
        if not signin_serializer.is_valid():
            return HttpResponse(signin_serializer.errors, status=400)
        print(f"Resultado otp: {login_otp(username, password)}")
        if login_otp(username, password):
            max_id = models.User.objects.aggregate(models.models.Max('id'))['id__max']
            max_id = max_id + 1 if max_id is not None else 0
            user = models.User(id=max_id,username=username)
            user.save()
            # create token
            token = jwt.encode(payload={
                'user': username,
                'exp': datetime.utcnow() + timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS)},
                key=settings.SECRET_KEY,
                algorithm="HS512")
            print(str(token))
            # remove b' .... ' with slicing token string
            return JsonResponse({'token': token}, status=200)


@api_view(["GET"])
@token_required
def users(request):
    users_: models.models.QuerySet = models.User.objects.values('username').distinct()
    return JsonResponse({"users": list(users_.all())})


@api_view(["GET"])
@token_required
def rbd(request, rbd_id: int):
    rr = models.Report.objects.filter(rbd=rbd_id)
    rr = rr.values().all()
    return JsonResponse({"rbd": list(rr)})


@api_view(["GET"])
@token_required
def rbd_query(request, rbd_id: int):
    rr = models.QuerysRbds.objects.filter(rbd=rbd_id)
    rr = rr.values().all()
    return JsonResponse({"rbd": list(rr)})


@api_view(["GET"])
@token_required
def rbds(request):
    rbds_ = models.Report.objects.values('rbd').distinct()
    return JsonResponse({"rbds": list(rbds_.all())})


@api_view(["GET"])
@token_required
def rbds_query(request):
    rbds_ = models.QuerysRbds.objects.values('rbd').distinct()
    return JsonResponse({"rbds": list(rbds_.all())})


@api_view(["GET"])
@token_required
def report(request, report_id: str):
    rr = models.ResultReport.objects.filter(report_id=report_id)
    rr = rr.values().all()
    response = {}
    for res in rr:
        response[res['func_name']] = res['result']
    return JsonResponse(response)
