# Revenus+ — site complet

Cette archive contient le frontend et le backend réellement associés.

## Structure

- `frontend/` : interface HTML/CSS/JavaScript + Nginx
- `backend/` : API FastAPI + SQLAlchemy + JWT
- `docker-compose.yml` : lance les deux services et conserve SQLite dans un volume
- `.env.example` : variables de production

## Déploiement Docker sur un VPS

1. Installer Docker et Docker Compose.
2. Copier l'archive sur le serveur et la décompresser.
3. Créer le fichier `.env` :

```bash
cp .env.example .env
```

4. Générer une clé secrète :

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

5. Mettre cette valeur dans `SECRET_KEY` du `.env`.
6. Remplacer `FRONTEND_URL` par le domaine public, par exemple `https://revenus.mondomaine.com`.
7. Mettre `CORS_ORIGINS` sur ce même domaine.
8. Lancer :

```bash
docker compose up -d --build
```

Le site est alors servi sur le port 80. Pour HTTPS, place un reverse proxy comme Caddy, Nginx Proxy Manager ou Traefik devant le conteneur frontend.

## Vérification

- Site : `http://IP_DU_SERVEUR/`
- API : `http://IP_DU_SERVEUR/api/health`
- Documentation API : `http://IP_DU_SERVEUR/docs`

## Important pour la production

Le projet utilise SQLite pour rester simple et immédiatement déployable. Pour une application multi-utilisateurs importante, remplace `DATABASE_URL` par PostgreSQL et mets en place des sauvegardes.

Le frontend appelle l'API avec des URLs relatives (`/api/...`) : le même domaine sert donc le frontend et relaie les appels API vers FastAPI. Aucun changement d'URL dans le JavaScript n'est nécessaire après déploiement.


## Administration

Revenus+ inclut un espace d'administration protégé par le backend. Il permet de consulter les utilisateurs, les volumes globaux de revenus et dépenses, le journal des activités API et de supprimer un compte utilisateur. Les mots de passe et jetons ne sont jamais enregistrés dans le journal d'activité.

Pour un déploiement Render sans configuration supplémentaire, le **premier compte créé** devient l'administrateur si `ADMIN_EMAILS` n'est pas défini. Pour un usage réel, configurez `ADMIN_EMAILS` dans Render avec l'adresse de l'administrateur avant d'ouvrir le site au public.

## Render

Le fichier `render.yaml` est inclus à la racine. Il crée un Web Service FastAPI, un Static Site frontend et un PostgreSQL Render gratuit. Dans Render, utilisez **New > Blueprint** et connectez le dépôt contenant ce dossier. Aucun secret administrateur n'est demandé : le premier compte créé devient administrateur. Pour un usage réel, vous pouvez ensuite définir `ADMIN_EMAILS` dans les variables du Web Service afin de verrouiller explicitement l'accès.

Attention : le PostgreSQL Render gratuit expire après 30 jours selon les limites actuelles de Render. Les services Web gratuits peuvent aussi se mettre en veille après 15 minutes d'inactivité. Pour conserver les données durablement, passez la base à une offre payante ou utilisez une base externe persistante.
