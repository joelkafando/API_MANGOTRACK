# MangoTrack · Kit Django (séance 2)

Ce kit est le **socle** de la séance : un projet Django + Django REST Framework prêt à lancer,
avec la console de recette qui vérifie le contrat de l'API. Tu y écris le code qui manque,
étape par étape, en suivant les `TODO` numérotés.

## Ce que contient le kit

```
S2_demo_django/
├── manage.py
├── requirements.txt          dépendances (Django, DRF)
├── roues/                    les mêmes dépendances, pour installer sans internet
├── appliquer.sh / .bat       copie le squelette (ou la solution) dans api/
├── config/                   réglages et adresses racine (/api/... et /console/)
├── api/
│   ├── models.py             les 3 tables : Acheteur (exemple), Producteur, Livraison   [fourni]
│   ├── serializers.py        validation + champs visibles                               [à compléter : 2.2]
│   ├── services.py           règles métier (stock)                                      [à compléter : 2.3 à 2.5]
│   ├── views.py              les routes et les codes HTTP                               [à compléter : TODO 1 à 6]
│   ├── urls.py               aiguillage adresse -> vue                                  [fourni]
│   └── templates/console.html + static/console/recette.js    la console de recette      [fourni]
├── etapes/                   les 4 étapes de l'exemple résolu (acheteur), à lire
└── variantes/                squelette (départ) et solution (dernier recours)
```

**L'architecture, en une phrase :** la route reçoit la requête et choisit le code HTTP ; le serializer
valide l'entrée ; le service porte la règle métier et ne connaît pas HTTP ; le modèle décrit la table.
Chaque règle a donc un seul endroit où elle vit.

---

## Phase 0 · Installer et vérifier (20 min)

```bash
python -m venv venv
source venv/bin/activate            # Windows : venv\Scripts\activate
pip install -r requirements.txt     # sans internet : pip install --no-index --find-links roues -r requirements.txt
./appliquer.sh squelette            # Windows : appliquer.bat squelette
python manage.py migrate
python manage.py runserver
```

Ouvre <http://localhost:8000/console/>.

- Onglet **Requête** : `GET /api/producteurs` doit répondre **501** (le TODO n'est pas écrit, c'est normal).
- Onglet **Recette** : « Lancer la vérification » affiche **0 sur 9**.
- Premier commit : `git init`, configure ton nom, puis `git add .` et `git commit -m "kit MangoTrack S2 : point de départ"`.

> `appliquer.sh` refuse de s'exécuter une seconde fois pour ne pas écraser ton travail (`--force` pour passer outre).

---

## Phase 1 · API Producteur (45 min) → Socle 9 sur 9

Règle de travail : **une étape, une vérification à la console, puis la suivante.**
Tout se passe dans `api/views.py` (cherche `TODO 1`, `TODO 2`, `TODO 3`).

| Étape | Tu fais | Tu vérifies à la console | Recette |
|---|---|---|---|
| 1.1 | Lis `etapes/` et la partie « exemple résolu » de `views.py` (acheteur). Note le rôle de chaque pièce | Quelle pièce renvoie 404 ? 422 ? Laquelle choisit les champs visibles ? | — |
| 1.2 | Dessine les 2 tables (annexe E). Lis `api/models.py` | Le dessin montre clé primaire, clé étrangère, 1 et N | — |
| 1.3 | **TODO 1** : créer un producteur (valider, 422 ou `save()` + 201) | POST valide → 201 ; même POST → 422 ; `{}` → 422 ; `{"nom": ""}` → 422 | S1, S4, S5, S8 |
| 1.4 | **TODO 2** (liste) et **TODO 3** (lecture) : `get_object_or_404` | GET `/api/producteurs/{id}` → 200 ; `/999999` → 404 | S2, S3, S6 |
| 1.5 | **TODO 3**, branche PUT : un PUT invalide répond 422 comme un POST invalide | PUT `{"nom": "Awa Traoré"}` → 200 | S7 |
| 1.6 | **TODO 3**, branche DELETE : 204 sans corps | DELETE → 204 puis GET → 404 | S9 |
| 1.7 | Lance la recette | **9 sur 9** : lève la main | S1–S9 |

Commit : `API Producteur : créer, lire, modifier, supprimer`

Piège classique : si tu redéclares `nom` à la main dans un serializer, la contrainte d'unicité disparaît
et un doublon donne une **500** au lieu d'une 422.

---

## Phase 2 · Livraison et stock (60 min) → Cible 11 sur 11

Question du Critique avant de commencer : **« Et si deux agents expédient en même temps ? »** Note ta réponse.

