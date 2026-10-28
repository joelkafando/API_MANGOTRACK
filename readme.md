# MangoTrack · Ce que fait le code complet

*Explication en phrases simples de l'application Django de la séance 2.*

## En une phrase

C'est une petite application qui garde la trace des mangues d'une coopérative : qui les livre, combien il y en a en stock, et qui empêche les erreurs de Salimata.

## Les deux choses qu'elle gère

- Les **producteurs** : les personnes qui apportent des mangues, comme Awa.
- Les **livraisons** : chaque fois qu'un producteur apporte des mangues (une *entrée*) ou que des mangues sortent pour être vendues (une *sortie*).

## Ce que l'application sait faire

Pour les producteurs, elle sait :

- en ajouter un,
- afficher la liste,
- en afficher un seul,
- changer son nom ou son village,
- le supprimer.

Pour les livraisons, elle sait :

- enregistrer une entrée ou une sortie,
- afficher la liste,
- dire combien de kilos il reste en stock pour un producteur.

## Les règles qu'elle impose

1. **Pas de nom vide ni de doublon.** Un producteur doit avoir un nom d'au moins 2 lettres, et deux producteurs ne peuvent pas avoir le même nom. Sinon elle répond **422**.
2. **Pas de poids absurde.** Une livraison de 0 kg ou de -5 kg est refusée (**422**). Un « sens » autre que `entree` ou `sortie` aussi.
3. **Pas de livraison sans producteur.** Chaque livraison doit appartenir à un producteur qui existe. Sinon c'est **422**.
4. **Le stock ne descend jamais sous zéro.** Si le stock est de 40 kg et qu'on veut sortir 50 kg, elle refuse (**409**). Sortir exactement 40 kg est permis.
5. **On n'efface pas l'historique.** Si Awa a des livraisons, on ne peut pas la supprimer (**409**).

## Comment elle calcule le stock

Elle ne garde pas le stock quelque part. Chaque fois qu'on le demande, elle additionne toutes les entrées, puis retire toutes les sorties. Comme ça, le chiffre est toujours juste, parce qu'il vient directement des livraisons.

## Comment elle répond

À chaque demande, elle répond avec un **code** qui dit ce qui s'est passé :

| Code | Ce que ça veut dire |
| --- | --- |
| 200 | Ça a marché |
| 201 | Quelque chose a été créé |
| 204 | Supprimé, rien à afficher |
| 404 | Ça n'existe pas |
| 422 | Ce que tu as envoyé est invalide |
| 409 | Ce que tu demandes est impossible vu l'état actuel |

## Le rôle de chaque morceau

| Fichier | Rôle |
| --- | --- |
| `models.py` | Décrit les tables : à quoi ressemble un producteur et une livraison |
| `serializers.py` | Vérifie que ce qu'on envoie est correct (nom, poids, sens) |
| `services.py` | Contient la règle du stock : il calcule et refuse les sorties trop grandes |
| `views.py` | Reçoit la demande, appelle les bons morceaux et choisit le bon code de réponse |
| `urls.py` | Relie chaque adresse (comme `/api/producteurs`) à la bonne fonction |
| `console.html` et `recette.js` | Le tableau de contrôle : l'un envoie des demandes à la main, l'autre vérifie automatiquement les règles et donne la note (9 sur 9, puis 11 sur 11) |

## Un exemple de bout en bout

Tu envoies : « Awa livre 40 kg de Kent ».

1. L'application vérifie que Awa existe et que 40 est un poids valide.
2. Elle enregistre la livraison et répond **201**.

Ensuite tu envoies : « On sort 50 kg pour Awa ».

1. L'application calcule le stock : 40 kg.
2. 50 est plus grand que 40, donc elle refuse, ne retient rien, et répond **409** avec un message clair.

C'est exactement ce qui évite de retomber sur le fameux « moins quarante kilos ».
