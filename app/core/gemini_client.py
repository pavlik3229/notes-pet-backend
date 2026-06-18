from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import config

llm = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash', temperature=0.2, api_key=config.GOOGLE_AI_API_KEY
)


async def get_llm():
    return llm
