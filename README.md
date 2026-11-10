# Wabo – Agenda Bénin

Tous les événements du Bénin au même endroit : concerts, festivals, conférences, soirées, avec les dates, les lieux et les liens d'inscription.

## Le site en ligne aujourd'hui : `site/` sur Netlify

Le site public est la page statique du dossier `site/`, publiée par Netlify (réglages dans `netlify.toml`). Chaque modification envoyée sur la branche `main` est mise en ligne automatiquement.

Pour ajouter ou corriger un événement :

1. Modifier `data/events.json`.
2. Lancer `python3 scripts/build_site.py` (reconstruit `site/index.html` à partir de `site-src/template.html`).
3. Envoyer la modification sur `main`.

Les dossiers ci-dessous sont la version complète (base de données, robot de veille, back-office), à brancher plus tard.

## La version complète

Le projet complet a trois parties :

| Dossier | Rôle | Où ça tourne |
| --- | --- | --- |
| `web/` | Le site (agenda, calendrier, fiches, « Proposer un événement », back-office `/admin`) | Vercel (gratuit pour démarrer) |
| `supabase/` | La base de données : schéma + 10 événements réels vérifiés | Supabase (gratuit pour démarrer) |
| `collector/` | Le robot de veille (flux RSS, sites) + l'extraction par IA + la réception WhatsApp | GitHub Actions (robot) et un petit serveur (WhatsApp) |

Le site fonctionne **même sans base de données** : il affiche alors les événements de `web/data/events.json`. On peut donc le mettre en ligne en premier et brancher Supabase ensuite.

---

## Étape 1 – Mettre le site en ligne (30 minutes)

