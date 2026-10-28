# ETAPE 2 : le serializer. Il VALIDE l'entree et CHOISIT les champs visibles.
# Laisse le ModelSerializer lire le modele : si tu redeclares "nom" a la main,
# la contrainte unique disparait et un doublon provoque une erreur 500.
from rest_framework import serializers


class AcheteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acheteur
        fields = ["id", "nom", "ville"]
        extra_kwargs = {"nom": {"min_length": 2}}
