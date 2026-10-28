# MangoTrack · Guide complet du kit Django

**Séance 2 · L3 MIAGE · Applications N-tiers & DevOps**
Ce guide fait deux choses : il **explique tout le code source généré**, fichier par fichier, et il te dit **exactement ce que tu dois coder maintenant**, dans l'ordre.

---

## Sommaire

1. [Rappel de la mission](#1-rappel-de-la-mission)
2. [Le contrat de l'API en bref](#2-le-contrat-de-lapi-en-bref)
3. [Comment une requête traverse le code](#3-comment-une-requête-traverse-le-code)
4. [Arborescence du projet](#4-arborescence-du-projet)
5. [Le code expliqué fichier par fichier](#5-le-code-expliqué-fichier-par-fichier)
6. [Ce que tu dois coder maintenant](#6-ce-que-tu-dois-coder-maintenant)
7. [Git, journal de bord et restitution](#7-git-journal-de-bord-et-restitution)
8. [Après la séance : faire évoluer le projet](#8-après-la-séance--faire-évoluer-le-projet)
9. [Dépannage](#9-dépannage)

---

## 1. Rappel de la mission

Salimata dirige une coopérative de mangues. Elle décrit trois douleurs. Ton travail est de les traduire en règles techniques.

| Problème | Entité concernée | Règle à respecter | Code HTTP si violée |
|---|---|---|---|
| **Le stock** : un agent sort plus que ce qu'il y a (on a déjà eu moins quarante kilos) | **Livraison** (le stock se calcule à partir d'elles) | Stock = somme des entrées − somme des sorties, **jamais négatif** | **409** |
| **La trace** : impossible de retrouver le producteur d'un lot | **Livraison**, liée à **Producteur** par une clé étrangère obligatoire | Toute livraison appartient à un producteur qui existe | **422** |
| **L'erreur** : Awa a été effacée avec tout son historique | **Producteur** | Un producteur qui a des livraisons **ne se supprime pas** | **409** |

> Écris d'abord ta propre version de ce tableau dans le journal, puis compare avec celle-ci à la fin.

Il y a donc **deux entités** (Producteur, Livraison), **une règle de stock** et **une règle de suppression**.

---

## 2. Le contrat de l'API en bref

La console de recette vérifie exactement ce contrat.

| Adresse | Verbe | Succès | Échecs |
|---|---|---|---|
| `/api/producteurs` | GET | 200 : la liste | |
| `/api/producteurs` | POST | 201 : le producteur créé | 422 : nom absent, vide ou déjà pris |
| `/api/producteurs/{id}` | GET | 200 | 404 |
| `/api/producteurs/{id}` | PUT | 200 : le producteur modifié | 404, 422 |
| `/api/producteurs/{id}` | DELETE | 204 : rien | 404 ; 409 : il a des livraisons |
| `/api/producteurs/{id}/stock` | GET | 200 : `{"producteur_id": 3, "stock_kg": 40}` | 404 |
| `/api/livraisons` | GET | 200 : la liste | |
| `/api/livraisons` | POST | 201 : la livraison créée | 422 : poids ≤ 0, sens inconnu, producteur inconnu ; 409 : sortie > stock |
| `/api/livraisons/{id}` | GET | 200 | 404 |

**Corps d'un producteur :** `{"nom": "Awa", "village": "Orodara"}`
**Corps d'une livraison :** `{"producteur": 3, "variete": "Kent", "poids_kg": 40, "sens": "entree"}` (sens : `entree` ou `sortie`)
**Forme d'une erreur :** `{"message": "Donnees invalides", "errors": {"nom": ["..."]}}`

### Les codes HTTP à retenir

| Code | Sens | Quand |
|---|---|---|
| 200 | OK | Lecture ou modification réussie |
| 201 | Créé | Un POST a créé quelque chose (jamais 200) |
| 204 | Pas de contenu | Suppression réussie, on ne renvoie rien |
| 404 | Introuvable | L'**adresse** ne désigne rien (`/api/producteurs/999`) |
| 422 | Donnée invalide | La requête est invalide **en elle-même** |
| 409 | Conflit | La requête est valide, mais l'**état des données** l'interdit |
| 500 | Erreur serveur | Ta faute, jamais celle du client. Ne jamais la produire exprès |

### Le test des deux questions (422 ou 409 ?)

1. Peut-on décider **en regardant seulement la requête** ? Oui → **422** (un poids négatif est invalide quel que soit l'état de la base).
2. Faut-il **regarder la base** ? Oui → **409** (une sortie de 50 kg est valide, mais il n'y a que 40 kg en stock).

Cas piège : un producteur inconnu **dans le corps** d'une livraison est un **422**. Un producteur inconnu **dans l'adresse** (`/api/producteurs/999`) est un **404**.

---

## 3. Comment une requête traverse le code

Retiens ce schéma, c'est la clé de toute l'architecture :

```
Client (console)
     │   POST /api/livraisons  {"producteur": 3, "poids_kg": 50, "sens": "sortie"}
     ▼
config/urls.py ──► api/urls.py          « quelle vue pour cette adresse ? »
     ▼
api/views.py                            Choisit le CODE HTTP. Ne contient pas de règle métier.
     │  1. valide avec ──► api/serializers.py   (422 si la requête est invalide en elle-même)
     │  2. appelle    ──► api/services.py       (la RÈGLE du stock vit ici)
     │                        │  lit / écrit ──► api/models.py ──► base SQLite
     │  3. attrape l'erreur métier StockInsuffisant et la traduit en 409
     ▼
Réponse JSON + code (201, 409, 422...)
```

**Règle d'or : chaque règle a un seul endroit où elle vit.**

| Couche | Fichier | Responsabilité | Elle ne fait PAS |
|---|---|---|---|
| Routes | `urls.py` | Adresse → vue | Aucune logique |
| Vue | `views.py` | Choisir le code HTTP, orchestrer | Ne calcule pas le stock |
| Serializer | `serializers.py` | Valider l'entrée, choisir les champs visibles | Ne regarde pas l'état de la base (sauf unicité, existence) |
| Service | `services.py` | Les règles métier (stock) | Ne connaît pas HTTP : il lève une erreur, il ne renvoie pas de code |
| Modèle | `models.py` | Décrire les tables et contraintes | Aucune règle d'API |

Pourquoi le stock est dans le **service** et pas dans la vue ? Parce qu'un script qui importerait 500 livraisons doit respecter **la même règle** sans passer par HTTP.

---

## 4. Arborescence du projet

```
S2_demo_django/
├── manage.py                    Outil en ligne de commande de Django
├── requirements.txt             Dépendances Python
├── roues/                       Les mêmes dépendances, pour installer sans internet
├── appliquer.sh / appliquer.bat Copie le squelette (ou la solution) dans api/
├── .gitignore                   Fichiers à ne jamais commiter
├── README.md                    Guide court livré avec le kit
├── config/                      Réglages du projet
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/                         L'application : tout le code de MangoTrack
│   ├── models.py                Les 3 tables                          [fourni]
│   ├── migrations/0001_initial.py   Création des tables              [fourni]
│   ├── serializers.py           Validation                            [à compléter]
│   ├── services.py              Règles métier                         [à compléter]
│   ├── views.py                 Routes et codes HTTP                  [à compléter]
│   ├── urls.py                  Aiguillage                            [fourni]
│   ├── templates/console.html   Page de la console de recette         [fourni]
│   └── static/console/recette.js    La logique de la recette          [fourni]
├── etapes/                      Les 4 étapes de l'exemple résolu (acheteur)
└── variantes/
    ├── squelette/               Point de départ (views, serializers, services)
    └── solution/                Correction complète, dernier recours
```

---

## 5. Le code expliqué fichier par fichier

### 5.1 `manage.py`

Point d'entrée de toutes les commandes Django.

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
```

Cette ligne dit à Django où trouver les réglages : le fichier `config/settings.py`. Ensuite `execute_from_command_line(sys.argv)` exécute la commande que tu tapes.

| Commande | Effet |
|---|---|
| `python manage.py migrate` | Crée les tables dans la base |
| `python manage.py runserver` | Lance le serveur de développement (port 8000) |
| `python manage.py makemigrations` | Génère une migration après un changement dans `models.py` |
| `python manage.py shell` | Console Python avec ton projet chargé (utile pour tester le stock) |

**Tu n'as jamais à modifier ce fichier.**

### 5.2 `requirements.txt`

```
Django>=5.2,<5.3
djangorestframework>=3.15
tzdata
```

- **Django** : le framework, avec son **ORM** (l'outil qui traduit une table en classe et une ligne en objet, donc pas de SQL à la main).
- **djangorestframework (DRF)** : ajoute ce qu'il faut pour construire une API : `@api_view`, `Response`, serializers.
- **tzdata** : base des fuseaux horaires, nécessaire sous Windows.

Installation : `pip install -r requirements.txt`. Sans internet : `pip install --no-index --find-links roues -r requirements.txt` (le dossier `roues/` contient les mêmes paquets déjà téléchargés).

### 5.3 `.gitignore`

```
venv/
db.sqlite3
__pycache__/
*.pyc
.variante_appliquee
```

Liste de ce que Git ignore : l'environnement virtuel, la base de données locale, les fichiers compilés. **Ne commite jamais ces fichiers.** Le fichier `.variante_appliquee` est le marqueur posé par `appliquer.sh` (voir 5.17).

### 5.4 `config/settings.py` (les réglages)

Ne modifie rien ici, sauf si on te le demande. Voici ce que chaque bloc fait et **pourquoi**.

| Réglage | Rôle |
|---|---|
| `DEBUG = True` | Affiche les erreurs détaillées. **Jamais en production.** C'est lui qui produit la page « Page non trouvée » avec la liste des adresses |
| `ALLOWED_HOSTS = ["*"]` | Accepte toutes les adresses (kit de formation) |
| `INSTALLED_APPS` | `staticfiles` (sert `recette.js`), `rest_framework` (DRF), `api` (ton application) |
| `MIDDLEWARE` | Uniquement `CommonMiddleware`. Il n'y a **ni sessions, ni CSRF** : c'est volontaire, une API JSON n'en a pas besoin ici |
| `APPEND_SLASH = False` | `/api/producteurs` et `/api/producteurs/` sont deux adresses différentes. Le contrat n'a pas de `/` final |
| `TEMPLATES` avec `APP_DIRS: True` | Django cherche les pages HTML dans `api/templates/` : c'est comme ça qu'il trouve `console.html` |
| `DATABASES` | SQLite, fichier `db.sqlite3` à la racine. Aucune installation nécessaire |
| `STATIC_URL = "static/"` | Les fichiers statiques sont servis sous `/static/` |

Le bloc le plus important :

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "UNAUTHENTICATED_USER": None,
}
```

- **Pas d'authentification, tout est autorisé** : sinon DRF répondrait « Authentication credentials were not provided » ou une erreur CSRF.
- **Renderer JSON uniquement** : l'API répond toujours en JSON, jamais en page HTML.
- **Parser JSON uniquement** : le corps des requêtes doit être du JSON valide. Un JSON cassé (virgule oubliée) donne un 400 automatique de DRF, hors contrat.
- `UNAUTHENTICATED_USER: None` : évite à DRF de chercher le système d'utilisateurs de Django, que ce projet n'installe pas.

> Si tu vois une erreur d'authentification ou CSRF, c'est que ce bloc a été modifié. Rétablis-le tel quel.

### 5.5 `config/urls.py` (adresses racine)

```python
urlpatterns = [
    path("", RedirectView.as_view(url="/console/")),
    path("api/", include("api.urls")),
    path("console/", TemplateView.as_view(template_name="console.html")),
]
```

- `""` : la racine `/` redirige vers la console (c'est ce qui évite le 404 sur `http://127.0.0.1:8000/`).
- `"api/"` : tout ce qui commence par `/api/` est confié à `api/urls.py`. C'est pourquoi, dans `api/urls.py`, les adresses s'écrivent `producteurs` et non `api/producteurs`.
- `"console/"` : affiche la page `console.html`. Pas besoin de vue Python, `TemplateView` suffit.

### 5.6 `config/wsgi.py`

Point d'entrée utilisé par un vrai serveur web en production (gunicorn, etc.). Tu ne t'en sers pas pendant la séance : `runserver` suffit. Il deviendra utile plus tard pour le déploiement (partie DevOps).

### 5.7 `api/apps.py`

Déclare l'application `api` (`name = "api"`) et le type de clé primaire par défaut (`BigAutoField`, un entier qui s'incrémente tout seul). Aucune modification.

### 5.8 `api/models.py` (les tables)

Chaque classe est une table, chaque attribut est une colonne. C'est l'**ORM**.

**`Acheteur`** : l'entité de l'**exemple résolu**. Elle sert de modèle à imiter. Ne la modifie pas.

**`Producteur`** : table `producteurs`

```python
class Producteur(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    village = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "producteurs"
```

- `unique=True` est une **contrainte** : la base elle-même refuse deux producteurs de même nom. C'est ce qui permet au serializer de détecter les doublons (422).
- `blank=True, default=""` : le village est facultatif.
- `db_table` : force le nom exact de la table, comme dans le document.
- La clé primaire `id` est ajoutée automatiquement par Django.

**`Livraison`** : table `livraisons`

```python
class Livraison(models.Model):
    SENS_CHOIX = [("entree", "entree"), ("sortie", "sortie")]

    producteur = models.ForeignKey(
        Producteur,
        on_delete=models.PROTECT,
        related_name="livraisons",
        db_index=False,
    )
    variete = models.CharField(max_length=100)
    poids_kg = models.FloatField()
    sens = models.CharField(max_length=10, choices=SENS_CHOIX)
```

| Élément | Ce qu'il fait |
|---|---|
| `ForeignKey(Producteur)` | **Clé étrangère** : crée la colonne `producteur_id` qui pointe vers `producteurs.id`. C'est le **1-N** : un producteur, plusieurs livraisons. Elle répond au problème « La trace » |
| `on_delete=models.PROTECT` | **La règle de suppression de Salimata.** La base refuse de supprimer un producteur qui a des livraisons et lève `ProtectedError`. Tu la traduiras en 409 |
| `related_name="livraisons"` | Permet d'écrire `producteur.livraisons` pour retrouver ses livraisons |
| `db_index=False` | **Volontaire.** Django indexe normalement les clés étrangères tout seul. On désactive l'index pour que le défi « Index » (phase 3) ait un sens |
| `choices=SENS_CHOIX` | Seules les valeurs `entree` et `sortie` sont acceptées. Le serializer en déduit tout seul qu'un sens inconnu est invalide |
| `FloatField` | Poids en kg, décimaux autorisés |

> Le **stock n'est pas une colonne**. Il se calcule. Si on le stockait, il finirait par diverger de la somme réelle des livraisons (oubli de mise à jour, erreur, suppression). La vérité, ce sont les livraisons.

### 5.9 `api/migrations/0001_initial.py`

Fichier **généré** par `makemigrations`. Il décrit comment créer les trois tables. La commande `python manage.py migrate` l'exécute et produit `db.sqlite3`.

Règle à retenir : **chaque fois que tu modifies `models.py`**, tu dois lancer `makemigrations` (génère une nouvelle migration) puis `migrate` (l'applique). Sinon l'erreur `no such table` ou `no such column` apparaît.

### 5.10 `api/serializers.py` (la validation)

Un **serializer** fait deux métiers :

- **À l'entrée** (`Serializer(data=request.data)`) : il **valide** ce que le client envoie. `is_valid()` renvoie `True` ou `False`, et `.errors` donne la liste des problèmes.
- **À la sortie** (`Serializer(objet).data`) : il **choisit les champs visibles** et les convertit en JSON.

Avec un `ModelSerializer`, DRF lit le modèle et en déduit **automatiquement** les règles : champ obligatoire, longueur maximale, unicité, valeurs de `choices`, existence de la clé étrangère.

**`AcheteurSerializer`** (exemple résolu) :

```python
class AcheteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acheteur
        fields = ["id", "nom", "ville"]
        extra_kwargs = {"nom": {"min_length": 2}}
```

**`ProducteurSerializer`** (déjà fourni, étape 1.3) a la même forme : nom d'au moins 2 lettres, nom unique. Tu dois pouvoir l'expliquer à l'équipe.

> **Le piège réel (Django).** Si tu redéclares `nom = serializers.CharField(...)` à la main, tu perds l'unicité héritée du modèle : un doublon provoque alors une erreur **500**. Laisse le `ModelSerializer` lire le modèle.

**`LivraisonSerializer`** (à compléter à l'étape 2.2) :

```python
class LivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livraison
        fields = ["id", "producteur", "variete", "poids_kg", "sens"]
    # TODO : validate_poids_kg
```

Ce qu'il fait **déjà** sans rien écrire :
- `producteur` inexistant → erreur de validation (le champ vérifie que l'id existe dans la table).
- `sens` inconnu → erreur de validation (à cause de `choices`).

Ce qui **manque** : refuser un poids ≤ 0. DRF reconnaît automatiquement toute méthode nommée `validate_<nom_du_champ>`, donc `validate_poids_kg(self, value)`.

### 5.11 `api/services.py` (les règles métier)

Le fichier où vit **la règle du stock**. Il ne connaît pas HTTP.

**`StockInsuffisant`** (fournie) : une exception métier.

```python
class StockInsuffisant(Exception):
    def __init__(self, disponible, demande):
        self.disponible = disponible
        self.demande = demande
        super().__init__(f"Stock insuffisant : {demande} kg demandes, {disponible} kg disponibles")
```

Le service **lève** cette erreur. C'est la vue qui l'**attrape** et décide du code 409. Le service n'écrit jamais `409`, parce que le même service pourrait être appelé par un script ou une tâche planifiée, où un code HTTP n'a aucun sens.

**`calculer_stock(producteur_id)`** (à écrire, étape 2.4) : renvoie entrées − sorties.
**`enregistrer_livraison(producteur, variete, poids_kg, sens)`** (à écrire, étapes 2.3 et 2.5) : crée la livraison, après avoir vérifié la règle pour une sortie.

Dans le squelette, ces deux fonctions lèvent `NotImplementedError` tant que tu ne les as pas écrites.

Principe central : **vérifier d'abord, écrire ensuite.** Un refus n'écrit rien en base.

### 5.12 `api/views.py` (routes et codes HTTP)

C'est le fichier principal de ton travail.

**Imports et outils**

| Élément | Rôle |
|---|---|
| `@api_view([...])` | Transforme une fonction en vue d'API. La liste indique les verbes acceptés (un autre verbe → 405 automatique) |
| `request.data` | Le corps JSON envoyé par le client |
| `Response(donnees, status=...)` | Renvoie du JSON avec le code choisi |
| `get_object_or_404(Modele, pk=pk)` | Cherche l'objet, sinon répond **404** tout seul |
| `ProtectedError` | L'erreur levée par la base quand `PROTECT` refuse une suppression |
| `a_faire(numero)` | Fonction du squelette : renvoie **501** « TODO n : à écrire ». C'est pourquoi une route non faite répond 501 |

**L'exemple résolu `acheteurs` / `acheteur` (à lire, à transférer, pas à recopier)**

```python
@api_view(["GET", "POST"])
def acheteurs(request):
    if request.method == "POST":
        serializer = AcheteurSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Donnees invalides",
                             "errors": serializer.errors}, status=422)
        acheteur = serializer.save()
        return Response(AcheteurSerializer(acheteur).data, status=201)
    return Response(AcheteurSerializer(Acheteur.objects.all(), many=True).data)
```

Lecture ligne par ligne :

1. `AcheteurSerializer(data=request.data)` : on prépare la validation de ce que le client a envoyé.
2. `is_valid()` : si c'est faux, on répond **422** avec la forme d'erreur du contrat. DRF répondrait 400 par défaut, **mais notre contrat dit 422**, donc on l'écrit nous-mêmes.
3. `serializer.save()` : écrit en base et renvoie l'objet créé.
4. `status=201` : créé, **jamais 200**.
5. Sans POST, on est dans le cas GET : la liste, avec `many=True` (un tableau JSON).

```python
@api_view(["GET", "PUT", "DELETE"])
def acheteur(request, pk):
    obj = get_object_or_404(Acheteur, pk=pk)          # 404
    if request.method == "PUT":
        serializer = AcheteurSerializer(obj, data=request.data)   # obj = on modifie l'existant
        ...                                                        # 422 ou save() puis 200
    if request.method == "DELETE":
        obj.delete()
        return Response(status=204)                    # 204, sans corps
    return Response(AcheteurSerializer(obj).data)      # GET : 200
```

Remarque : passer `obj` en premier argument du serializer (`AcheteurSerializer(obj, data=...)`) indique à DRF qu'il s'agit d'une **modification** et non d'une création. C'est aussi ce qui évite qu'un producteur soit refusé comme « doublon de lui-même » lors d'un PUT.

**Les vues du producteur et de la livraison (squelette)** : les TODO sont numérotés.

| TODO | Vue | Contenu à écrire |
|---|---|---|
| 1 | `producteurs` (POST) | Créer un producteur |
| 2 | `producteurs` (GET) | La liste |
| 3 | `producteur` | Lire, modifier (PUT), supprimer (DELETE), avec la protection 409 |
| 4 | `stock_producteur` | `GET /producteurs/{id}/stock` |
| 5 | `livraisons` (POST) | Créer une livraison, valider, appeler le service, traduire les erreurs |
| 6 | `livraisons` (GET) | La liste |

`livraison` (lecture d'une livraison par id) est **déjà écrite** : elle ne fait pas partie des TODO.

### 5.13 `api/urls.py` (aiguillage)

```python
urlpatterns = [
    path("acheteurs", views.acheteurs),
    path("acheteurs/<int:pk>", views.acheteur),
    path("producteurs", views.producteurs),
    path("producteurs/<int:pk>", views.producteur),
    path("producteurs/<int:pk>/stock", views.stock_producteur),
    path("livraisons", views.livraisons),
    path("livraisons/<int:pk>", views.livraison),
]
```

- `<int:pk>` capture un entier dans l'adresse et le passe à la vue sous le nom `pk`. `/api/producteurs/abc` ne correspond donc à rien et donne 404 avant même d'arriver dans ta vue.
- **Le verbe n'est jamais dans l'adresse** : on écrit `POST /api/producteurs`, pas `/ajouterProducteur`. Le nom de la ressource est au pluriel.
- Ce fichier est complet : tu n'as rien à y ajouter pour la séance.

### 5.14 `api/templates/console.html`

La page de la console, servie sur `/console/`. Elle contient deux onglets.

- **Requête** : choisis un verbe, une adresse et un corps JSON, puis « Envoyer ». La réponse affiche le **code HTTP** en vert (2xx) ou en rouge, plus le JSON. Des boutons d'exemples préremplissent les requêtes courantes. Si ton JSON est mal formé (virgule en trop, guillemets simples), la console te le dit **avant** d'envoyer.
- **Recette** : « Lancer la vérification » exécute tous les points et affiche trois scores : Socle (sur 9), Cible (sur 11), Défi (sur 5). Chaque point rouge donne la cause précise et un **indice** renvoyant à une carte de l'annexe D.

La page ne contient que l'affichage. La logique des tests est dans `recette.js`.

### 5.15 `api/static/console/recette.js` (la logique de la recette)

C'est le « jury » automatique. Il envoie de vraies requêtes à ton API et compare les codes reçus à ceux du contrat.

Les briques :

| Élément | Rôle |
|---|---|
| `appel(methode, chemin, corps)` | Envoie une requête et renvoie `{status, json, ...}`. Si le serveur est arrêté, `status` vaut 0 (« Failed to fetch ») |
| `attendu(res, code)` | Compare le code reçu au code attendu, et traduit les cas courants : 501 = TODO non écrit, 500 = erreur dans ton code |
| `t(id, niveau, titre, carte, indice, run)` | Déclare un point de recette |
| `suf` | Suffixe unique (basé sur l'heure) ajouté aux noms de test, pour pouvoir relancer la recette sans conflit de doublons |
| `lancer()` | Exécute tous les points dans l'ordre et renvoie le bilan |

Chaque test partage un petit objet `c` qui garde les identifiants créés (`c.id1`, `c.pid`...). Si un point en amont échoue, les points dépendants affichent « dépend de S1 » plutôt qu'une erreur trompeuse.

**Les points vérifiés**

| Niveau | Points | Ce que ça vérifie |
|---|---|---|
| **Socle (9)** | S1 à S9 | POST 201, GET 200, GET inconnu 404, POST sans nom 422, nom vide 422, liste, PUT 200, doublon 422, DELETE 204 puis 404 |
| **Cible (11)** | C0 à C10 | C0 prépare un producteur. C1 entrée 201. C2 à C5 : poids négatif, nul, producteur inconnu, sens inconnu → 422. C6 sortie > stock → 409. C7 le stock vaut toujours 40 après le refus. C8 sortie de 15 → 25 restants. C9 sortie égale au stock → 0. C10 suppression avec livraisons → 409 |
| **Défi (5)** | D1 à D5 | Pagination, `X-Total-Count`, filtre, forme d'erreur 404/422, forme d'erreur 409 |

Tu peux **ajouter ton propre point** en copiant une ligne `t("X1", ...)`. Le fichier est écrit sans dépendance au navigateur : il peut aussi s'exécuter dans Node.

### 5.16 `variantes/` et `etapes/`

- `variantes/squelette/` : les trois fichiers de départ (`views.py`, `serializers.py`, `services.py`) avec les TODO.
- `variantes/solution/` : la même chose, complète et testée (Socle 9/9, Cible 11/11). **À n'ouvrir qu'en dernier recours** : le transfert de l'exemple vers le producteur est ton travail.
- `etapes/` : les 4 étapes de l'exemple de l'acheteur, en fichiers courts : modèle, serializer, vue, routes.

### 5.17 `appliquer.sh` et `appliquer.bat`

```bash
./appliquer.sh squelette     # Windows : appliquer.bat squelette
```

Le script copie les trois fichiers de `variantes/<nom>/` dans `api/`, puis crée le marqueur `.variante_appliquee`. Si ce marqueur existe déjà, **il refuse de recommencer**, pour ne pas écraser ton travail. Pour forcer : `./appliquer.sh squelette --force`. **Attention : cela efface tout ce que tu as écrit.**

---

## 6. Ce que tu dois coder maintenant

Tu as déjà fait (ou tu fais) la **Phase 0** : le serveur tourne, la console affiche **0 sur 9**.

Méthode : **une étape, une vérification à la console, puis la suivante.** Lis chaque point rouge et son indice avant de toucher au code. Je donne ici la démarche et les outils à utiliser, pas le code complet : c'est à toi de transférer l'exemple de l'acheteur.

### Phase 1 · API Producteur → viser Socle 9 sur 9

Tout se passe dans `api/views.py`.

#### Étape 1.1 · Lire l'exemple résolu (8 min)
- Lis la section « exemple résolu » de `views.py` et le dossier `etapes/`.
- Note dans le journal, en une phrase, le rôle de chaque pièce : modèle, serializer, vue, routes.
- Réponds : quelle pièce renvoie 404 ? 422 ? Laquelle choisit les champs visibles ?

#### Étape 1.2 · Dessiner le schéma (5 min)
- Deux tables, clés primaires soulignées, flèche de la clé étrangère `producteur_id`, le **1** et le **N**.
- Écris ce qui arrive si on supprime un producteur qui a des livraisons.
- Le secrétaire prend une photo pour le journal.

#### Étape 1.3 · TODO 1, créer un producteur (12 min)
Dans `producteurs(request)`, branche `POST`, remplace `return a_faire(1)`.

À faire, dans l'ordre :
1. Construire `ProducteurSerializer(data=request.data)`.
2. Si `is_valid()` est faux : répondre **422** avec `{"message": "Donnees invalides", "errors": serializer.errors}`.
3. Sinon : `save()`, puis répondre avec les données du producteur créé et `status=201`.

Vérifie à la console (onglet Requête) :

| Requête | Résultat attendu |
|---|---|
| POST `{"nom": "Awa", "village": "Orodara"}` | 201 |
| Le même POST une deuxième fois | 422 (doublon, jamais 500) |
| POST `{}` | 422 |
| POST `{"nom": ""}` | 422 |

Recette : **S1, S4, S5, S8**.

#### Étape 1.4 · TODO 2 et TODO 3, lire (8 min)
- **TODO 2** (branche GET de `producteurs`) : renvoyer la liste avec `many=True`.
- **TODO 3** (vue `producteur`) : chercher le producteur avec `get_object_or_404`, puis, pour un GET, le renvoyer avec le serializer.

Vérifie : GET `/api/producteurs/{id}` → 200 ; GET `/api/producteurs/999999` → 404. Recette : **S2, S3, S6**.

#### Étape 1.5 · TODO 3, branche PUT (6 min)
- Construire le serializer avec l'objet existant **et** les données : `ProducteurSerializer(obj, data=request.data)`.
- Invalide → **422** (comme un POST invalide). Valide → `save()` puis **200** avec le producteur modifié.

Vérifie : PUT `{"nom": "Awa Traoré"}` → 200 avec le nouveau nom. Recette : **S7**.

#### Étape 1.6 · TODO 3, branche DELETE (5 min)
- `obj.delete()` puis `Response(status=204)`, sans corps.
- Pour l'instant, ne t'occupe pas du cas « il a des livraisons » : c'est la phase 2.

Vérifie : DELETE → 204, puis GET du même id → 404. Recette : **S9**.

#### Étape 1.7 · Passer le Socle (5 min)
- Onglet Recette → « Lancer la vérification » : **S1 à S9 verts**.
- **Lève la main** : le formateur vient voir.
- Commit : `API Producteur : créer, lire, modifier, supprimer`.

### Phase 2 · Livraison et stock → viser Cible 11 sur 11

Cette phase est plus autonome. **Avant de commencer**, le Critique pose la question : **« Et si deux agents expédient en même temps ? »** Réfléchissez deux minutes, sans coder, et notez la réponse dans le journal.

#### Étape 2.1 · Schéma complet et règle (5 min)
Ajoute sur ton dessin la règle du stock et son code **409**. Réponds : où va la règle, dans la route, dans le client, ou dans une couche réutilisable ? (Réponse attendue : la couche réutilisable, donc `services.py`.)

#### Étape 2.2 · Valider une livraison, 422 (12 min)
Fichier : `api/serializers.py`, classe `LivraisonSerializer`.
- Ajoute la méthode `validate_poids_kg(self, value)` qui lève `serializers.ValidationError` avec un message lisible si `value <= 0`, et renvoie `value` sinon.
- Le `sens` inconnu et le `producteur` inexistant sont **déjà** refusés par le `ModelSerializer`.

Remarque : ces points (C2 à C5) ne passeront qu'**après** l'étape 2.3, car la vue des livraisons n'est pas encore écrite et répond 501.

#### Étape 2.3 · Créer une livraison, 201 (10 min)
Trois morceaux :

1. **`services.py`, `enregistrer_livraison`** : créer la livraison avec `Livraison.objects.create(...)` et la renvoyer. (Pas encore de règle du stock.)
2. **`views.py`, TODO 5** (POST de `livraisons`) :
   - valider avec `LivraisonSerializer` ; invalide → **422** `{"message", "errors"}` ;
   - appeler `services.enregistrer_livraison(**serializer.validated_data)` ;
   - répondre **201** avec la livraison créée.
3. **`views.py`, TODO 6** (GET de `livraisons`) : la liste avec `many=True`.

Astuce : `validated_data` contient déjà `producteur` sous forme d'**objet** `Producteur`, pas d'un simple id.

Vérifie : POST `{"producteur": ID, "variete": "Kent", "poids_kg": 40, "sens": "entree"}` → 201 ; GET `/api/livraisons` → 200. Recette : **C0, C1**, puis **C2 à C5** passent.

#### Étape 2.4 · Calculer le stock (10 min)
1. **`services.py`, `calculer_stock`** : deux sommes filtrées, entrées et sorties, avec `Livraison.objects.filter(producteur_id=..., sens=...).aggregate(Sum("poids_kg"))`. **Attention** : la somme vaut `None` s'il n'y a aucune ligne (pense à `or 0`). Renvoie entrées − sorties.
2. **`views.py`, TODO 4** : `get_object_or_404(Producteur, pk=pk)`, puis `Response({"producteur_id": ..., "stock_kg": ...})` en appelant `services.calculer_stock`.

Question à noter dans le journal : **pourquoi le stock n'est-il pas une colonne ?**

Vérifie : après une entrée de 40 kg, GET `/api/producteurs/{id}/stock` → `{"producteur_id": …, "stock_kg": 40}`.

#### Étape 2.5 · La règle, une sortie trop grande donne 409 (12 min)
1. **`services.py`, `enregistrer_livraison`** : **avant** de créer, si `sens == "sortie"` et `poids_kg` dépasse le stock, lever `StockInsuffisant(disponible, demande)`.
2. **`views.py`, TODO 5** : entourer l'appel au service d'un `try/except services.StockInsuffisant` et répondre **409** avec `{"message": str(erreur), "errors": None}`.

Cas limite à respecter : **une sortie égale au stock est permise** (le stock tombe à 0). C'est donc une comparaison **stricte** (`>`), pas `>=`.

Vérifie, avec 40 kg en stock :

| Action | Résultat attendu |
|---|---|
| Sortie de 50 kg | **409**, et le stock vaut toujours 40 |
| Sortie de 15 kg | 201, le stock passe à 25 |
| Sortie de 25 kg | 201, le stock tombe à 0 |

Recette : **C6, C7, C8, C9**.

#### Étape 2.6 · Protéger la suppression, 409 (6 min)
Dans `views.py`, TODO 3, branche DELETE : entoure `obj.delete()` d'un `try/except ProtectedError` et réponds **409** avec un message lisible. Sans livraison, le DELETE reste un **204**.

Recette : **C10**.

#### Étape 2.7 · Passer la Cible (5 min)
- Recette : **C0 à C10 verts** (11 sur 11). Lève la main.
- Commit : `Livraison, stock et règle du stock (409)`.

### Phase 3 · Défi et restitution (35 min)

Si la Cible n'est pas finie, **termine la Cible** : c'est tout aussi valable. Sinon, choisis **un** défi.

| Défi | Ce qu'il faut faire | Recette | Piste |
|---|---|---|---|
| **Pagination** | `GET /api/livraisons?page=2&per_page=10` renvoie une portion. Plafond raisonnable pour `per_page`. Total dans l'en-tête `X-Total-Count` | D1, D2 | Lire `request.query_params`, découper le queryset, puis `reponse["X-Total-Count"] = total` |
| **Filtre** | `?producteur_id=3` ne renvoie que ses livraisons. C'est un **paramètre**, pas une nouvelle route | D3 | Filtrer le queryset **avant** de paginer |
| **Erreurs structurées** | Toutes les erreurs (404, 409, 422) ont la forme `{"message": ..., "errors": ...}` | D4, D5 | Une fonction unique qui construit la réponse d'erreur. Le 404 de `get_object_or_404` a une forme différente : remplace-le |
| **Index** | Un index sur `livraisons.producteur_id` | — | Dans `Livraison.Meta`, ajouter `indexes = [models.Index(fields=["producteur"])]`, puis `makemigrations` et `migrate`. Explique le compromis : lecture plus rapide, écriture un peu plus lente. Mesure avant de décider |

#### Les 10 dernières minutes
- [ ] **Git** : chaque membre a au moins un commit (sinon il en fait un maintenant, même une correction du journal).
- [ ] **Auto-évaluation** : chacun, **seul**, place une croix sur l'échelle de l'annexe G.
- [ ] **Restitution flash** : le présentateur choisit à la console **un appel qui échoue** (un 422 ou un 409) et prépare une minute : pourquoi ce code et pas un autre ?
- [ ] **Réponse au Critique** : « Et si deux agents expédient en même temps ? » Note la réponse de l'équipe.
- [ ] **Journal** : photo du schéma, résultat de la recette, invites IA.

> Piste pour la question du Critique : deux sorties simultanées peuvent chacune vérifier le stock avant que l'autre n'ait écrit, et passer toutes les deux. Il faut que la vérification et l'écriture se fassent comme **une seule opération indivisible** (transaction, verrou sur la ligne du producteur). À toi de formuler la réponse avec tes mots.

---

## 7. Git, journal de bord et restitution

### Git : un commit chacun

```bash
git init
git config user.name "Ton Nom"
git config user.email "toi@exemple.com"
git add .
git commit -m "kit MangoTrack S2 : point de depart"
git log --oneline
```

Un bon message dit **ce qui change et pourquoi** : « ajoute la validation du poids », pas « modif ». Commits suggérés : fin du Socle, fin de la Cible, défi.

### Les quatre rôles, qui tournent à chaque phase

| Rôle | Ce qu'il fait |
|---|---|
| **Chef d'équipe** | Lit l'énoncé, découpe le travail, surveille l'heure, décide quand demander de l'aide |
| **Secrétaire technique** | Tient le journal, note les décisions et les invites IA, fait les commits, photographie le schéma |
| **Présentateur** | Prépare la restitution, reformule à voix haute ce que fait l'équipe |
| **Critique** | Pose la question qui dérange, vérifie les réponses de l'IA, relit chaque code HTTP |

Un seul clavier à la fois : le **pilote** tape, le **copilote** lit et questionne. On échange toutes les 20 minutes.

### La règle « trois avant moi »
1. Lis le message d'erreur **en entier**.
2. Demande à ton équipe, puis regarde l'exemple résolu et les cartes d'indices.
3. Reproduis le problème à la console avec la requête la plus courte possible.

### L'IA est autorisée, à trois conditions
- Tu **notes l'invite** dans le journal.
- Tu **lis la réponse** avant de la coller.
- Tu peux **expliquer chaque ligne** que tu gardes. Le Critique vérifie au moins une réponse : est-ce le bon code HTTP ? la règle est-elle au bon endroit ?

---

## 8. Après la séance : faire évoluer le projet

Le kit est conçu en couches pour grandir. Toute nouvelle ressource suit **les mêmes cinq pièces** (par exemple `Acheteur`, puis `Commande`).

| # | Pièce | Fichier | Remarque |
|---|---|---|---|
| 1 | Modèle | `api/models.py` | Puis `makemigrations` et `migrate` |
| 2 | Serializer | `api/serializers.py` | Laisse le `ModelSerializer` lire le modèle |
| 3 | Service | `api/services.py` | **Seulement** s'il y a une règle métier |
| 4 | Vue | `api/views.py` | Choisit 200, 201, 204, 404, 409, 422 |
| 5 | Route | `api/urls.py` | Adresse au pluriel, sans verbe |

Puis ajoute le point de recette correspondant dans `recette.js`.

Évolutions naturelles, dans l'esprit « Applications N-tiers & DevOps » :

1. **Tests automatisés** : écrire `api/tests.py` et lancer `python manage.py test`. La règle du stock se teste très bien directement sur `services.py`, sans HTTP.
2. **Pagination et filtres** globaux sur toutes les listes.
3. **Base PostgreSQL** à la place de SQLite (le verrou de ligne contre les expéditions simultanées devient alors réellement effectif).
4. **Authentification** des agents (qui a enregistré quelle sortie) et traçabilité d'un lot vers l'acheteur.
5. **Conteneurisation** (Docker) et **intégration continue** : lancer les tests à chaque commit.

---

## 9. Dépannage

| Tu vois… | Cause probable | Ce que tu fais |
|---|---|---|
| « Failed to fetch » dans la console | Serveur arrêté ou mauvaise adresse | Relance `python manage.py runserver`, ouvre `/` ou `/console/` |
| `no such table` | Migrations non lancées | `python manage.py migrate` |
| 404 sur `/` | Ancienne version du kit, sans redirection | Voir `config/urls.py` (section 5.5) |
| 400 au lieu de 422 | DRF répond 400 par défaut | Écris `status=422` explicitement |
| 500 sur un doublon | Champ redéclaré dans le serializer | Laisse le `ModelSerializer` lire le modèle |
| `Authentication credentials were not provided` ou CSRF | `REST_FRAMEWORK` modifié | Rétablis le bloc de `settings.py` (section 5.4) |
| 501 | Le TODO de cette route n'est pas écrit | Complète le TODO ou passe à l'étape suivante |
| 500 | Erreur dans ton code | Lis la **première ligne** de l'erreur dans le terminal, puis le fichier et le numéro de ligne |
| La recette dit « Termine d'abord le niveau Socle » | C0 a besoin que `POST /api/producteurs` marche | Termine la phase 1 |
| Port déjà utilisé | Un autre serveur tourne | `python manage.py runserver 8001`, puis `/console/` sur ce port |
| Git : « Please tell me who you are » | Nom non configuré | `git config user.name "Ton Nom"` et `git config user.email "toi@exemple.com"` |
| JSON refusé à la console | Virgule en trop ou oubliée, guillemets simples | Clés et textes entre guillemets **doubles**, pas de virgule après le dernier élément |
| `appliquer.sh` refuse de s'exécuter | Une variante est déjà appliquée | C'est voulu. Ajoute `--force` **seulement** si tu acceptes d'effacer ton travail |

---

*Ce guide complète le `README.md` du kit : le README donne la marche à suivre, ce document explique pourquoi chaque morceau de code existe et ce qu'il reste à écrire.*
