from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq



llm = ChatGroq(
    model_name="llama3-70b-8192",  # ✅ valid Groq model
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

response = llm.invoke("What is the capital of France?")
print(response.content)