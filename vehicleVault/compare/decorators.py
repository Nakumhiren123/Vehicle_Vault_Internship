from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):

            # Not logged in → send to login
            if not request.user.is_authenticated:
                return redirect('login')

            # Check role attribute exists and matches
            user_role = getattr(request.user, 'role', None)
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Wrong role → redirect to their own dashboard
            if user_role == 'admin':
                return redirect('admin-dashboard')
            elif user_role == 'user':
                return redirect('user-dashboard')

            # Fallback: 403
            return HttpResponseForbidden("You are not authorized to view this page.")

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