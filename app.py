import gradio as gr
# from chatbot import model_inference, EXAMPLES, chatbot
# from voice_chat import respond
# from MyChatInterface import MyChatInterface
from groq import Groq
GROP_API_KEY = "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"
# Define Gradio theme
theme = gr.themes.Soft(
    primary_hue="sky",
    secondary_hue="violet",
    neutral_hue="gray",
    font=[gr.themes.GoogleFont('orbitron')]
)


# Create Gradio blocks for different functionalities

# Chat interface block
# with gr.Blocks(
#         css=""".gradio-container .avatar-container {height: 40px width: 40px !important;} #duplicate-button {margin: auto; color: white; background: #f1a139; border-radius: 100vh; margin-top: 2px; margin-bottom: 2px;}""",
# ) as chat:
#     gr.Markdown("### Image Chat, Image Generation, Image classification and Normal Chat")
#     # gr.ChatInterface(
#     #     fn=model_inference,
#     #     chatbot = chatbot,
#     #     examples=EXAMPLES,
#     #     multimodal=True,
#     #     cache_examples=False,
#     #     autofocus=False,
#     #     concurrency_limit=10,
#     # )
#     MyChatInterface(
#         fn=model_inference,
#         chatbot = chatbot,
#         examples=EXAMPLES,
#         multimodal=True,
#         cache_examples=False,
#         autofocus=False,
#         concurrency_limit=10,
#     )

# Voice chat block
# with gr.Blocks() as voice:
#     gr.Markdown("# Try Voice Chatfrom Below Link:")
#     gr.HTML("<a href='https://huggingface.co/spaces/KingNish/Voicee'>https://huggingface.co/spaces/KingNish/Voicee</a>")
def transcribe_and_stream(inputs, model_name="groq_whisper", show_info="show_info", language="english"):
    def groq_whisper_tts(filename):
        ###TODO提升识别速度
        groq_client = Groq(api_key=GROP_API_KEY)
        with open(filename, "rb") as file:
            transcriptions = groq_client.audio.transcriptions.create(
            file=(filename, file.read()), 
            model="whisper-large-v3-turbo",
            response_format="json", 
            temperature=0.0 
            )
        print("transcribed text:", transcriptions.text)
        print("********************************")
        return transcriptions.text
    
    if inputs is not None and inputs!="":
        if show_info=="show_info":
            gr.Info("Processing Audio")
        text = groq_whisper_tts(inputs)
        
        # stream text output
        # for i in range(len(text)):
        #     time.sleep(0.01)
        #     yield text[: i + 10]
        return text
    else:
        return ""

def aya_speech_text_response(text):
    ###TODO 改这里的prompt和addiional instruction
    if text is not None and text!="":
        groq_client = Groq(api_key=GROP_API_KEY)
        stream = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[    ####改为self.messages  TODO
                {
                    "role": "system",
                    "content": "You are an expert writer. Generate a long, comprehensive, structured chapter for the section provided. If additional instructions are provided, consider them very important. Only output the content.",
                },
                {
                    "role": "user",
                    "content": f"Generate a long, comprehensive, structured chapter. Use the following section and important instructions:\n\n<section_title>{prompt}</section_title>\n\n<additional_instructions>{additional_instructions}</additional_instructions>",
                },
            ],
            temperature=0.3,
            max_tokens=8000,
            top_p=1,
            stream=True,
            stop=None,
        )

        ###debug TODO
        for temp_token in stream:
            yield temp_token
        #output = ""
        
        # for event in stream:
        #     if event:
        #         if event.event_type == "text-generation":
        #             output+=event.text
        #             cleaned_output = clean_text(output)
        #             yield cleaned_output
    else:
        return ""
   
###TODO debug
def convert_text_to_speech(text, language="english"):
    # Text-to-speech function
    import edge_tts 
    import tempfile

    async def text_to_speech(text, voice, rate, pitch):
        if not text.strip():
            return None, gr.Warning("Please enter text to convert.")
        if not voice:
            return None, gr.Warning("Please select a voice.")
        
        voice_short_name = voice.split(" - ")[0]
        rate_str = f"{rate:+d}%"
        pitch_str = f"{pitch:+d}Hz"
        communicate = edge_tts.Communicate(text, voice_short_name, rate=rate_str, pitch=pitch_str)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_path = tmp_file.name
            await communicate.save(tmp_path)
        return tmp_path, None
    
    # do language detection to determine voice of speech response
    if text is not None and text!="":
        # clean text before doing language detection
        # cleaned_text = clean_text(text, remove_bullets=True, remove_newline=True)

        audio_path = text_to_speech(text)
            
        return audio_path
    else:
        return None

with gr.Blocks() as voice:
    with gr.Row():
        with gr.Column():
            e2e_audio_file = gr.Audio(sources="microphone", type="filepath", min_length=None)
            e2_audio_submit_button = gr.Button(value="Get Aya's Response", variant="primary")
            
            clear_button_microphone = gr.ClearButton()
                                
        with gr.Column():
            e2e_audio_file_trans = gr.Textbox(lines=3,label="Your Input", autoscroll=False, show_copy_button=True, interactive=False)
            e2e_audio_file_aya_response = gr.Textbox(lines=3,label="Aya's Response", show_copy_button=True, container=True, interactive=False)
            e2e_aya_audio_response = gr.Audio(type="filepath", label="Aya's Audio Response")

    e2_audio_submit_button.click(
        transcribe_and_stream,
        inputs=[e2e_audio_file],
        outputs=[e2e_audio_file_trans],
        show_progress="full",
    ).then(
        aya_speech_text_response,
        inputs=[e2e_audio_file_trans],
        outputs=[e2e_audio_file_aya_response],
        show_progress="full",
    ).then(
        convert_text_to_speech,
        inputs=[e2e_audio_file_aya_response],
        outputs=[e2e_aya_audio_response],
        show_progress="full",
    )

    clear_button_microphone.click(lambda: None, None, e2e_audio_file)
    clear_button_microphone.click(lambda: None, None, e2e_aya_audio_response)
    clear_button_microphone.click(lambda: None, None, e2e_audio_file_aya_response)
    clear_button_microphone.click(lambda: None, None, e2e_audio_file_trans)

# with gr.Blocks() as image:
#     gr.HTML("<iframe src='https://kingnish-image-gen-pro.hf.space' width='100%' height='2000px' style='border-radius: 8px;'></iframe>")

# with gr.Blocks() as instant2:
#     gr.HTML("<iframe src='https://kingnish-instant-video.hf.space' width='100%' height='3000px' style='border-radius: 8px;'></iframe>")

# with gr.Blocks() as video:
#     gr.Markdown("""More Models are coming""")
#     gr.TabbedInterface([ instant2], ['Instant🎥'])     

# Main application block
with gr.Blocks(theme=theme, title="OpenGPT 4o DEMO") as demo:
    gr.Markdown("# OpenGPT 4o")
    # gr.TabbedInterface([chat, voice, image, video], ['💬 SuperChat','🗣️ Voice Chat', '🖼️ Image Engine', '🎥 Video Engine'])
    
    gr.TabbedInterface([voice], ['💬 SuperChat','🗣️ Voice Chat', '🖼️ Image Engine', '🎥 Video Engine'])

demo.queue(max_size=300)
# demo.launch(share=True)
demo.launch()