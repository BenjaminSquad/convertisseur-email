import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
import os
import unicodedata
import re

# -------------------------
# Helper : normalisation
# -------------------------
def normalize_colname(s):
    """normalise un nom de colonne : minuscules, supprime accents, espaces et ponctuation"""
    if not isinstance(s, str):
        s = str(s)
    s = s.strip().lower().replace('\xa0', ' ')
    # retire accents
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    # garde uniquement lettres/nombres
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

# Synonymes acceptés (normalisés) pour chaque champ attendu
SYNONYMS = {
    "nom": ["nom", "nomadherent", "nomadh", "lastname", "surname"],
    "prenom": ["prenom", "prenomadherent", "prenomadh", "firstname", "givenname"],
    "email": ["email", "emailpayeur", "emailpayer", "email_payeur", "payeremail"],
    "langue": ["langue", "language", "lang"],
    "profil": ["profil", "profile"],
    "entite": ["entite", "entiteorganisation", "entité", "entity", "entityname", "entity_name"]
}

def find_column_mapping(df_cols):
    """
    Essaie d'identifier les colonnes du DataFrame en comparant les noms normalisés
    avec les synonymes. Retourne mapping dict (key -> original colname) ou None si manquant.
    """
    norm_map = {normalize_colname(c): c for c in df_cols}
    mapping = {}
    for key, synonyms in SYNONYMS.items():
        found = None
        for syn in synonyms:
            if syn in norm_map:
                found = norm_map[syn]
                break
        # fallback : chercher si le nom normalisé contient le synonyme (pour cas bizarres)
        if not found:
            for ncol, orig in norm_map.items():
                for syn in synonyms:
                    if syn in ncol or ncol in syn:
                        found = orig
                        break
                if found:
                    break
        if found:
            mapping[key] = found
    return mapping

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Convertisseur Email", page_icon="📧", layout="centered")

# Logo
logo_path = "logo.png"
if os.path.exists(logo_path):
    try:
        img = Image.open(logo_path)
        st.image(img, width=120)
    except Exception:
        st.title("Convertisseur Email")
else:
    st.title("Convertisseur Email")

st.markdown("## Convertisseur Email")
st.markdown("Bienvenue sur l’outil **Convertisseur Email** 🎯")

# Consignes (mise à jour)
st.markdown(
    """
    <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; margin-bottom:20px;">
    ℹ️ <b>Consignes pour utiliser l’outil :</b><br><br>
    - Le fichier doit être un export <b>Squadeasy</b> au format <code>.xlsx</code><br>
    - Les colonnes attendues sont exactement (ou des variantes acceptées) :<br>
      • <b>nom</b><br>
      • <b>prénom</b><br>
      • <b>email</b><br>
      • <b>langue</b><br>
      • <b>profil</b><br>
    - Une colonne <b>entité</b> peut être présente : si oui elle sera ajoutée à la fin du CSV.
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Déposez un fichier Excel exporté de Squadeasy (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # On essaye deux lectures au cas où l'en-tête réel serait sur la 2e ligne
    tried_headers = [0, 1]
    df = None
    last_error = None
    for hdr in tried_headers:
        try:
            df_try = pd.read_excel(uploaded_file, header=hdr)
            # si on a effectivement des colonnes, on garde
            if df_try is not None and len(df_try.columns) > 0:
                df = df_try
                break
        except Exception as e:
            last_error = e
    if df is None:
        st.error(f"Impossible de lire le fichier Excel. Erreur: {last_error}")
    else:
        st.write("Colonnes détectées dans le fichier :", list(df.columns))
        mapping = find_column_mapping(df.columns)

        # Vérif présence colonnes obligatoires
        required_keys = ["nom", "prenom", "email", "langue", "profil"]
        missing = [k for k in required_keys if k not in mapping]
        if missing:
            st.error("❌ Colonnes manquantes ou non reconnues : " + ", ".join(missing))
            st.info("Colonnes détectées (raw) : " + ", ".join(list(df.columns)))
            st.markdown(
                "Si tu veux, copie-colle ici la première ligne d’en-têtes telle qu'elle apparaît ; je te dirai comment la renommer."
            )
        else:
            # on a les colonnes nécessaires
            # on renomme localement pour usage simple
            df = df.rename(columns={
                mapping["nom"]: "nom",
                mapping["prenom"]: "prénom",
                mapping["email"]: "email",
                mapping["langue"]: "langue",
                mapping["profil"]: "profil"
            })

            # entité facultative
            entite_present = "entite" in mapping
            if entite_present:
                df = df.rename(columns={mapping["entite"]: "entité"})

            # Nettoyage léger
            for c in ["nom", "prénom", "email", "langue", "profil"] + (["entité"] if entite_present else []):
                if c in df.columns:
                    df[c] = df[c].astype(str).str.strip()

            # Construire la colonne fusionnée (ordre : firstname,lastname,email,langue,profil[,entity])
            if entite_present:
                header_name = "firstname,lastname,email,langue,profil,entity"
                single_col = df["prénom"].astype(str) + "," + df["nom"].astype(str) + "," + df["email"].astype(str) + "," + df["langue"].astype(str) + "," + df["profil"].astype(str) + "," + df["entité"].astype(str)
            else:
                header_name = "firstname,lastname,email,langue,profil"
                single_col = df["prénom"].astype(str) + "," + df["nom"].astype(str) + "," + df["email"].astype(str) + "," + df["langue"].astype(str) + "," + df["profil"].astype(str)

            final_df = pd.DataFrame({header_name: single_col})

            # Aperçu
            st.markdown("**Aperçu (5 premières lignes) :**")
            st.dataframe(final_df.head())

            # Préparer et proposer le téléchargement (UTF-16 avec ; pour compatibilité template)
            output = BytesIO()
            final_df.to_csv(output, sep=";", index=False, encoding="utf-16")
            output.seek(0)

            st.success("✅ Fichier prêt.")
            st.download_button(
                label="📥 Télécharger le CSV final",
                data=output.getvalue(),
                file_name="final_template.csv",
                mime="text/csv"
            )
