import streamlit as st
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from utils import process_image, generate_solution, text_to_speech

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.frame = None

    def transform(self, frame):
        self.frame = frame.to_ndarray(format="bgr24")
        return self.frame

def main():
    st.title("Your Smart Tutor Solution")
    st.write("Upload an image with a math problem or use the webcam to capture an image.")

    # file upload option
    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        math = process_image(image)
        st.session_state['math'] = math
        st.write("Problem:")
        st.write(math)
    else:
        # if no file is uploaded, display the webcam option
        st.write("Or capture an image using your webcam:")

        webrtc_ctx = webrtc_streamer(
            key="example",
            video_transformer_factory=VideoTransformer,
            media_stream_constraints={"video": True},
        )

        # check if the video transformer is initialized and has a frame
        if webrtc_ctx.video_transformer is not None:
            frame = webrtc_ctx.video_transformer.frame
            if frame is not None:
                image = Image.fromarray(frame)
                st.image(image, caption="Captured Image", use_column_width=True)
                math = process_image(image)
                st.session_state['math'] = math
                st.write("Problem:")
                st.write(math)
            else:
                st.write("Webcam capture not yet available.")
        else:
            st.write("Webcam stream not initialized.")

    # buttons to trigger LLM and TTS
    if st.button("Tutor Me"):
        if 'math' in st.session_state:
            math = st.session_state['math']
            solution = generate_solution(math, tokenizer, model)
            st.session_state['solution'] = solution
            st.session_state['audio_data'] = text_to_speech(solution, tokenizer_au, model_au)  # Save audio data in session state

    # display solution and audio
    if 'solution' in st.session_state:
        st.write("Step by Step Solution:")
        st.markdown(st.session_state['solution'])
        
        if 'audio_data' in st.session_state:
            st.write("Audio:")
            st.audio(st.session_state['audio_data'], format="audio/wav")

if __name__ == "__main__":
    main()
