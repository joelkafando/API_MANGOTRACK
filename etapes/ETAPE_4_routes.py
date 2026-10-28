# ETAPE 4 : les routes. Seulement l'aiguillage : adresse -> vue.
# Le verbe n'est jamais dans l'adresse (pas de /ajouterAcheteur).
urlpatterns = [
    path("acheteurs", views.acheteurs),
    path("acheteurs/<int:pk>", views.acheteur),
]
