# 📧 Convertisseur Email

Cet outil transforme vos exports SquadEasy (`.xlsx`) en fichiers `.csv` compatibles avec le template attendu.

## 🚀 Utilisation

1. Chargez un fichier `.xlsx`.
2. Colonnes prises en compte :
   - `Prénom adhérent` → `prenom`
   - `Nom adhérent` → `nom`
   - `Email payeur` → `email`
   - `langue`
   - `profil`
3. Le CSV généré contient une seule colonne avec le format :

firstname,lastname,email,langue,profil

## 🌐 Déploiement

1. Créez un repo GitHub `convertisseur-email`.
2. Poussez-y `app.py`, `requirements.txt`, `README.md`, et `logo.png`.
3. Connectez le repo à [Streamlit Cloud](https://streamlit.io/cloud).
4. Déployez → votre app sera accessible à :

https://convertisseur-email.streamlit.app
