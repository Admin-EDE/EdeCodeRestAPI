import jwt
from django.http import JsonResponse
from django.conf import settings
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(args)
        print(kwargs)
        token = args[0].GET.get('token', None)  # http://localhost/rbd/1-9?token=alshfjfjdklsfj89549834ur
        if not token:
            return JsonResponse({'message': 'Token is missing!'})
        try:
            data = jwt.decode(token, settings.SECRET_KEY, algorithms="HS512")
        except Exception as e:
            return JsonResponse({'message': 'Token is invalid!'})
        return f(*args, **kwargs)
    return decorated
