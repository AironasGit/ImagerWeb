from django.conf import settings
from django.shortcuts import redirect

class GatedContent(object):
    def __init__(self, get_response):
        self.get_response = get_response
        
    def process_request(self, request):
        path = request.path
        user = request.user # out of the box auth, YMMV
    
        is_gated = False
        for gated in settings.GATED_CONTENT:
            if path.startswith(gated) or path.endswith(gated):
                is_gated = True
                break
        # Validate the user is an authenticated/valid user
        if is_gated and not user.is_authenticated():
            return redirect('')