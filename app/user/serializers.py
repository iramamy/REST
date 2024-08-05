"""Serializers for the user api view"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create and return user with secured/encrypted password"""
        return get_user_model().objects.create_user(**validated_data)


class AuthenticationSerializer(serializers.Serializer):
    """Serilizer for user authentication token"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""

        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("requets"), username=email, password=password
        )

        if not user:
            message = _("Unable to authenticate using the provided credentials")
            raise serializers.ValidationError(message, code="authorization")

        attrs["user"] = user

        return attrs
