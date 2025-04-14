from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

# Define a custom authentication backend to allow login using email
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            #fetch the user using the email (username will actually be the email here)
            user = User.objects.get(email=username)
            # Check if the given password matches the stored password hash
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None # If user not found, return None 
        return None
