"""
App to convert text to speech using Google's Cloud TTS APIs.
Uses streamlit to create web app to easily interact with Google's API.

"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st
from google.cloud import texttospeech
from google.oauth2 import service_account
from langcodes import *
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR.joinpath("static")
MEDIA_DIR = BASE_DIR.joinpath("media")
CSS_DIR = STATIC_DIR.joinpath("css")
IMG_DIR = STATIC_DIR.joinpath("img")
ICO = Image.open(IMG_DIR.joinpath("language.png"))
LOGO = Image.open(IMG_DIR.joinpath("language.png"))


    
def local_css():
    # Updated CSS styling as a string
    custom_css = """
    <style>
    /* Apply background color to the main content area */
    .main {
        background-color: #333333  !important;
    }
    body, h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-weight: bold !important;
        font-size: 14px !important;
    }
    /* Hide the Streamlit menu (hamburger) and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
    # Inject the custom CSS into the Streamlit app
    st.markdown(custom_css, unsafe_allow_html=True)




@st.cache_data()
def load_credentials_file() -> str:
    # load the Google Cloud credentials JSON file from the folder 'static'
    try:
        with open(STATIC_DIR.joinpath("credentials.json"), "r") as f:
            #credential_file = f.read()
            credential_file = json.load(f)
        return credential_file
    except Exception as e:
        return None


def handle_change():
    """
    set and update session state variables
    """
    if st.session_state.input_type_choice:
        st.session_state.input_type = st.session_state.input_type_choice
    if st.session_state.input_text:
        st.session_state.text = st.session_state.input_text
    if st.session_state.file_type_choice:
        st.session_state.file_type = st.session_state.file_type_choice
    if st.session_state.voice_lang_choice:
        st.session_state.voice_lang = st.session_state.voice_lang_choice
    if st.session_state.voice_type_choice:
        st.session_state.voice_type = st.session_state.voice_type_choice
    if st.session_state.voice_name_choice:
        st.session_state.voice_name = st.session_state.voice_name_choice
    if st.session_state.audio_profile_choice:
        st.session_state.audio_profile = st.session_state.audio_profile_choice
    if st.session_state.voice_speed_choice:
        st.session_state.voice_speed = st.session_state.voice_speed_choice
    if st.session_state.voice_pitch_choice:
        st.session_state.voice_pitch = st.session_state.voice_pitch_choice


@st.cache_data()
def get_available_voices(credentials_file: str) -> pd.DataFrame:
    """
    get a list of available voices and return a dataframe containing the data
    """
    try: 
        credentials = service_account.Credentials.from_service_account_info(credentials_file)
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        # Performs the list voices request
        voices = client.list_voices()
        voices_list = [
            {
            "name": voice.name, 
            "language_code": voice.language_codes[0], 
            "ssml_gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name, 
            "language": Language.get(voice.language_codes[0]).display_name(voice.language_codes[0]).title()
            } for voice in voices.voices]

        df = pd.DataFrame(voices_list)
        return df
    except Exception as e:
        return pd.DataFrame()


@st.cache_data()
def convert(in_text: str, in_file_type: str, out_file: str, credentials_file: str, lang_code: str = "en-US", 
            lang_name: str = "en-US-Wavenet-C", ssml_gender: str = "FEMALE", speaking_rate: float = 1.0, 
            pitch: float = 0.0, effects_profile_id: str = "") -> bool:


    try:
        # set the path to the credentials JSON file and construct credentials object
        credentials = service_account.Credentials.from_service_account_info(credentials_file)
        # Instantiate a client using the credentials object
        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # set input to text or ssml, depending on the input file
        if in_file_type == "ssml":
            synthesis_input = texttospeech.SynthesisInput(ssml=in_text)
        else:
            synthesis_input = texttospeech.SynthesisInput(text=in_text)
        
        # set ssmlVoiceGender as per request to either female or male
        gender = texttospeech.SsmlVoiceGender.FEMALE if "FEMALE" in ssml_gender else texttospeech.SsmlVoiceGender.MALE
        # Set the voice parameters: select the language, language code ("en-US") and the ssml gender
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code, name=lang_name, ssml_gender=gender
        )

        # Select the audio file type to be returned
        audio_settings = {
            "audio_encoding": None,
            "speaking_rate": speaking_rate,
            "sample_rate_hertz":8000,
            "pitch": pitch
        }
        if "mp3" in out_file[-3:]:
            audio_settings["audio_encoding"] = texttospeech.AudioEncoding.MP3
            if effects_profile_id:
                audio_settings["effects_profile_id"] = [effects_profile_id]
        elif "wav" in out_file[-3:]:
            audio_settings["audio_encoding"] = texttospeech.AudioEncoding.LINEAR16
            if effects_profile_id:
                audio_settings["effects_profile_id"] = [effects_profile_id]
        else:
            return False

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=texttospeech.AudioConfig(**audio_settings)
        )

        # Write the response audio to an audio file
        # The response's audio_content is binary.
        with open(out_file, "wb") as out:
            out.write(response.audio_content)
            
        return True
    except Exception as e:
        return False


def app():
    # set the page title and style on page load
    st.set_page_config(page_title="Google TTS", page_icon=ICO, layout="wide")
    # load and apply local CSS for additional styling
    local_css()
    
    # ---- PAGE LAYOUT ----
    # add page title, description, and placeholder for any info or alarm banners
    logo = st.image(LOGO, width=100)
    page_title = st.empty()
    page_description = st.empty()
    alert_box = st.empty()
    # add download and playback section above divider
    left_top_col, right_top_col = st.columns([1,8])
    divider1 = st.markdown("---")    
    # add 'input section' with text input box
    text_type_radio = st.empty()
    text_input = st.empty()
    # add parameter section and divite it into three columns of equal width
    # each column will contain several configuration options/dropdowns/radio buttons
    left_btm_col, mid_btm_col, right_btm_col = st.columns(3) 
    # add send/convert button and set it slightly apart from the configuration section
    spacer2 = st.write("#####")
    send_button = st.empty()
    divider2 = st.markdown("---")
    # ---- END OF PAGE LAYOUT ----

    # add information to the page
    page_title.header("Text To Speech Converter")
    page_description.write("""
    This application enables you to convert plain text or SSML (Speech Synthesis Markup Language) into WAV or MP3 audio files using Google's Cloud Text-to-Speech API. Simply input your text, select from a variety of customization options, and generate your audio file.
    """
    )

    # load credential file required to access the Google Cloud Service or display an error
    credentials_file = load_credentials_file()
    if not credentials_file:
        alert_box.error(f"""Unable to find the JSON credential file!\n
        Please ensure it is located at :::  {STATIC_DIR.joinpath('credentials.json')}""")
        st.stop()
    
    # get an updated list of available voices or display an error
    voices = get_available_voices(credentials_file)
    if voices.size == 0:
        alert_box.error("Unable to fetch the list of available voices from the Google API. Do not continue.")
        st.stop()
    
    # get the language names for the Language/Locale dropdown
    language_names = voices["language"].sort_values().unique()
    
    # get audio device profiles from json file
    with open(STATIC_DIR.joinpath("audio_profile_id.json")) as f:
        profile_names = pd.read_json(f)

    # ---- INPUT SECTION ----
    # create the text input section
    input_type = text_type_radio.radio(label="input_type", options=["text", "ssml"], index=0, key="input_type_choice", label_visibility="hidden", horizontal=True)
    text = text_input.text_area("Text to speak:", placeholder=f"Please Enter {input_type} here", key="input_text")

    # ---- PARAMETER SECTION ----
    with left_btm_col:
        # Language/locale dropdown
        selected_lang = st.selectbox("Language/locale", on_change=handle_change, options=language_names, index=9 ,key="voice_lang_choice")
        
        # audio profile dropdown
        selected_profile = st.selectbox("Audio Device Profile", on_change=handle_change, options=profile_names["name"] ,key="audio_profile_choice")

        # output file format radio button
        out_file_type_choice = st.radio("Choose the output file type", on_change=handle_change, options=["WAV", "MP3"], key="file_type_choice", horizontal=True)
        out_file_name = f"audio.{out_file_type_choice.lower()}"
        out_file = str(MEDIA_DIR.joinpath(out_file_name))
    
    with mid_btm_col:
        # Voice Type dropdown - Wavenet voices are of higher quality than Standard/Basic ones
        selected_voice_type = st.selectbox("Voice type", on_change=handle_change, options=["Standard", "Wavenet"], index=1 ,key="voice_type_choice")
        
        # voice speed slider - determines playback speed in resulting audio file
        selected_speed = st.slider("Speed:", min_value=0.25, max_value=4.00, value=1.00, key="voice_speed_choice")
    
    with right_btm_col:
        # create a copy of the voices dataframe to work with and apply filters to
        voicedf = voices.copy()
        # concatenate the voice name and SSMl gender into one new column "friendly_name"
        # this is only used to display a friendlier name in the voice name dropdown
        voicedf["friendly_name"] = voicedf["name"].astype(str) + " (" + voicedf["ssml_gender"].str.lower() + ")"
        # apply filter based on chosen language and voice type (both are part of 'name' in the original dataframe)
        voicedf = voicedf[(voicedf["language"] == selected_lang) & voicedf["friendly_name"].str.contains(selected_voice_type)]
        
        # Voice Name dropdown - will update based on language/locale and voice type choices
        selected_voice = st.selectbox("Voice", on_change=handle_change, options=voicedf["friendly_name"], key="voice_name_choice")

        # voice pitch slider - determines pitch in resulting audio file
        selected_pitch = st.slider("Pitch:", min_value=-20.00, max_value=20.00, value=0.0, step=0.1, key="voice_pitch_choice")
    
    # only continue with the remaining script, if some plain text or SSML text has been provided
    if text:
        # get the dataframe entry for the selected voice
        voice = voicedf[voicedf["friendly_name"]==selected_voice]
        # get the dataframe entry for the selected audio device profile
        profile = profile_names[profile_names["name"]==selected_profile]
        # convert text to speech using all the collected arguments
        if send_button.button("Convert"):
            result = convert(
                in_text=text,
                in_file_type=input_type, 
                out_file=out_file, 
                credentials_file=credentials_file, 
                lang_code=voice["language_code"].values[0], 
                lang_name=voice["name"].values[0], 
                ssml_gender=voice["ssml_gender"].values[0],
                speaking_rate=selected_speed,
                pitch=selected_pitch,
                effects_profile_id=profile["id"].values[0]
            )
            
            # only continue if the 'convert' function returned True
            if result:
                alert_box.success("Your audio file has been created successfully! You can now play or download it.")
                # open/read the newly created audio.wav or audio.mp3 file
                with open(out_file, "rb") as file:
                    audio_bytes = file.read()
                    audio_format = "audio/wav" if "WAV" in out_file_type_choice else "audio/mpeg"
                    # display an audio player to play back newly created audio file
                    right_top_col.audio(audio_bytes, format=audio_format)
                
                    # create a download button to download newly created audio file
                    left_top_col.download_button(
                            label="Download",
                            data=file,
                            file_name=out_file_name
                        )
            elif not result:
                alert_box.error("Something went wrong! The text could not be converted using the Google API.")
                st.stop()


if __name__ == "__main__":
    app()
