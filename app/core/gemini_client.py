from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.core.config import config

text_model = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash', temperature=0.2, api_key=config.GOOGLE_AI_API_KEY
)

embedding_model = GoogleGenerativeAIEmbeddings(
    model='gemini-embedding-2',
    output_dimensionality=1536,
    api_key=config.GOOGLE_AI_API_KEY,
)


async def get_text_model() -> ChatGoogleGenerativeAI:
    return text_model


async def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    return embedding_model
