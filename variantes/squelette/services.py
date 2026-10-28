"""Couche metier : les regles de MangoTrack vivent ICI, pas dans les vues.

Pourquoi ? Un script qui importerait 500 livraisons doit respecter la meme
regle du stock que l'API. Le service ne connait PAS HTTP : il leve une erreur
metier (StockInsuffisant) et c'est la vue qui la traduit en code 409.
"""
from .models import Livraison


class StockInsuffisant(Exception):
    """Levee quand une sortie demande plus que le stock disponible."""

    def __init__(self, disponible, demande):
        self.disponible = disponible
        self.demande = demande
        super().__init__(
            f"Stock insuffisant : {demande} kg demandes, {disponible} kg disponibles"
        )


def calculer_stock(producteur_id):
    """Stock = somme des entrees - somme des sorties, pour ce producteur.

    TODO (etape 2.4) : calcule-le avec une agregation filtree, par exemple
    Livraison.objects.filter(producteur_id=..., sens=...).aggregate(Sum("poids_kg")).
    Attention : la somme vaut None s'il n'y a aucune ligne.
    Le stock n'est pas une colonne : il se CALCULE (pourquoi ? note-le dans le journal).
    """
    raise NotImplementedError("TODO etape 2.4 : calculer_stock")


def enregistrer_livraison(producteur, variete, poids_kg, sens):
    """Cree une livraison et la renvoie.

    TODO (etape 2.3) : cree la livraison avec Livraison.objects.create(...).
    TODO (etape 2.5) : AVANT de creer, si sens == "sortie" et poids_kg > stock,
    leve StockInsuffisant(disponible, demande). Verifier d'abord, ecrire ensuite :
    un refus n'ecrit rien en base.
    """
    raise NotImplementedError("TODO etape 2.3 : enregistrer_livraison")
