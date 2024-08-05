"""Views for user api"""

from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


from user.serializers import UserSerializer, AuthenticationSerializer


class CreateUserView(generics.CreateAPIView):
    """Create new user in the system"""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create new auth token for new user"""

    serializer_class = AuthenticationSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
