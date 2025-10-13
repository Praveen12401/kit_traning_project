from django.shortcuts import render,HttpResponse
class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # Allow only the home page ("/") to be accessed normally
        
        if request.path != '/':
            return render(request,'under_construction.html')
            
        
        # Code to be executed for each request/response after
        # the view is called.
         # For home page, continue normal processing
        response = self.get_response(request)
         
        return response