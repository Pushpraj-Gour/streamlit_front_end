import streamlit as st
import pyttsx3
import threading
import time

def speak_question(question: str, 
                  voice_rate: int = 150, 
                  voice_volume: float = 0.9,
                  display_duration: int = 5,
                  show_repeat_button: bool = True) -> None:
    """
    Display a question in Streamlit and automatically speak it using text-to-speech.
    
    Usage:
        speak_question("What is your name?")
        speak_question("How are you?", voice_rate=120, voice_volume=0.8)
    
    Args:
        question (str): The question text to display and speak
        voice_rate (int): Speech rate (words per minute, default: 150)
        voice_volume (float): Voice volume (0.0 to 1.0, default: 0.9)
        display_duration (int): How long to display the question in seconds (default: 5)
        show_repeat_button (bool): Whether to show the repeat button (default: True)
    """
    
    def _speak_text(text: str):
        """Internal function to handle text-to-speech in a separate thread"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', voice_rate)
            engine.setProperty('volume', voice_volume)
            
            # Optional: Set voice (uncomment and modify as needed)
            # voices = engine.getProperty('voices')
            # if voices:
            #     engine.setProperty('voice', voices[0].id)  # Use first available voice
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            st.error(f"Error with text-to-speech: {str(e)}")
    
    # Display the question prominently
    # st.markdown(f"""
    # <div style="
    #     background-color: #f0f2f6;
    #     border-left: 5px solid #4CAF50;
    #     padding: 20px;
    #     margin: 10px 0;
    #     border-radius: 5px;
    #     font-size: 18px;
    #     font-weight: bold;
    #     color: #333;
    # ">
    #     🎤 {question}
    # </div>
    # """, unsafe_allow_html=True)
    
    # Start speaking in a separate thread to avoid blocking the UI
    speak_thread = threading.Thread(target=_speak_text, args=(question,))
    speak_thread.daemon = True
    speak_thread.start()
    
    # Optional: Show a speaking indicator
    with st.spinner('🔊 Speaking...'):
        time.sleep(display_duration)
    
    # Show repeat button if enabled
    if show_repeat_button:
        if st.button("🔄 Repeat Question", key=f"repeat_{hash(question)}"):
            # Start speaking again in a separate thread
            repeat_thread = threading.Thread(target=_speak_text, args=(question,))
            repeat_thread.daemon = True
            repeat_thread.start()
            
            # Show speaking indicator again
            with st.spinner('🔊 Speaking...'):
                time.sleep(display_duration)