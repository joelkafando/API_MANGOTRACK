from django.db import models


class Acheteur(models.Model):
    """Entite de l'EXEMPLE RESOLU (annexe A). Ne pas modifier."""
    nom = models.CharField(max_length=100, unique=True)
    ville = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "acheteurs"

    def __str__(self):
        return self.nom


class Producteur(models.Model):
    """Table producteurs (id, nom unique, village)."""
    nom = models.CharField(max_length=100, unique=True)
    village = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "producteurs"

    def __str__(self):
        return self.nom


class Livraison(models.Model):
    """Table livraisons (id, producteur_id, variete, poids_kg, sens).

    Un producteur a plusieurs livraisons (1 - N).
    on_delete=PROTECT : la base refuse de supprimer un producteur qui a des
    livraisons (ProtectedError). C'est la regle de suppression de Salimata.
    """
    SENS_CHOIX = [("entree", "entree"), ("sortie", "sortie")]

    # Foreignkey(Producteur) clé etrangère, django créer producteur_id et la pointe à producteur.id
    # Ainsi on pourrait avoir un producteur plusieurs livraison, cela répond aux problèmes de traces
    producteur = models.ForeignKey(
        Producteur,
        on_delete=models.PROTECT,
        related_name="livraisons",
        db_index=False,  # volontaire : l'index est l'un des defis (phase 3)
    )
    variete = models.CharField(max_length=100)
    poids_kg = models.FloatField()
    sens = models.CharField(max_length=10, choices=SENS_CHOIX)

    class Meta:
        db_table = "livraisons"

    def __str__(self):
        return f"{self.sens} {self.poids_kg} kg ({self.variete})"
