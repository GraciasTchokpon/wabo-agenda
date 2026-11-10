# Wabo – Agenda Bénin : consignes pour mettre à jour les événements

Le site public est la page statique `site/`, publiée par Netlify à chaque envoi sur `main`
(https://wabo-agenda.netlify.app). La source des événements est `data/events.json`.

## Ajouter ou corriger des événements

1. Modifier `data/events.json` (et copier le même contenu dans `web/data/events.json`).
2. Lancer `python3 scripts/build_site.py` : il reconstruit l'accueil, une page par événement,
   ville, catégorie et mois, et `site/sitemap.xml`. Ne jamais modifier `site/` à la main.
3. Vérifier que la page s'affiche (par exemple `python3 -m http.server` dans `site/` et un
   navigateur sans tête) et qu'aucune erreur JavaScript n'apparaît.
4. Commit en français, puis `git push origin main`. Netlify publie en une à deux minutes.

## Format d'un événement

```json
{
 "id": "nom-court-annee",              // minuscules, tirets, unique, stable (sert d'adresse de page)
 "title": "Nom officiel",
 "category": "concert",                // festival, concert, conference, gastronomie, humour, culture,
                                       // soiree, atelier, sport, lancement, salon
 "start": "2026-12-20", "end": "2026-12-20",
 "time": "16:00",                      // facultatif
 "city": "Cotonou",                    // plusieurs villes : "Abomey-Calavi · Kétou · Cotonou"
 "place": "Lieu précis, Cotonou",
 "price": "5 000 FCFA" ,               // ou "Gratuit", "Non communiqué", "Sur inscription"…
 "free": false,
 "tbc": false,                         // true si les dates exactes ne sont pas publiées
 "dateText": "Décembre 2026 – dates à confirmer",   // seulement si tbc = true
 "description": "2 à 4 phrases, en français, écrites avec nos mots (jamais copiées).",
 "link": "https://… ou null",          // inscription ou billetterie officielle
 "sources": [{"label": "Média, date", "url": "https://…"}]
}
```

## Règles de vérification (à respecter strictement)

- Uniquement des événements **au Bénin**, **ouverts au public** (gratuits ou payants), à venir.
- Chaque événement a au moins **une source publique datée** : site officiel, ministère
  (gouv.bj, tourisme.gouv.bj, benin.bj…), Institut français, presse béninoise (Benin Web TV,
  Matin Libre, La Nouvelle Tribune, Banouto, 24 Heures au Bénin…), billetterie officielle.
- Date, lieu ou prix incertains : le dire (« lieu à préciser », « Non communiqué ») ou mettre
  `tbc: true`. Ne jamais inventer.
- Éviter les doublons : comparer avec les événements existants (même nom, même date).
  Mettre à jour la fiche existante plutôt que d'en créer une seconde.
- Ne pas supprimer les événements passés : le site les classe tout seul dans « Déjà passés ».
- Pas d'événements privés (mariages, réunions internes), ni politiques ou religieux de culte
  (les festivals culturels comme les Vodun Days sont acceptés).
- Les sorties « chill » (brunchs, afterworks, soirées plage, pool parties) sont bienvenues
  dès qu'il y a une date précise et un lieu.
