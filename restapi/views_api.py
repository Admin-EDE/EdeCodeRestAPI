from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from . import models


@api_view(["GET"])
def users(request):
    users_: models.models.QuerySet = models.User.objects.values('username').distinct()
    print(list(users_.all()))
    return JsonResponse({"users": list(users_.all())})


@api_view(["GET"])
def rbd(request):
    return HttpResponse("Hello, world.")


@api_view(["GET"])
def rbds(request):
    rbds_ = models.QuerysRbds.objects.values('rbd').distinct()
    return JsonResponse({"rbds": list(rbds_.all())})


@api_view(["GET"])
def report(request):
    return HttpResponse("Hello, world.")




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