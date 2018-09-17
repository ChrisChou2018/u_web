from django.utils.deprecation import MiddlewareMixin


class MD1(MiddlewareMixin):
    
    def process_request(self, request):
        print("MD1里面的 process_request")

    def process_response(self, request, response):
        print("MD1里面的 process_response")
        return response