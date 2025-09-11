import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Convertisseur Email", page_icon="📧", layout="centered")

# --- LOGO + TITRE ---
st.image("logo.png", width=120)
st.title("Convertisseur Email")
st.markdown("""
Bienvenue sur l’outil **Convertisseur Email** 🎯  
Chargez un export Squadeasy (.xlsx), et récupérez automatiquement un `.csv` prêt à l’emploi.
""")

# --- UPLOAD ---
uploaded_files = st.file_uploader(
    "Déposez un ou plusieurs fichiers Excel (.xlsx)", 
    type=["xlsx"], 
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        try:
            # Lire le fichier
            df = pd.read_excel(file)

            # Normaliser noms de colonnes
            df = df.rename(columns={
                "Prénom adhérent": "prénom",
                "Nom adhérent": "nom",
                "Email payeur": "email"
            })

            # Colonnes attendues
            required_cols = ["prénom", "nom", "email", "langue", "profil"]
            if not all(col in df.columns for col in required_cols):
                st.error(f"❌ Le fichier {file.name} ne contient pas toutes les colonnes attendues ({', '.join(required_cols)}).")
                continue

            # Nettoyer
            for col in required_cols:
                df[col] = df[col].astype(str).str.strip()

            # Fusionner
            header = "firstname,lastname,email,langue,profil"
            single_col = df.apply(
                lambda r: f"{r['prénom']},{r['nom']},{r['email']},{r['langue']},{r['profil']}", axis=1
            )
            final_df = pd.DataFrame({header: single_col})

            # Export CSV en mémoire
            output = io.BytesIO()
            final_df.to_csv(output, sep=";", index=False, encoding="utf-16")
            output.seek(0)

            # Bouton téléchargement
            st.success(f"✅ Fichier {file.name} converti avec succès !")
            st.download_button(
                label="⬇️ Télécharger le CSV converti",
                data=output,
                file_name=file.name.replace(".xlsx", "_converted.csv"),
                mime="text/csv"
            )

            # Aperçu
            st.dataframe(final_df.head())

        except Exception as e:
            st.error(f"⚠️ Erreur lors de la conversion de {file.name} : {e}")
