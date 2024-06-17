def SetDefaultLangMiddleware(get_response):

    def middleware(request):
        
        if not request.COOKIES.get('django_language'): 
            request.COOKIES['django_language'] = 'az'

        response = get_response(request)
        
        return response

    return middleware