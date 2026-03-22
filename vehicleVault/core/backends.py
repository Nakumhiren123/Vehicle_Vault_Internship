from django.contrib.auth.backends import ModelBackend
from .models import User


class EmailBackend(ModelBackend):
    """
    Authenticate using email + password instead of username.
    Works for both Django admin (/admin/) and custom login views.
    """

    def authenticate(self, request, email=None, password=None,
                     username=None, **kwargs):
        # Django admin passes credentials as 'username' — treat it as email
        login_email = email or username

        if not login_email:
            return None

        try:
            user = User.objects.get(email=login_email)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None