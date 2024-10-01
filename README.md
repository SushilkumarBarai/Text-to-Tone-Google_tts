# Text-to-Speech-streamlit

This Streamlit app allows you to convert text to audio files using the Google Cloud Text-to-Speech API. It features a user interface for quick testing, enabling users to input text easily and receive audio files in just a few clicks.

## Features
Access to most of the Google TTS API features, including
- voice and language selection (including WaveNet voices)
- text and ssml support
- voice tuning (pitch, speaking rate,sample rate)
- two output audio formats (LINEAR16 [.wav], MP3 [.mp3])
- audio profiles

You can play the audio from the converted text directly in the browser or download the audio file to your local machine.

## Requirements
Before you can begin, you must have a Google Cloud account and enable the Text-to-Speech API in the Google Cloud Platform Console.
Follow the steps on the official website:
https://cloud.google.com/text-to-speech/docs/before-you-begin

In a nutshell:
- Enable Text-to-Speech on a project.
  - Make sure billing is enabled for Text-to-Speech.
  - Make sure your project has at least one service account.
  - Download a service account credential key in the JSON format.
- Place the credentials key JSON file in this project's ***static*** folder and make sure to name the file ***credentials.json***

## Installation

Install the Python requirements using the requirements.txt file. This will install Streamlit, the Google Cloud TTS Python package, and other dependencies.

```bash
pip install -r requirements.txt
```
Place the **`credentials.json`** file into the **`static`** folder. Please refer to the **Requirements** section above.


## Run the Streamlit app

```bash
streamlit run app.py
```
This command will start the streamlit app, will automatically open a browser window, and navigate to http://localhost:8501/

## How-to use the app

1. **Input Method Selection:**
   - Choose between **Plain Text** and **SSML** as the input method using the radio buttons.

2. **Text Input:**
   - Enter your plain text or SSML markup into the text box.

3. **Voice Selection:**
   - **Choose Language:**
     - Select a language from the first dropdown menu. The **Voice Type** and **Voice** dropdown menus will update automatically with the available selections.
   - **Select Voice Type:**
     - Choose either **Standard** or **WaveNet** (if available in the selected language) from the **Voice Type** dropdown.
   - **Select Voice:**
     - Choose from the list of available voices in the **Voice** dropdown.

4. **Output File Type:**
   - Choose between **WAV** (lossless) and **MP3** (lossy) as the output file type.

**Optional Customizations:**
- Select one of the available profiles in the **Audio Device Profile** dropdown to optimize the audio experience for specific use cases.
- Adjust the **Speed** and **Pitch** to further customize the voice.

5. **Convert Text to Speech:**
   - Once you’ve entered your text, the **Convert** button will appear. Press the button to start the text-to-speech conversion.

6. **Download and Playback:**
   - After the conversion is finished, a **Download** button and a media player will appear on the screen.
   - **Playback:** Play the message directly in your browser using the media player.
   - **Download:** Download the audio file to your local machine using the **Download** button.


