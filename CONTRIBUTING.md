# Guide de contribution — S2_demo_django

Ce fichier explique comment installer le projet et comment travailler ensemble sur GitHub.
Merci de le lire avant votre première contribution.

---

## 1. Installation (une seule fois)

### Récupérer le projet

```bash
git clone https://github.com/joelkafando/API_MANGOTRACK.git
cd S2_demo_django
```

### Créer et activer l'environnement virtuel

```bash
python -m venv venv
```

Activation selon votre système :

| Système | Commande |
| --- | --- |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| Windows (CMD) | `venv\Scripts\activate.bat` |
| Linux / macOS | `source venv/bin/activate` |

> Si PowerShell refuse d'exécuter le script, lancez une seule fois :
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Installer les dépendances et préparer la base

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Le projet est accessible sur http://127.0.0.1:8000/

---

## 2. Travail au quotidien

Chaque nouvelle tâche suit ce cycle. **Ne jamais travailler directement sur `main`.**

```bash
# 1. Récupérer la dernière version
git checkout main
git pull origin main

# 2. Créer une branche pour la tâche
git checkout -b feature/nom-de-la-tache

# 3. Travailler, puis enregistrer
git add .
git commit -m "feat: description courte de la modification"

# 4. Envoyer la branche sur GitHub
git push -u origin feature/nom-de-la-tache
```

---

## 3. Pull Request et relecture

1. Sur GitHub, cliquez sur **Compare & pull request** (ou lancez `gh pr create`).
2. Décrivez ce que vous avez fait et pourquoi.
3. Un camarade relit le code, laisse ses commentaires, puis fusionne la Pull Request dans `main`.

Après la fusion :

```bash
git checkout main
git pull origin main
git branch -d feature/nom-de-la-tache
```

---

## 4. En cas de conflit

```bash
git checkout feature/ma-branche
git pull origin main
# Corrigez les fichiers marqués <<<<<<< ======= >>>>>>>
git add .
git commit -m "fix: résolution des conflits"
git push
```

Après un `git pull` qui apporte de nouveaux modèles ou dépendances, pensez à lancer :

```bash
pip install -r requirements.txt
python manage.py migrate
```

---

## 5. Règles de l'équipe

### Noms de branches

| Préfixe | Usage | Exemple |
| --- | --- | --- |
| `feature/` | Nouvelle fonctionnalité | `feature/api-articles` |
| `fix/` | Correction de bug | `fix/erreur-login` |
| `docs/` | Documentation | `docs/readme` |
| `refactor/` | Réorganisation du code | `refactor/services` |

### Messages de commit

| Préfixe | Signification |
| --- | --- |
| `feat:` | Ajout d'une fonctionnalité |
| `fix:` | Correction d'un bug |
| `docs:` | Documentation |
| `refactor:` | Amélioration du code sans changer le comportement |
| `chore:` | Configuration, dépendances, maintenance |

### À ne jamais envoyer sur GitHub

- `venv/`, `db.sqlite3`, `.env`, `__pycache__/`
- Les mots de passe et la `SECRET_KEY`

Si vous ajoutez une bibliothèque, mettez à jour `requirements.txt` :

```bash
pip freeze > requirements.txt
```
