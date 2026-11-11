# Ligne de Front

Jeu de tactique d'escouade au tour par tour, dans le style des jeux mobiles de combat
de soldats (déplacement sur grille, couverture, pourcentage de toucher, progression des
soldats entre les missions).

Tout tient dans un seul fichier : `index.html`. Aucune installation.

## Jouer

- **Sur ordinateur** : ouvrez `index.html` dans un navigateur.
- **Sur téléphone** : copiez le fichier sur le téléphone et ouvrez-le dans le navigateur,
  ou activez GitHub Pages sur le dépôt et ouvrez `…/ligne-de-front/`.

La campagne est sauvegardée automatiquement dans le navigateur.

## Règles

- Chaque soldat peut **se déplacer** puis faire **une action** (tirer, compétence,
  se mettre à couvert). Tirer ou agir termine son tour.
- **Sacs de sable** : couverture partielle (−20 % pour être touché).
  **Murs** : couverture totale (−40 %) et ils bloquent la ligne de vue.
- Une cible sans couverture de votre côté est **prise de flanc** : +10 % pour la toucher
  et 35 % de chances de coup critique (×1,5).
- La précision baisse avec la distance (sauf pour le sniper).
- **À couvert** : −15 % pour vous toucher jusqu'à votre prochain tour.

| Classe      | PV | Précision | Dégâts | Portée | Particularité |
|-------------|----|-----------|--------|--------|---------------|
| Fusilier    | 10 | 70 %      | 3–5    | 7      | Polyvalent |
| Mitrailleur | 13 | 62 %      | 4–7    | 5      | Robuste, courte portée |
| Sniper      | 7  | 82 %      | 5–8    | 12     | Ne tire pas s'il a bougé |
| Grenadier   | 10 | 65 %      | 3–4    | 6      | Grenade 3×3 qui ignore la couverture (tous les 3 tours) |
| Médecin     | 9  | 65 %      | 2–4    | 6      | Soigne un allié adjacent de 5 PV (tous les 2 tours) |

Entre les missions : l'or sert à recruter (8 soldats max, 4 déployés, puis plus avec
l'avancée de la campagne). Les éliminations donnent de l'XP ; chaque niveau donne
+1 PV, +4 % de précision et +1 dégât tous les 2 niveaux. Un soldat tombé au combat
est perdu définitivement.
