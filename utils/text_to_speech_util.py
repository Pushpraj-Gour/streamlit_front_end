import streamlit as st
import streamlit.components.v1 as components
import time
import uuid

def speak_question(question: str, 
                  voice_rate: float = 1.0, 
                  voice_volume: float = 0.9,
                  display_duration: int = 3,
                  show_repeat_button: bool = True,
                  auto_speak: bool = True) -> None:
    """
    Display a question in Streamlit and speak it using browser-based text-to-speech.
    Works in Streamlit Cloud and other web deployments.
    
    Usage:
        speak_question("What is your name?")
        speak_question("How are you?", voice_rate=0.8, voice_volume=0.9)
    
    Args:
        question (str): The question text to display and speak
        voice_rate (float): Speech rate (0.1 to 10, default: 1.0)
        voice_volume (float): Voice volume (0.0 to 1.0, default: 0.9)
        display_duration (int): How long to show speaking indicator (default: 3)
        show_repeat_button (bool): Whether to show the repeat button (default: True)
        auto_speak (bool): Whether to automatically speak on load (default: True)
    """
    
    # Sanitize the question text for JavaScript
    clean_question = question.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
    
    # Generate unique ID for this instance
    component_id = f"tts_{uuid.uuid4().hex[:8]}"
    
    # Create the HTML/JavaScript component for browser TTS
    tts_html = f"""
    <div id="{component_id}" style="margin: 10px 0;">
        <script>
        (function() {{
            let isCurrentlySpeaking = false;
            
            function speakText(text, rate, volume) {{
                // Stop any current speech
                if (window.speechSynthesis.speaking) {{
                    window.speechSynthesis.cancel();
                }}
                
                // Check if speech synthesis is supported
                if (!('speechSynthesis' in window)) {{
                    console.warn('Speech Synthesis not supported in this browser');
                    return;
                }}
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = rate;
                utterance.volume = volume;
                utterance.lang = 'en-US';
                
                // Try to use a more natural voice if available
                const voices = window.speechSynthesis.getVoices();
                if (voices.length > 0) {{
                    // Prefer English voices
                    const englishVoice = voices.find(voice => 
                        voice.lang.startsWith('en') && 
                        (voice.name.includes('Google') || voice.name.includes('Microsoft'))
                    );
                    if (englishVoice) {{
                        utterance.voice = englishVoice;
                    }}
                }}
                
                utterance.onstart = function() {{
                    isCurrentlySpeaking = true;
                    console.log('Speech started');
                }};
                
                utterance.onend = function() {{
                    isCurrentlySpeaking = false;
                    console.log('Speech ended');
                }};
                
                utterance.onerror = function(event) {{
                    isCurrentlySpeaking = false;
                    console.error('Speech error:', event.error);
                }};
                
                window.speechSynthesis.speak(utterance);
            }}
            
            // Auto-speak when component loads
            {"speakText('" + clean_question + "', " + str(voice_rate) + ", " + str(voice_volume) + ");" if auto_speak else ""}
            
            // Make speak function globally available for repeat button
            window.speakQuestion_{component_id} = function() {{
                speakText('{clean_question}', {voice_rate}, {voice_volume});
            }};
        }})();
        </script>
    </div>
    """
    
    # Render the TTS component
    components.html(tts_html, height=0)
    
    # Show speaking indicator
    if auto_speak:
        with st.spinner('🔊 Speaking...'):
            time.sleep(display_duration)
    
    # Show repeat button if enabled
    if show_repeat_button:
        if st.button("🔄 Repeat Question", key=f"repeat_{component_id}"):
            # Create repeat TTS component
            repeat_html = f"""
            <script>
            if (typeof window.speakQuestion_{component_id} === 'function') {{
                window.speakQuestion_{component_id}();
            }} else {{
                // Fallback if function not available
                const utterance = new SpeechSynthesisUtterance('{clean_question}');
                utterance.rate = {voice_rate};
                utterance.volume = {voice_volume};
                utterance.lang = 'en-US';
                window.speechSynthesis.speak(utterance);
            }}
            </script>
            """
            components.html(repeat_html, height=0)
            
            # Show speaking indicator again
            with st.spinner('🔊 Speaking...'):
                time.sleep(display_duration)
