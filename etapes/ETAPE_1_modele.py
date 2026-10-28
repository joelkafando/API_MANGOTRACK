# ETAPE 1 de l'exemple resolu (acheteur) : le modele.
# La table devient une classe. Rien d'autre.
from django.db import models


class Acheteur(models.Model):
    nom = models.CharField(max_length=100, unique=True)   # unique : pas de doublon
    ville = models.CharField(max_length=100, blank=True, default="")
