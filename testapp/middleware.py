from django.shortcuts import redirect
from django.urls import resolve

class PreventURLModificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_url_names = [
            'create_family', 'family_list', 'update_family', 'delete_family',
            'create_familyhead', 'familyhead_list', 'update_familyhead',
            'create_member', 'member_list'
        ]

        try:
            resolver_match = resolve(request.path)  # Get the resolved URL name
            if resolver_match.url_name not in allowed_url_names:
                return redirect(request.session.get('last_valid_url', '/'))  # Redirect to last valid page
            
            request.session['last_valid_url'] = request.path  # Store last valid page
        except:
            return redirect('/')  # Redirect to home if URL resolution fails

        return self.get_response(request)
    

from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin

class EnsureSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # If the request does not have a trailing slash AND a matching URL exists with a slash
        if not request.path.endswith('/'):
            return HttpResponsePermanentRedirect(request.path + '/')