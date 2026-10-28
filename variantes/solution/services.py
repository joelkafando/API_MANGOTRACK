"""Couche metier : les regles de MangoTrack vivent ICI, pas dans les vues.

Le service ne connait PAS HTTP : il leve une erreur metier (StockInsuffisant)
et c'est la vue qui la traduit en code 409.
"""
from django.db import transaction
from django.db.models import Sum

from .models import Livraison, Producteur


class StockInsuffisant(Exception):
    """Levee quand une sortie demande plus que le stock disponible."""

    def __init__(self, disponible, demande):
        self.disponible = disponible
        self.demande = demande
        super().__init__(
            f"Stock insuffisant : {demande} kg demandes, {disponible} kg disponibles"
        )


def calculer_stock(producteur_id):
    """Stock = somme des entrees - somme des sorties. Calcule, jamais stocke :
    une colonne 'stock' finirait par diverger des livraisons."""
    lignes = Livraison.objects.filter(producteur_id=producteur_id)
    entrees = lignes.filter(sens="entree").aggregate(t=Sum("poids_kg"))["t"] or 0
    sorties = lignes.filter(sens="sortie").aggregate(t=Sum("poids_kg"))["t"] or 0
    return round(entrees - sorties, 3)


@transaction.atomic
def enregistrer_livraison(producteur, variete, poids_kg, sens):
    """Verifie la regle du stock, puis ecrit. Un refus n'ecrit rien."""
    if sens == "sortie":
        # Reponse a la question du Critique ("et si deux agents expedient en
        # meme temps ?") : on verrouille la ligne du producteur pour que les
        # deux verifications de stock se fassent l'une apres l'autre.
        # (No-op sous SQLite, effectif sous PostgreSQL / MySQL.)
        Producteur.objects.select_for_update().get(pk=producteur.pk)
        disponible = calculer_stock(producteur.pk)
        if round(poids_kg, 3) > disponible:
            raise StockInsuffisant(disponible, poids_kg)
    return Livraison.objects.create(
        producteur=producteur, variete=variete, poids_kg=poids_kg, sens=sens
    )
