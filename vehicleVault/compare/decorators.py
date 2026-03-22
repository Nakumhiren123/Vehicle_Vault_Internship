from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):

            # Not logged in → send to login
            if not request.user.is_authenticated:
                return redirect('login')

            user_role = getattr(request.user, 'role', None)

            # is_staff / is_superuser users always get admin access
            if request.user.is_staff or request.user.is_superuser:
                user_role = 'admin'

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Wrong role → redirect to their own dashboard
            if user_role == 'admin':
                return redirect('admin-dashboard')
            else:
                return redirect('user-dashboard')

        return wrapper
    return decorator


# from django.shortcuts import redirect, reverse, HttpResponseRedirect
# from django.contrib import messages

# def role_required(allowed_roles=[]):
#     def decorator(view_func):
#         def wrapper_func(request, *args, **kwargs):
#             if not request.user.is_authenticated:
#                 return redirect('login')
#             if request.user.role in allowed_roles:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return HttpResponseRedirect("You are not authorized to view this page.")
#         return wrapper_func
#     return decorator