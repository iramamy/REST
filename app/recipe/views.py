"""Views for recipe API"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions

from core.models import Recipe
from recipe import serializers


class RecipeViewSets(viewsets.ModelViewSet):
    """View to manage recipe APIs"""

    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter recipes for authenticated user only"""

        return self.queryset.filter(
            user=self.request.user,
        ).order_by("-id")

    def get_serializer_class(self):
        """Return serializer class for request"""

        if self.action == "list":
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create new recipe for authenticated user"""

        serializer.save(user=self.request.user)