| Étape | Tu fais | Où | Tu vérifies | Recette |
|---|---|---|---|---|
| 2.1 | Ajoute la règle du stock et son code (409) sur ton schéma. Où vit la règle : route, client ou couche réutilisable ? | papier | Le schéma porte « stock jamais négatif → 409 » | — |
| 2.2 | Valide le poids : méthode `validate_poids_kg` qui refuse ≤ 0 | `serializers.py` | Le `sens` inconnu et le producteur inexistant sont déjà refusés par le ModelSerializer | C2–C5 (après 2.3) |
| 2.3 | Crée la livraison : `Livraison.objects.create(...)` dans le service, puis **TODO 5** (POST) et **TODO 6** (liste) | `services.py`, `views.py` | POST entrée de 40 kg → 201 ; GET liste → 200 | C0, C1 |
| 2.4 | Calcule le stock (entrées − sorties, `aggregate(Sum(...))`, attention à `None`), puis **TODO 4** | `services.py`, `views.py` | `GET /api/producteurs/{id}/stock` → `{"producteur_id": …, "stock_kg": 40}` | (C7, C8) |
| 2.5 | **La règle** : avant de créer, une sortie > stock lève `StockInsuffisant` ; la vue l'attrape et répond 409 | `services.py`, `views.py` | Stock 40 : sortie 50 → 409 (stock reste 40) ; sortie 15 → 201 (stock 25) ; sortie 25 → 201 (stock 0) | C6–C9 |
| 2.6 | Suppression protégée : attrape `ProtectedError` autour de `delete()` et réponds 409 | `views.py` (TODO 3) | Producteur avec livraisons → 409 | C10 |
| 2.7 | Lance la recette | | **11 sur 11** | C0–C10 |

Commit : `Livraison, stock et règle du stock (409)`

**422 ou 409 ?** Peut-on décider en regardant seulement la requête ? Oui → **422**. Faut-il regarder la base ? Oui → **409**.
Producteur inconnu dans le *corps* → 422. Producteur inconnu dans l'*adresse* → 404.

---

## Phase 3 · Défi et restitution (35 min)

Si la Cible n'est pas finie, termine la Cible. Sinon, choisis **un** défi (la recette D1 à D5 les vérifie) :

| Défi | Piste |
|---|---|
| Pagination (D1, D2) | Lis `request.query_params`, découpe le queryset avec un maximum pour `per_page`, ajoute l'en-tête `X-Total-Count` : `response["X-Total-Count"] = total` |
| Filtre (D3) | `?producteur_id=3` : filtre le queryset **avant** de paginer |
| Erreurs structurées (D4, D5) | Une fonction `erreur(message, errors=None, status=...)` utilisée pour tous les 404, 409, 422. Pour le 404, remplace `get_object_or_404` par une recherche qui renvoie ta forme d'erreur |
| Index | Dans `Livraison.Meta`, ajoute `indexes = [models.Index(fields=["producteur"])]`, puis `python manage.py makemigrations` et `migrate`. Dans le kit, la clé étrangère a volontairement `db_index=False`. Compromis : lecture plus rapide, écriture un peu plus lente |

Les 10 dernières minutes : un commit par membre, auto-évaluation (annexe G), un appel qui échoue à expliquer
à la restitution, réponse au Critique, journal complété.

---

## Faire évoluer le projet : ajouter une nouvelle ressource

Le kit est fait pour grandir. Toute nouvelle entité (ex. `Acheteur`, puis `Commande`) suit les mêmes cinq pièces :

1. **Modèle** dans `api/models.py`, puis `python manage.py makemigrations` et `python manage.py migrate`.
2. **Serializer** dans `api/serializers.py` (laisse le `ModelSerializer` lire le modèle).
3. **Service** dans `api/services.py`, *seulement s'il y a une règle métier* (comme le stock).
4. **Vue** dans `api/views.py` : choisit les codes (201, 204, 404, 409, 422).
5. **Route** dans `api/urls.py`.

Ensuite, ajoute le point de recette correspondant dans `api/static/console/recette.js` (une ligne `t("X1", ...)`).
Prochaines évolutions naturelles : tests automatisés (`python manage.py test`), pagination globale,
base PostgreSQL, authentification des agents, conteneur Docker et intégration continue (le « DevOps » du cours).

---

## Dépannage rapide

| Tu vois… | Fais |
|---|---|
| « Failed to fetch » dans la console | Relance `python manage.py runserver` |
| `no such table` | `python manage.py migrate` |
| 400 au lieu de 422 | DRF répond 400 par défaut : écris `status=422` toi-même |
| 500 sur un doublon | Tu as redéclaré le champ dans le serializer |
| `Authentication credentials were not provided` ou CSRF | Rétablis `REST_FRAMEWORK` dans `config/settings.py` |
| 501 | Le TODO de cette route n'est pas encore écrit |
| Port déjà utilisé | `python manage.py runserver 8001` puis ouvre `localhost:8001/console/` |

---

## Corrigé du tableau de la partie 1 (à lire à la fin, après avoir écrit ta version)

| Problème | Entité | Règle | Code si violée |
|---|---|---|---|
| Le stock | Livraison (le stock se calcule à partir d'elle) | Stock = entrées − sorties, jamais négatif | 409 |
| La trace | Livraison, liée à Producteur par une clé étrangère obligatoire | Toute livraison a un producteur existant | 422 |
| L'erreur | Producteur | Un producteur qui a des livraisons ne se supprime pas | 409 |

`variantes/solution/` contient une correction complète et testée (Socle + Cible). Ouvre-la en dernier recours :
le transfert de l'exemple vers le producteur est ton travail.
