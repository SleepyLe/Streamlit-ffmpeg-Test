import pathlib
import subprocess
import ffmpeg
import streamlit as st
import whisper
import tempfile

# Load the Whisper model
model = whisper.load_model("base")

@st.experimental_memo
def convert_mp4_to_wav_ffmpeg_bytes2bytes(input_data: bytes) -> bytes:
   """
    It converts mp3 to wav using ffmpeg
    :param input_data: bytes object of a mp3 file
    :return: A bytes object of a wav file.
    """
    # print('convert_mp3_to_wav_ffmpeg_bytes2bytes')
    args = (ffmpeg
            .input('pipe:', format='mp3')
            .output('pipe:', format='wav')
            .global_args('-loglevel', 'error')
            .get_args()
            )
    # print(args)
    proc = subprocess.Popen(
        ['ffmpeg'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return proc.communicate(input=input_data)[0]

def on_file_change(uploaded_file):
    """
    Handles file upload changes by converting the uploaded MP4 file to WAV format.
    :param uploaded_file: Uploaded file object
    :return: WAV file as bytes
    """
    try:
        return convert_mp4_to_wav_ffmpeg_bytes2bytes(uploaded_file.getvalue())
    except Exception as e:
        st.error(f"Error converting file: {e}")
        return None

if __name__ == '__main__':
    st.title('MP4 to WAV Converter & Transcriber')
    st.markdown("""This app converts an MP4 file to WAV format, transcribes it using Whisper, and displays the transcription.""")

    uploaded_mp4_file = st.file_uploader('Upload Your MP4 File', type=['mp4'])

    if uploaded_mp4_file:
        filename = pathlib.Path(uploaded_mp4_file.name).stem
        try:
            converted_wav = on_file_change(uploaded_mp4_file)
            if converted_wav:
                # Lưu dữ liệu WAV vào một file tạm thời
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
                    tmpfile.write(converted_wav)
                    tmpfile_path = tmpfile.name
                
                # Sử dụng file tạm thời với Whisper để transcribe
                transcription = model.transcribe(tmpfile_path)
                
                st.sidebar.success("Transcription Complete")
                st.markdown(transcription["text"])
                
                # Xóa file tạm thời sau khi đã sử dụng
                pathlib.Path(tmpfile_path).unlink()
                
        except Exception as e:
            st.error(f"An error occurred during file processing: {e}")
