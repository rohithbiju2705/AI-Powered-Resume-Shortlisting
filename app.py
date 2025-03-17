import streamlit as st
import pdfplumber
import docx
import os
import pandas as pd
import numpy as np
from groq import Groq  # Import Groq class for API interaction
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Initialize Groq API
groq_api_key = os.getenv("GROQ_API_KEY", "")  # Fetch the API key from environment variable

if not groq_api_key:
    st.error("Groq API key is missing. Please set the API key.")

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_skills_experience(text):
    prompt = f"""
    Extract the key skills and experience from the following resume:
    {text}
    Provide the output in structured format: Skills, Experience.
    """
    
    # Make a chat completion request to Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile"  # Use the appropriate model (you can replace this if needed)
    )
    
    # Extract the response from Groq's chat
    return chat_completion.choices[0].message.content

def match_with_job_description(resume_data, job_description):
    prompt = f"""
    Compare the following resume details:
    {resume_data}
    With the job description:
    {job_description}
    Provide a score from 0-100 based on relevance and suggest improvements.
    """
    
    # Make a chat completion request to Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile"  # Use the appropriate model (you can replace this if needed)
    )
    
    # Extract the response from Groq's chat
    return chat_completion.choices[0].message.content

def process_resumes(uploaded_files, job_description):
    results = []
    for file in uploaded_files:
        if file.name.endswith(".pdf"):
            text = extract_text_from_pdf(file)
        elif file.name.endswith(".docx"):
            text = extract_text_from_docx(file)
        else:
            continue
        
        skills_exp = extract_skills_experience(text)
        match_result = match_with_job_description(skills_exp, job_description)
        results.append((file.name, skills_exp, match_result))
    
    return results

def main():
    st.title("AI-Powered Resume Shortlisting System")
    st.sidebar.header("Upload Resumes")
    uploaded_files = st.sidebar.file_uploader("Upload Resume Files (PDF/DOCX)", accept_multiple_files=True, type=["pdf", "docx"])
    job_description = st.sidebar.text_area("Paste Job Description")
    
    if st.sidebar.button("Process Resumes"):
        if uploaded_files and job_description:
            st.write("### Processing resumes...")
            results = process_resumes(uploaded_files, job_description)
            
            # Loop over each result and display in expandable sections
            for result in results:
                with st.expander(result[0]):
                    st.subheader("Extracted Skills & Experience:")
                    st.write(result[1])  # Display extracted skills and experience
                    st.subheader("Match Score & Suggestions:")
                    st.write(result[2])  # Display match score and suggestions
                
                st.markdown("---")  # Add a horizontal line for separation
            
        else:
            st.warning("Please upload resumes and enter a job description.")

if __name__ == "__main__":
    main()