1. Créez un compte sur [github.com](https://github.com) et un dépôt **privé** `wabo`. Envoyez-y ce dossier (bouton « uploading an existing file », ou `git push`).
2. Créez un compte sur [vercel.com](https://vercel.com) avec GitHub, puis **Add New → Project** et choisissez `wabo`.
3. Dans **Root Directory**, indiquez `web`. Laissez le reste par défaut, cliquez **Deploy**.
4. Le site est en ligne sur une adresse du type `wabo-xxx.vercel.app`.

Pour un vrai nom de domaine (`wabo.bj`, `wabo.africa`…) : achetez-le chez un registraire (pour le `.bj`, vérifiez la liste des registraires agréés), puis dans Vercel **Settings → Domains → Add**, et suivez les instructions DNS.

## Étape 2 – Brancher la base de données (20 minutes)

1. Créez un projet sur [supabase.com](https://supabase.com) (région la plus proche : Europe de l'Ouest).
2. **SQL Editor** → collez et exécutez `supabase/schema.sql`, puis `supabase/seed.sql`.
3. **Project Settings → API** : copiez l'URL, la clé `anon` et la clé `service_role`.
4. Dans Vercel → **Settings → Environment Variables**, ajoutez les variables de `web/.env.example` :
   `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `NEXT_PUBLIC_SITE_URL`, `ADMIN_USER`, `ADMIN_PASSWORD` (et `NEXT_PUBLIC_WABO_WHATSAPP` quand le numéro existe).
5. **Deployments → Redeploy**. Le formulaire « Proposer » enregistre maintenant les propositions, et `/admin` permet de les modérer.

> La clé `service_role` donne tous les droits sur la base : ne la mettez jamais dans du code envoyé au navigateur ni dans un message.

## Étape 3 – Activer le robot de veille (15 minutes)

1. Créez une clé API sur [console.anthropic.com](https://console.anthropic.com) (l'extraction lit les articles et les affiches).
2. Dans GitHub → votre dépôt → **Settings → Secrets and variables → Actions**, ajoutez les secrets `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `ANTHROPIC_API_KEY`.
3. Onglet **Actions** → « Collecte quotidienne » → **Run workflow** pour un premier essai. Ensuite il tourne seul chaque matin.
4. Les nouvelles fiches arrivent dans `/admin` avec le statut « à valider » : rien n'est publié sans votre accord.

Ajouter ou retirer des sources : `collector/config/sources.yaml`. Avant d'activer une source, vérifiez ses conditions d'utilisation et testez l'adresse de son flux (celles marquées « à vérifier »).

Tester en local :

```bash
cd collector
cp .env.example .env          # puis remplissez les valeurs
pip install -r requirements.txt
python -m pytest -q tests
python -m wabo_collector collect   # lit les sources
python -m wabo_collector extract   # crée les fiches à valider
```

## Étape 3 bis – Lire Instagram (et Facebook plus tard) par les API officielles

Le robot lit Instagram **sans scraping**, par l'API officielle « Business Discovery » de Meta : elle donne accès aux publications publiques des comptes **professionnels ou créateurs** (la plupart des lieux, promoteurs et festivals).

1. Créez le compte Instagram de Wabo, passez-le en **compte professionnel** et reliez-le à une page Facebook Wabo.
2. Dans votre app Meta (étape 4 ci-dessous), ajoutez le produit **Instagram** et générez un jeton longue durée avec les permissions `instagram_basic` et `pages_show_list`.
3. Ajoutez `META_ACCESS_TOKEN` et `IG_USER_ID` (identifiant du compte Instagram pro) aux secrets GitHub et au fichier `.env`.
4. Dans `collector/config/sources.yaml`, ajoutez les comptes à suivre (`kind: instagram`, `username: ...`) et passez-les en `active: true`.
5. Hashtags (`kind: instagram_hashtag`) : demandez d'abord la fonctionnalité « Instagram Public Content Access » dans l'examen de l'app Meta ; limite de 30 hashtags différents par 7 jours.
6. Facebook (`kind: facebook_page`) : demandez « Page Public Content Access » (examen Meta + vérification d'entreprise), puis mettez `FACEBOOK_PPCA_ENABLED=1`.

LinkedIn n'offre aucune API pour lire les publications des autres : la veille LinkedIn se fait à la main, en envoyant les annonces repérées au numéro WhatsApp de Wabo (une capture suffit, l'IA lit l'image).

## Étape 4 – Recevoir les affiches par WhatsApp (1 à 2 heures, dont la vérification Meta)

1. Prenez un numéro dédié à Wabo (une SIM qui n'est pas déjà sur l'application WhatsApp).
2. Sur [developers.facebook.com](https://developers.facebook.com) : **Créer une app → type Business → ajouter WhatsApp**. Ajoutez le numéro et faites vérifier votre compte Meta Business.
3. Déployez la réception : par exemple sur [render.com](https://render.com) → **New Web Service** → dépôt `wabo`, dossier `collector`,
   commande de démarrage `uvicorn wabo_collector.whatsapp_webhook:app --host 0.0.0.0 --port $PORT`, avec les variables de `collector/.env.example`.
4. Dans Meta → **WhatsApp → Configuration → Webhook** : URL `https://<votre-service>.onrender.com/webhook`, jeton = `WHATSAPP_VERIFY_TOKEN`, abonnez-vous au champ `messages`.
5. Envoyez une affiche au numéro : elle apparaît dans `/admin`, la personne reçoit un accusé de réception, et le robot la transforme en fiche à valider.

Recevoir des messages ne coûte rien. Les réponses dans les 24 h qui suivent un message reçu (« messages de service ») sont gratuites jusqu'à un certain volume mensuel ; au-delà, Meta facture au message. Vérifiez la grille en vigueur sur la page tarifs de WhatsApp Business.

## Comment ça marche

```
Sources (RSS, sites, WhatsApp, formulaire)
        → raw_items      (tout est gardé tel quel, avec sa source)
        → extraction IA  (titre, dates, lieu, prix, lien + score de confiance + points à vérifier)
        → dédoublonnage  (même événement vu plusieurs fois = une seule fiche, sources fusionnées)
        → events « a_valider »  → validation dans /admin → « publie » → site
```

- Chaque fiche publique affiche ses sources et un bouton « Signaler une erreur ».
- Les pages événements contiennent des données schema.org `Event` : Google peut les afficher dans ses résultats « événements ».
- Fichier `.ics` et lien Google Agenda sur chaque fiche ; partage WhatsApp avec le titre, la date et le lien.

## Cadre légal (Bénin)

- Les données personnelles relèvent du Livre V du Code du numérique (loi 2017-20), contrôlé par l'APDP. Ne publiez que les contacts que l'organisateur a rendus publics ; le contact laissé dans le formulaire n'est jamais affiché.
- Avant d'ouvrir des comptes utilisateurs, renseignez-vous auprès de l'APDP sur les formalités.
- Le robot respecte `robots.txt`, s'identifie (`WABO_USER_AGENT`) et attend entre deux pages. Ne collectez pas Facebook ni Instagram par scraping : leurs conditions l'interdisent.

## Mettre à jour les événements sans base de données

Modifiez `web/data/events.json` (même format que les fiches existantes) et redéployez. Champs : `id`, `title`, `category`, `start`, `end` (AAAA-MM-JJ), `city`, `place`, `price`, `free`, `tbc` (dates à confirmer), `description`, `link`, `sources`.
