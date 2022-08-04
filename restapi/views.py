from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from . import models

import re
from datetime import datetime, timedelta
from functools import wraps

from .authentication import token_expire_handler, expires_in
from .serializers import UserSerializer, UserSigninSerializer
# Create your views here.


def login(request):
    if request.method == "GET":
        form = AuthenticationForm()
        return render(request, 'restapi/login.html', {'form': form})
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        signin_serializer = UserSigninSerializer(data={"username": username, "password": password})
        if not signin_serializer.is_valid():
            return HttpResponse(signin_serializer.errors, status=400)
        return HttpResponse(username)

@api_view(["GET"])
def check(request):
    return render(request, 'restapi/form.html')


@api_view(["GET"])
def check_result(request):
    return render(request, 'restapi/check.html', {"tojson": {}, "folder": "", "file": ""})


@api_view(["GET"])
def rbd(request):
    return HttpResponse("Hello, world.")


@api_view(["GET"])
def rbds(request):
    return HttpResponse("Hello, world.")


@api_view(["GET"])
def report(request):
    return HttpResponse("Hello, world.")


@api_view(["POST"])
def upload(request):
    file = request.POST.get("file", None)
    run = request.POST.get("run", None)
    otp = request.POST.get("otp", None)
    rbd = request.POST.get("rbd", None)
    if not (file is None and run is None and otp is None and rbd is None):
        print(file)
        print(run)
        print(otp)
        print(rbd)



@api_view(["POST"])
@permission_classes((AllowAny,))
def signin(request):
    signin_serializer = UserSigninSerializer(data=request.data)
    if not signin_serializer.is_valid():
        return HttpResponse(signin_serializer.errors, status=400)

    user = authenticate(
        username=signin_serializer.data['username'],
        password=signin_serializer.data['password']
    )
    # if not user:
    #    return HttpResponse({'detail': 'Invalid Credentials or activate account'}, status=404)

    # TOKEN STUFF
    token, _ = Token.objects.get_or_create(user=user)

    # token_expire_handler will check, if the token is expired it will generate new one
    is_expired, token = token_expire_handler(token)  # The implementation will be described further
    user_serialized = UserSerializer(user)

    return JsonResponse({
        'user': user_serialized.data,
        'expires_in': expires_in(token),
        'token': token.key
    }, status=200)


@api_view(["GET"])
def user_info(request):
    return HttpResponse("Hello, world.")
