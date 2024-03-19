from .services import UserService


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        scope = 'ambassador' if 'api/ambassador' in request.path else 'admin'
        try:
            user = UserService.get('/user/' + scope, headers=request.headers)
        except:
            user = None

        request.user_ms = user
        return self.get_response(request)
