import requests
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User
from .authentication import JWTAuthentication
from .serializers import UserSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data
        data['is_ambassador'] = 'api/ambassador' in request.path

        response = requests.post(
            'http://host.docker.internal:8001/api/register', data)

        return Response(response.json())


class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        data['scope'] = 'ambassador' if 'api/ambassador' in request.path else 'admin'

        resp = requests.post(
            'http://host.docker.internal:8001/api/login', data).json()

        response = Response()
        response.set_cookie(key='jwt', value=resp['jwt'], httponly=True)
        response.data = {
            'message': 'success'
        }

        return response


class UserAPIView(APIView):

    def get(self, request):
        # if 'api/ambassador' in request.path:
        #     data['revenue'] = user.revenue

        response = requests.get(
            'http://host.docker.internal:8001/api/user', headers=request.headers).json()

        return Response(response)


class LogoutAPIView(APIView):

    def post(self, _):
        requests.post(
            'http://host.docker.internal:8001/api/logout', []).json()

        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }
        return response


class ProfileInfoAPIView(APIView):

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfilePasswordAPIView(APIView):

    def put(self, request, pk=None):
        user = request.user
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        user.set_password(data['password'])
        user.save()
        return Response(UserSerializer(user).data)
