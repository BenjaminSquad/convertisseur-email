import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
import os

# Configuration de la page
st.set_page_config(page_title="Convertisseur Email", page_icon="📧", layout="centered")

# Chargement du logo (robuste)
logo_path = "logo.png"  # Assure-toi que ton fichier s'appelle bien logo.png (sans espace) et qu'il est dans ton repo
if os.path.exists(logo_path):
    try:
        img = Image.open(logo_path)
        st.image(img, width=120)
    except Exception:
        st.warning("⚠️ Le logo n'a pas pu être chargé. Affichage du titre à la place.")
        st.title("Convertisseur Email")
else:
    st.title("Convertisseur Email")

st.markdown("## Convertisseur Email")
st.markdown("Bienvenue sur l’outil **Convertisseur Email** 🎯")

# 🔹 Bloc consignes (mis à jour)
st.markdown(
    """
    <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; margin-bottom:20px;">
    ℹ️ <b>Consignes pour utiliser l’outil :</b><br><br>
    - Le fichier doit être un export <b>Squadeasy</b> au format <code>.xlsx</code><br>
    - Les colonnes attendues sont exactement :<br>
      • <b>nom</b><br>
      • <b>prénom</b><br>
      • <b>email</b><br>
      • <b>langue</b><br>
      • <b>profil</b><br>
    - Une colonne <b>entité</b> peut être présente. Si c’est le cas, elle sera incluse automatiquement dans le CSV final ✅
    </div>
    """,
    unsafe_allow_html=True
)

# Upload fichier
uploaded_file = st.file_uploader("Déposez un fichier Excel exporté de Squadeasy", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Lecture du fichier
        df = pd.read_excel(uploaded_file)

        # Vérif colonnes obligatoires
        colonnes_requises = ["Nom adhérent", "Prénom adhérent", "Email payeur", "langue", "profil"]
        if all(col in df.columns for col in colonnes_requises):
            
            # Renommer les colonnes
            df = df.rename(columns={
                "Nom adhérent": "nom",
                "Prénom adhérent": "prénom",
                "Email payeur": "email"
            })
            
            # Cas où la colonne "entité" existe
            if "entité" in df.columns:
                df["fusion"] = (
                    df["nom"].astype(str) + "," +
                    df["prénom"].astype(str) + "," +
                    df["email"].astype(str) + "," +
                    df["langue"].astype(str) + "," +
                    df["profil"].astype(str) + "," +
                    df["entité"].astype(str)
                )
            else:
                df["fusion"] = (
                    df["nom"].astype(str) + "," +
                    df["prénom"].astype(str) + "," +
                    df["email"].astype(str) + "," +
                    df["langue"].astype(str) + "," +
                    df["profil"].astype(str)
                )

            # Préparer fichier CSV
            output = BytesIO()
            df[["fusion"]].to_csv(output, index=False, header=False, encoding="utf-8")
            output.seek(0)

            st.success("✅ Fichier converti avec succès !")

            # 🔹 Affichage d’un aperçu des 5 premières lignes
            st.markdown("### 👀 Aperçu des 5 premières lignes générées")
            st.dataframe(df[["fusion"]].head(5))

            # Bouton de téléchargement
            st.download_button(
                label="📥 Télécharger le CSV final",
                data=output,
                file_name="final_template.csv",
                mime="text/csv"
            )

        else:
            st.error("❌ Colonnes manquantes dans le fichier importé. Vérifiez le format.")
    
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
