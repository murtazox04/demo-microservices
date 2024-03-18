from rest_framework.response import Response
from rest_framework.views import APIView

from .services import UserService


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data
        data['is_ambassador'] = 'api/ambassador' in request.path

        return Response(UserService.post('/register', data=data))


class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        data['scope'] = 'ambassador' if 'api/ambassador' in request.path else 'admin'

        resp = UserService.post('/login', data=data)

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

        return Response(request.user_ms)


class LogoutAPIView(APIView):

    def post(self, request):
        UserService.post('/logout', headers=request.headers)

        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }
        return response


class ProfileInfoAPIView(APIView):

    def put(self, request, pk=None):
        return Response(UserService.put('/users/info', data=request.data))


class ProfilePasswordAPIView(APIView):

    def put(self, request, pk=None):
        return Response(UserService.put('/users/password', data=request.data))
