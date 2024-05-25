from django.urls import path
from .views import AIView, RecipeGenerationView

urlpatterns = [
    path('generate/', AIView.as_view(), name='generate_api'),
    path('generate-recipes/', RecipeGenerationView.as_view(), name='generate_recipes_api'),
]