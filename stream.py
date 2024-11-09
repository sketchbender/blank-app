# youtube_summarizer.py

import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

# Configure API key for Gemini directly
GEMINI_API_KEY = "AIzaSyCt7gqXIdsE1o_Jc9oupC5XKqnqo5SKdZ8"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
def initialize_model(model_name="gemini-pro"):
    model = genai.GenerativeModel(model_name)
    return model

# Function to generate a response using the Gemini model
def get_response(model, prompt):
    response = model.generate_content(prompt)
    return response.text

# Function to retrieve YouTube video transcripts
def get_video_transcripts(video_id):
    try:
        transcription_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcription = " ".join([transcript["text"] for transcript in transcription_list])
        return transcription
    except Exception as e:
        st.error(f"Error retrieving transcription: {e}")
        return ""

# Function to extract the video ID from a YouTube URL
def get_video_id(url):
    video_id = url.split("=")[1]
    if "&" in video_id:
        video_id = video_id.split("&")[0]
    return video_id

# Streamlit app interface for summarizing video content
st.title("YouTube Video Summarizer")
st.markdown("<br>", unsafe_allow_html=True)
youtube_url = st.text_input("Enter YouTube video link:")

if youtube_url:
    video_id = get_video_id(youtube_url)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

submit = st.button("Submit")

# Define the behavior for the model prompt for summarization
model_behavior = """You are an expert in summarizing YouTube videos from their transcriptions.
                    The input is the transcription of a video, and the output should be a summary 
                    including all key information. Break down the information into multiple paragraphs 
                    if it improves clarity and conciseness. Provide a relevant title for the summary, 
                    aiming to keep it under 1000 words. Do not add irrelevant information or extra content.
                    If the transcription is empty or meaningless, return `Couldn't generate summary for the given video`.
                    This is the transcription for the video:
                """

if submit:
    transcriptions = get_video_transcripts(video_id)

    if transcriptions:
        # Initialize the Gemini model
        gemini_model = initialize_model(model_name="gemini-pro")
        final_prompt = model_behavior + "\n\n" + transcriptions
        summary = get_response(model=gemini_model, prompt=final_prompt)
        st.write(summary)
    else:
        st.write("Couldn't generate summary for the given video.")

# Streamlit app interface for question answering
st.title("Question Answering in YouTube Video")
st.markdown("<br>", unsafe_allow_html=True)
youtube_url = st.text_input("Enter YouTube video link for Q&A:")

if youtube_url:
    video_id = get_video_id(youtube_url)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

user_prompt = st.text_area("Your question about the video", key="user_prompt")
submit_qa = st.button("Submit Q&A")

# Define the behavior for the model prompt for Q&A
qa_model_behavior = """You are an expert in answering questions about YouTube videos from their transcription.
                        The input is the transcription of the video along with the user’s question. 
                        Ensure that you fully understand the information in the transcription and answer the user's question.
                        Please avoid adding irrelevant information. If the transcription is empty, return `Couldn't transcribe the video`.
                        Otherwise, respond accordingly:
                    """

if user_prompt and submit_qa:
    # Transcribe the video
    video_transcriptions = get_video_transcripts(video_id)
    
    if video_transcriptions:
        # Initialize the Gemini model
        gemini_model = initialize_model(model_name="gemini-pro")
        # Add transcription and user question to prompt
        qa_final_prompt = qa_model_behavior + f"\nVideo transcription: {video_transcriptions}\nUser question: {user_prompt}"
        
        # Generate response
        response = get_response(model=gemini_model, prompt=qa_final_prompt)
        st.write(response)
    else:
        st.write("Couldn't generate an answer for the given video.")
