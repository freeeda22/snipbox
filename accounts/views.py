from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from django.db import transaction
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny 
from rest_framework.generics import ( 
    CreateAPIView, 
    GenericAPIView,
    RetrieveUpdateAPIView,
    DestroyAPIView,
    RetrieveAPIView,
)
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import ( 
    UserCreateSerializer,
    UserUpdateSerializer,
    UserSerializer,
)

User = get_user_model()  

class UserCreateAPIView(CreateAPIView):
    """ create a user """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny] 

    def create(self, request, *args, **kwargs):
        """
        user creation.
        """
        email = request.data.get('email')  #getting email from input 
        if User.objects.filter(email=email).exists(): #checking whether the email already exists in the db
            return Response({
                "error": "A user with this email already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        raw_password = request.data.get('password')  #getting password from input
        if not raw_password: #checking whether the password have the data
            return Response({
                "error": "Password is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate the incoming data using the serializer
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():  # Begin transaction block 
                    hashed_password = make_password(request.data['password']) #hashing password 
                    username = self.request.data.get("email").split("@")[0] #to update uername split the email at @
                    serializer.save(password=hashed_password, #save the user
                                    username = username)
                # Send confirmation email after user is created successfully
                send_mail(
                    subject='Welcome to SnipBox!',
                    message='Thank you for signing up with SnipBox. We are happy to have you on board.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.request.data.get("email")],
                    fail_silently=False,  # Set to True in production to suppress errors if email fails
                )
                return Response({
                    "message": "User created successfully!",
                    "user": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as error:
                return Response({
                    "error": "Something went wrong during user creation.",  #handles the error
                    "details": str(error)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(GenericAPIView):
    """
    User login API. Authenticates using email and password.
    """
    permission_classes = [AllowAny] 

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')  #getting email from input data
        password = request.data.get('password') #getting password from input data

        # Validate email and password
        if not email or not password:
            return Response({
                "error": "Email and password are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return Response({
                "error": "Invalid email or password."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT token if authentication is successful
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        

        return Response({
            "message": "Login successful.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,  # Include other user details as needed
            }
        }, status=status.HTTP_200_OK)

class UserUpdateAPIView(RetrieveUpdateAPIView):
    """ user update api"""
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        """
        Custom update method to handle the update of user data.
        """
        user = self.get_object() #Fetches the object based on the lookup_field from the URL

        # Serialize the incoming data
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid(): #validates the serializer
            serializer.save()  #updating the data
            send_mail(
                subject='Profile was Updated',
                message='Hi {username}, your profile has been updated successfully.'.format(username=user),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({
                "message": "User updated successfully!",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) #Raises error

class UserDeleteAPIView(DestroyAPIView):
    """
    Delete a user.
    Only authenticated users or superadmin can delete their own account.
    """
    queryset = User.objects.all()
    lookup_field = 'id'  # Assuming the user is deleted by the 'id'

    def delete(self, request, *args, **kwargs):
        user = self.get_object()  # Get the user object based on the ID from the URL
        # Check if the user is trying to delete their own account and loggined user is superadmin or not
        if user == self.request.user or self.request.user.is_superuser:
            self.perform_destroy(user)  #destory the user
            send_mail(
                subject='Your SnipBox Account Has Been Deleted',
                message=f'Hi {user.first_name},\n\nYour SnipBox account has been successfully deleted.\n\nRegards,\nSnipBox Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({
                "message": "Your account has been deleted successfully.",
            }, status=status.HTTP_204_NO_CONTENT)
    
        else:
            return Response({
                "message": "Permission denied.",
                "error": "You can only delete your own account."
            }, status=status.HTTP_403_FORBIDDEN)
    
    def perform_destroy(self, instance):
        """
        Delete the user instance from the database.
        """
        instance.delete()

class UserRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve the details of a specific user.
    """
    queryset = User.objects.all()  # Queryset to fetch user from the database
    serializer_class = UserSerializer  # Serializer class to format the response
    lookup_field = 'id'  # Use 'id' from the URL to look up the user

    def get(self, request, *args, **kwargs):
        """
        Get user details.
        """
        user = self.get_object()  # Get the user based on 'id' from the URL

        # Return the user's data in the response
        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username,  # Include other fields as needed
            "first_name": user.first_name,
            "last_name": user.last_name,
        }, status=status.HTTP_200_OK)

