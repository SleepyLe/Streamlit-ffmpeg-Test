import pathlib
import subprocess
import tempfile

import ffmpeg
import streamlit as st
import whisper

model = whisper.load_model("base")

@st.experimental_memo
def convert_mp4_to_wav_ffmpeg_bytes2bytes(input_data: bytes) -> bytes:
    """
    It converts mp4 to wav using ffmpeg
    :param input_data: bytes object of a mp4 file
    :return: A bytes object of a wav file.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        args = (
            ffmpeg
            .input('pipe:', format='mp4')
            .output(temp_wav.name, format='wav', codec='pcm_s16le', ac=1, ar=16000)
            .global_args('-loglevel', 'error')
            .get_args()
        )
        proc = subprocess.Popen(
            ['ffmpeg'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.communicate(input=input_data)
        with open(temp_wav.name, "rb") as wav_data:
            return wav_data.read()

@st.experimental_memo
def on_file_change(uploaded_mp4_file):
    return convert_mp4_to_wav_ffmpeg_bytes2bytes(uploaded_mp4_file.getvalue())

def on_change_callback():
    """
    It prints a message to the console. Just for testing of callbacks.
    """
    print(f'on_change_callback: {uploaded_mp4_file}')

# The below code is a simple streamlit web app that allows you to upload an mp4 file
# and then download the converted wav file.
if __name__ == '__main__':
    st.title('mp4 to WAV Converter test app')
    st.markdown("""This is a quick example app for using **ffmpeg** on Streamlit Cloud.
    It uses the `ffmpeg` binary and the python wrapper `ffmpeg-python` library.""")

    uploaded_mp4_file = st.file_uploader('Upload Your mp4 File', type=['mp4'], on_change=on_change_callback)

    if uploaded_mp4_file:
        uploaded_mp4_file_length = len(uploaded_mp4_file.getvalue())
        filename = pathlib.Path(uploaded_mp4_file.name).stem
        if uploaded_mp4_file_length > 0:
            st.text(f'Size of uploaded "{uploaded_mp4_file.name}" file: {uploaded_mp4_file_length} bytes')
            wav_data = on_file_change(uploaded_mp4_file)

    st.markdown("""---""")
    if wav_data:
        transcription = model.transcribe(wav_data)
        st.sidebar.success("Transcription Complete")
        st.markdown(transcription["text"])

    st.markdown("""---""")
