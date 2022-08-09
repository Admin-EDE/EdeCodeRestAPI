from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from django.contrib.auth.forms import AuthenticationForm


from datetime import datetime, timedelta

from django.conf import settings
import jwt

from rest_framework.decorators import api_view

from . import models
from . import otp_model
from .serializers import UserSigninSerializer
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(args)
        print(kwargs)
        token = args[0].GET.get('token', None) #http://localhost/rbd/1-9?token=alshfjfjdklsfj89549834ur
        if not token:
            return JsonResponse({'message' : 'Token is missing!'})
        try:
            data = jwt.decode(token, settings.SECRET_KEY, algorithms="HS512")
        except Exception as e:
            return JsonResponse({'message' : 'Token is invalid!'})
        return f(*args, **kwargs)
    return decorated


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
        print(f"Resultado otp: {otp_model.login_otp(username, password)}")
        if otp_model.login_otp(username, password):
            user = models.User(username=username)
            user.save()
            # create token
            token = jwt.encode({
                'user': username,
                'exp': datetime.utcnow() + timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS)},
                settings.SECRET_KEY,
                algorithm="HS512")
            print(token)
            # remove b' .... ' with slicing token string
            return JsonResponse({'token': str(token)[2:-1]}, status=200)


@api_view(["GET"])
@token_required
def users(request):
    users_: models.models.QuerySet = models.User.objects.values('username').distinct()
    print(list(users_.all()))
    return JsonResponse({"users": list(users_.all())})


@api_view(["GET"])
@token_required
def rbd(request, rbd_id: int):
    rr = models.Report.objects.filter(rbd=rbd_id)
    rr = rr.values().all()
    return JsonResponse({"rbd":list(rr)})


@api_view(["GET"])
@token_required
def rbds(request):
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


