import streamlit as st
import speech_recognition as sr
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from itertools import zip_longest
from gtts import gTTS
import os

openapi_key = st.secrets["OPENAI_API_KEY"]


# Initialize Streamlit page configuration
st.set_page_config(page_title="Voice-Enabled AI-ChatBot")
st.title("AI Can Hear And Speak")

# Initialize session state variables
if 'entered_prompt' not in st.session_state:
    st.session_state['entered_prompt'] = ""

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# Initialize the ChatOpenAI model (replace with your actual AI model)
chat = ChatOpenAI(
    temperature=0.5,
    model_name="gpt-3.5-turbo",
    openai_api_key=openapi_key,  # Replace with your OpenAI API key
    max_tokens=100
)

def build_message_list():
    """
    Build a list of messages including system, human and AI messages.
    """
    # Start zipped_messages with the SystemMessage
    zipped_messages = [SystemMessage(
        content="""your name is AI Who Can Hear And Talk.. You are Expert for Students, here to guide and assist students with their questions and concerns. Please provide accurate and helpful information, and always maintain a polite and professional tone.

        1. Greet the user politely ask user name and ask how you can assist them with world related queries.
        2. Provide informative and relevant responses to questions about world and other related topics.
        3. Avoid discussing sensitive, offensive, or harmful content. Refrain from engaging in any form of discrimination, harassment, or inappropriate behavior.
        4. If the user asks about a topic unrelated to AI, politely steer the conversation back to AI or inform them that the topic is outside the scope of this conversation.
        5. Be patient and considerate when responding to user queries, and provide clear explanations.
        6. If the user expresses gratitude or indicates the end of the conversation, respond with a polite farewell.
        7. Do Not generate long paragraphs in response. Maximum words should be 100.

        Remember, your primary goal is to assist and educate students in the field of Artificial Intelligence. Always prioritize their learning experience and well-being."""
    )]

    # Zip together the past and generated messages
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(
                content=human_msg))  # Add user messages
        if ai_msg is not None:
            zipped_messages.append(
                AIMessage(content=ai_msg))  # Add AI messages

    return zipped_messages

def generate_speech(text):
    tts= gTTS(text)
    tts.save("ai_response.mp3")

def play_speech():
    os.system("Playing audio")


def generate_response(user_input):
    """
    Generate AI response using the ChatOpenAI model.
    """
    # Build the list of messages
    zipped_messages = build_message_list()

    # Append the latest user input to the list of messages
    zipped_messages.append(HumanMessage(content=user_input))

    # Generate response using the chat model
    ai_response = chat(zipped_messages)

    response = ai_response.content

    return response

recognizer = sr.Recognizer()

# Function to capture microphone input and convert to text
def capture_audio():
    with sr.Microphone() as source:
        st.write("Listening for audio input...")
        audio = recognizer.listen(source,timeout=5)

    try:
        st.write("Processing audio input...")
        text = recognizer.recognize_google(audio)  # You can use other engines as well
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Error: Could not request results; check your network connection."

# Function to submit user input
def submit(prompt):
    st.session_state.entered_prompt = prompt

# Create a button to capture audio
if st.button("Capture Audio"):
    audio_input = capture_audio()
    if audio_input:
        st.text("YOU (Voice): " + audio_input)
        response = generate_response(audio_input)
        st.session_state.generated.append(response)
        st.text("AI:"+ response)
        st.session_state.prompt_input = ""


        generate_response(response)
        play_speech()

# Create a text input for user
user_input = st.text_input("YOU (Text):", key='prompt_input')

if user_input != "":
    # Get user input
    st.session_state.entered_prompt = user_input

    # Append user input to past queries
    st.session_state.past.append(user_input)

    # Generate response
    ai_response = generate_response(user_input)

    # Append AI response to generated responses
    st.session_state.generated.append(ai_response)
    st.text("AI:"+ ai_response)

# Display the chat history
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        # Display AI response
        st.text(st.session_state["generated"][i], key=str(i))
        # Display user message
        st.text(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
