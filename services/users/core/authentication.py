import jwt
import datetime
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from config import settings
from .models import User, UserToken


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        is_ambassador = 'api/ambassador' in request.path

        token = request.COOKIES.get('jwt')

        if not token:
            return None

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Unauthenticated')

        if (is_ambassador and payload['scope'] != 'ambassador') or (not is_ambassador and payload['scope'] != 'admin'):
            raise exceptions.AuthenticationFailed('Invalid Scope!')

        user = User.objects.get(pk=payload['user_id'])

        if user is None:
            raise exceptions.AuthenticationFailed('User Not Found!')

        if not UserToken.objects.filter(
                user_id=user.id,
                token=token,
                expired_at__gt=datetime.datetime.now()
        ).exists():
            raise exceptions.AuthenticationFailed('Invalid Token!')

        return (user, None)

    @staticmethod
    def generate_jwt(id, scope):
        payload = {
            'user_id': id,
            'scope': scope,
            'exp': datetime.datetime.now() + datetime.timedelta(days=1),
            'iat': datetime.datetime.now()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
