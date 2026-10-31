# Outils Safari pour Google Ads (compte 911-188-2433, campagne 281499394161564)
Prérequis : Safari ouvert sur ads.google.com, « Autoriser JavaScript depuis les événements Apple » coché, Accessibilité accordée à l'app hôte.
- `export TABKEY=ads.google.com` puis `./sjs.sh 'js'` lit la page, `./press.sh 'Libellé exact'` focus + Entrée (fiable), `./sclick.sh 'expr'` vrai clic, `./fill2.sh <idx> "texte"` colle dans le n-ième champ visible.
- Import des 8 groupes : page Outils › Importations (`/aw/bulk/uploads?ocid=8640005932`), bouton + (focus material-fab + Entrée), « Sélectionner une source » → « Importer un fichier », puis `./sjsf.sh inject.js` (injecte ../import-8-gruppi.csv), `./press.sh 'Aperçu'`, lire le résultat, `./press.sh 'Appliquer'` si « Erreurs 0 ».
- Tant que l'aperçu dit « campagne en lecture seule », attendre (annonce en examen / brouillon en cours d'application).
