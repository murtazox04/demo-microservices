from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from core.models import User
from .serializers import UserSerializer
from .authentication import JWTAuthentication


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['confirm_password']:
            raise exceptions.ValidationError('Passwords do not match')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        scope = request.data['scope']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrect password!')

        if user.is_ambassador and scope == 'admin':
            raise exceptions.AuthenticationFailed('Unauthorized')

        token = JWTAuthentication.generate_jwt(user.id, scope)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'Successfully logged in'
        }

        return response


class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, _):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'Successfully logged out'
        }

        return response


class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        data = request.data

        if data['password'] != data['confirm_password']:
            raise exceptions.ValidationError('Passwords do not match')

        user.set_password(data['password'])
        user.save()
        return Response(UserSerializer(user).data)
