from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import services
from .models import Acheteur, Livraison, Producteur
from .serializers import (
    AcheteurSerializer,
    LivraisonSerializer,
    ProducteurSerializer,
)


# ===========================================================================
# EXEMPLE RESOLU : l'acheteur (annexe A). A lire, a transferer, pas a recopier.
# ===========================================================================
@api_view(["GET", "POST"])
def acheteurs(request):
    if request.method == "POST":
        serializer = AcheteurSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Donnees invalides", "errors": serializer.errors},
                status=422,
            )
        acheteur = serializer.save()
        return Response(AcheteurSerializer(acheteur).data, status=201)
    return Response(AcheteurSerializer(Acheteur.objects.all(), many=True).data)


@api_view(["GET", "PUT", "DELETE"])
def acheteur(request, pk):
    obj = get_object_or_404(Acheteur, pk=pk)  # 404
    if request.method == "PUT":
        serializer = AcheteurSerializer(obj, data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Donnees invalides", "errors": serializer.errors},
                status=422,
            )
        serializer.save()
        return Response(serializer.data)  # 200
    if request.method == "DELETE":
        obj.delete()
        return Response(status=204)  # 204
    return Response(AcheteurSerializer(obj).data)


# ===========================================================================
# PRODUCTEUR
# ===========================================================================
@api_view(["GET", "POST"])
def producteurs(request):
    if request.method == "POST":
        serializer = ProducteurSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Donnees invalides", "errors": serializer.errors},
                status=422,
            )
        producteur = serializer.save()
        return Response(ProducteurSerializer(producteur).data, status=201)
    return Response(
        ProducteurSerializer(Producteur.objects.order_by("id"), many=True).data
    )


@api_view(["GET", "PUT", "DELETE"])
def producteur(request, pk):
    obj = get_object_or_404(Producteur, pk=pk)  # 404
    if request.method == "PUT":
        serializer = ProducteurSerializer(obj, data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Donnees invalides", "errors": serializer.errors},
                status=422,
            )
        serializer.save()
        return Response(serializer.data)  # 200
    if request.method == "DELETE":
        try:
            obj.delete()
        except ProtectedError:
            return Response(
                {
                    "message": "Suppression refusee : ce producteur a des livraisons",
                    "errors": None,
                },
                status=409,
            )
        return Response(status=204)  # 204
    return Response(ProducteurSerializer(obj).data)


@api_view(["GET"])
def stock_producteur(request, pk):
    obj = get_object_or_404(Producteur, pk=pk)
    return Response(
        {"producteur_id": obj.pk, "stock_kg": services.calculer_stock(obj.pk)}
    )


# ===========================================================================
# LIVRAISON
# ===========================================================================
@api_view(["GET", "POST"])
def livraisons(request):
    if request.method == "POST":
        serializer = LivraisonSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Donnees invalides", "errors": serializer.errors},
                status=422,
            )
        try:
            livraison = services.enregistrer_livraison(**serializer.validated_data)
        except services.StockInsuffisant as erreur:
            return Response({"message": str(erreur), "errors": None}, status=409)
        return Response(LivraisonSerializer(livraison).data, status=201)
    return Response(
        LivraisonSerializer(Livraison.objects.order_by("id"), many=True).data
    )


@api_view(["GET"])
def livraison(request, pk):
    obj = get_object_or_404(Livraison, pk=pk)
    return Response(LivraisonSerializer(obj).data)
