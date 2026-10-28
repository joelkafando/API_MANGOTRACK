from rest_framework import serializers

from .models import Acheteur, Livraison, Producteur


# --- Exemple resolu (acheteur) : a lire, pas a modifier -------------------
class AcheteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acheteur
        fields = ["id", "nom", "ville"]
        extra_kwargs = {"nom": {"min_length": 2}}


# --- Producteur : la validation est DEJA fournie (etape 1.3) ---------------
# Lis-la et explique-la a l'equipe : nom d'au moins 2 lettres, nom unique.
# ATTENTION : ne redeclare pas le champ "nom" a la main, tu perdrais la
# contrainte d'unicite (un doublon donnerait alors une erreur 500).
class ProducteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producteur
        fields = ["id", "nom", "village"]
        extra_kwargs = {"nom": {"min_length": 2}}


# --- Livraison -------------------------------------------------------------
# Deja gere par le ModelSerializer : un "sens" inconnu et un "producteur"
# inexistant sont refuses (ce sont des donnees invalides -> 422 dans la vue).
class LivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livraison
        fields = ["id", "producteur", "variete", "poids_kg", "sens"]

    def validate_poids_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le poids doit etre strictement superieur a 0.")
        return value
