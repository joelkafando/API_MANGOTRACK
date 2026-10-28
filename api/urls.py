from django.urls import path

from . import views

urlpatterns = [
    # Exemple resolu (acheteur)
    path("acheteurs", views.acheteurs),
    path("acheteurs/<int:pk>", views.acheteur),
    # Producteur
    path("producteurs", views.producteurs),
    path("producteurs/<int:pk>", views.producteur),
    path("producteurs/<int:pk>/stock", views.stock_producteur),
    # Livraison
    path("livraisons", views.livraisons),
    path("livraisons/<int:pk>", views.livraison),
]
