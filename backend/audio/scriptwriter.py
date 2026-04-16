import os
import sys
from pydantic import BaseModel, Field
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from datetime import date

def generate_podcast_script(summaries: list[dict]) -> str:
    """Takes approved summaries and uses Groq to write a conversational podcast script."""
    if not summaries:
        return "Welcome to Pulse AI. There are no major updates today, but check back tomorrow for the latest in Artificial Intelligence."
        
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        return ""
        
    llm = ChatGroq(
        api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=6000
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the official scriptwriter for the 'Pulse AI Daily Briefing' podcast.
Your job is to take raw news summaries and weave them into a smooth, highly-engaging, fast-paced radio script.
The tone should be highly conversational and enthusiastic (similar to a dynamic tech podcast host).

Rules for the Script:
1. Start organically: 'Hey everyone, welcome to the Pulse AI Daily Briefing for [DATE]. I'm your host, and we have some massive stories today...'
2. Do not use Markdown, bullet points, or list numbers. Write it exactly as conversational dialogue.
3. TRUTH & CADENCE: Use filler words naturally! Use words like 'now', 'so', 'wow', 'get this', and 'listen to this' to make the Text-To-Speech engine sound 100% human and less robotic. Use commas heavily to force the engine to pause correctly.
4. Keep the entire script under 2-3 minutes of speaking time.
5. End smoothly: 'That's all the time we have today. Click the subscribe button, and I'll see you tomorrow!'
"""),
        ("user", "Today is {date}. Here are the stories:\n\n{stories}")
    ])
    
    stories_text = ""
    for idx, s in enumerate(summaries, 1):
        title = s.get('articles', {}).get('title', 'Unknown Title')
        summary = s.get('summary_text', '')
        stories_text += f"Story {idx} Headline: {title}\nSummary: {summary}\n\n"
        
    chain = prompt | llm
    
    response = chain.invoke({
        "date": date.today().strftime("%B %d, %Y"),
        "stories": stories_text
    })
    
    return response.content
