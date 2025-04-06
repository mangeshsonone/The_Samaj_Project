# from django.http import JsonResponse

# def get_client_ip():
#     x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(",")[0]  # Get the first IP from the list
#         print(ip)
#     else:
#         ip = request.META.get("REMOTE_ADDR")
#         print(ip)


# get_client_ip()