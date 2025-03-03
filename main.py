import streamlit as st
import speech_recognition as sr
from datetime import datetime
import os

# Initialisation des états de session
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'pause' not in st.session_state:
    st.session_state.pause = False


def transcribe_speech(api, language, **kwargs):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            st.info("Parlez maintenant...")
            audio_text = r.listen(source, timeout=5)
            st.info("Transcription en cours...")

            if api == "Google":
                text = r.recognize_google(audio_text, language=language)
            elif api == "Sphinx":
                text = r.recognize_sphinx(audio_text)
            elif api == "Wit.ai":
                text = r.recognize_wit(audio_text, key=kwargs.get('wit_key'))
            elif api == "IBM":
                text = r.recognize_ibm(
                    audio_text,
                    username=kwargs.get('ibm_username'),
                    password=kwargs.get('ibm_password'),
                    language=language
                )
            return text
        except sr.WaitTimeoutError:
            return "Délai d'attente dépassé - Aucun son détecté"
        except sr.UnknownValueError:
            return "La parole n'a pas pu être reconnue"
        except sr.RequestError as e:
            return f"Erreur de l'API : {str(e)}"
        except Exception as e:
            return f"Erreur inattendue : {str(e)}"


def save_transcript(text, filename):
    with open(filename, 'w') as f:
        f.write(text)
    return os.path.abspath(filename)


def main():
    st.title("🎙️ Application de Reconnaissance Vocale Améliorée")
    st.markdown("### Configuration des paramètres")

    # Sélection de l'API
    api_options = ["Google", "Sphinx", "Wit.ai", "IBM"]
    selected_api = st.selectbox("Choisissez une API de reconnaissance vocale", api_options)

    # Gestion des identifiants API
    api_key = None
    if selected_api == "Wit.ai":
        api_key = st.text_input("Clé API Wit.ai", type="password")
    elif selected_api == "IBM":
        col1, col2 = st.columns(2)
        with col1:
            ibm_user = st.text_input("Nom d'utilisateur IBM")
        with col2:
            ibm_pass = st.text_input("Mot de passe IBM", type="password")

    # Sélection de la langue
    languages = {
        'Français': 'fr-FR',
        'Anglais (US)': 'en-US',
        'Espagnol': 'es-ES',
        'Allemand': 'de-DE',
        'Italien': 'it-IT'
    }
    selected_lang = st.selectbox("Choisissez la langue parlée", list(languages.keys()))

    # Gestion de l'enregistrement
    st.markdown("### Contrôle d'enregistrement")
    col_rec, col_pause = st.columns(2)
    with col_rec:
        if st.button("▶️ Démarrer" if not st.session_state.is_recording else "⏹️ Arrêter"):
            st.session_state.is_recording = not st.session_state.is_recording
    with col_pause:
        if st.button("⏸️ Pause" if not st.session_state.pause else "⏯️ Reprendre"):
            st.session_state.pause = not st.session_state.pause

    # Transcription
    if st.session_state.is_recording and not st.session_state.pause:
        kwargs = {}
        if selected_api == "Wit.ai":
            kwargs['wit_key'] = api_key
        elif selected_api == "IBM":
            kwargs['ibm_username'] = ibm_user
            kwargs['ibm_password'] = ibm_pass

        result = transcribe_speech(selected_api, languages[selected_lang], **kwargs)

        if result and not result.startswith("Erreur"):
            st.session_state.transcript += result + " "
            st.rerun()

    # Affichage de la transcription
    st.markdown("### Transcription")
    transcript_area = st.text_area("", value=st.session_state.transcript, height=200)

    # Gestion de l'enregistrement
    # Téléchargement du fichier
    st.markdown("### Télécharger la transcription")
    filename = st.text_input("Nom du fichier",
                             f"transcript_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                             help="Entrez le nom du fichier avec l'extension .txt")

    download_button = st.download_button(
        label="⬇️ Télécharger",
        data=st.session_state.transcript,
        file_name=filename,
        mime="text/plain",
        disabled=not st.session_state.transcript
    )

    if download_button:
        st.success("Téléchargement démarré ! Vérifiez vos téléchargements")

    # Aide et informations
    with st.expander("ℹ️ Instructions d'utilisation"):
        st.markdown("""
        1. Sélectionnez une API de reconnaissance vocale
        2. Entrez les identifiants nécessaires si requis
        3. Choisissez la langue parlée
        4. Utilisez les boutons de contrôle pour gérer l'enregistrement
        5. Corrigez la transcription si nécessaire
        6. Sauvegardez le résultat final
        """)


if __name__ == "__main__":
    main()