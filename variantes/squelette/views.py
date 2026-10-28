from django.db.models import ProtectedError  # noqa: F401  (utile a l'etape 2.6)
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import services  # noqa: F401  (utile a partir de l'etape 2.3)
from .models import Acheteur, Livraison, Producteur  # noqa: F401
from .serializers import (  # noqa: F401
    AcheteurSerializer,
    LivraisonSerializer,
    ProducteurSerializer,
)


def a_faire(numero):
    """501 = 'pas implemente' : le TODO de cette route n'est pas encore ecrit."""
    return Response({"message": f"TODO {numero} : a ecrire", "errors": None}, status=501)


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
# PRODUCTEUR (phase 1) : a toi de jouer. Transfere l'exemple de l'acheteur.
# ===========================================================================
@api_view(["GET", "POST"])
def producteurs(request):
    if request.method == "POST":
        # TODO 1 (etape 1.3) : creer un producteur.
        #   - valider avec ProducteurSerializer(data=request.data)
        #   - invalide -> 422 avec {"message": "Donnees invalides", "errors": ...}
        #     (DRF repondrait 400 par defaut : le contrat dit 422)
        #   - valide -> save() puis 201 avec le producteur cree (jamais 200)
        return a_faire(1)

    # TODO 2 (etape 1.4) : la liste des producteurs.
    #   Un tableau JSON : ProducteurSerializer(..., many=True).data
    return a_faire(2)


@api_view(["GET", "PUT", "DELETE"])
def producteur(request, pk):
    # TODO 3 (etapes 1.4, 1.5, 1.6 puis 2.6) : un producteur par son id.
    #   - le chercher : introuvable -> 404 (get_object_or_404)
    #   - GET    -> 200 avec le producteur                               (etape 1.4)
    #   - PUT    -> valider ; invalide 422 ; sinon save() et 200         (etape 1.5)
    #   - DELETE -> supprimer et 204 sans corps                          (etape 1.6)
    #   - DELETE, 2e partie (etape 2.6) : un producteur qui a des livraisons ne se
    #     supprime pas. La base refuse (ProtectedError) : attrape l'erreur, 409 + message.
    return a_faire(3)


@api_view(["GET"])
def stock_producteur(request, pk):
    # TODO 4 (etape 2.4) : GET /api/producteurs/{id}/stock
    #   - producteur introuvable -> 404
    #   - sinon 200 avec {"producteur_id": ..., "stock_kg": ...}
    #     en appelant services.calculer_stock(...)
    return a_faire(4)


# ===========================================================================
# LIVRAISON (phase 2)
# ===========================================================================
@api_view(["GET", "POST"])
def livraisons(request):
    if request.method == "POST":
        # TODO 5 (etapes 2.3 et 2.5) : creer une livraison.
        #   - valider avec LivraisonSerializer ; invalide -> 422 {"message", "errors"}
        #   - appeler services.enregistrer_livraison(**serializer.validated_data)
        #   - attraper services.StockInsuffisant -> 409 avec un message lisible
        #   - sinon 201 avec la livraison creee
        return a_faire(5)

    # TODO 6 (etape 2.3) : la liste des livraisons (tableau JSON, many=True).
    return a_faire(6)


@api_view(["GET"])
def livraison(request, pk):
    obj = get_object_or_404(Livraison, pk=pk)
    return Response(LivraisonSerializer(obj).data)
