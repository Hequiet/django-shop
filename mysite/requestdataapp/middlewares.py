import time
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

REQUEST_LOG = {}

RATE_PERIOD = 0

class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        ip = self.get_client_ip(request)
        now = time.time()

        if ip in REQUEST_LOG:
            last_request_time = REQUEST_LOG[ip]
            if now - last_request_time < RATE_PERIOD:
                return render(request, 'requestdataapp/err_429.html',
                              context={'ip': ip}, status=429)
        REQUEST_LOG[ip] = now
        response = self.get_response(request)
        return response

    def get_client_ip(self, request: HttpRequest) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip



