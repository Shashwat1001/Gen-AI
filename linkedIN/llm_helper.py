from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()   

llm = ChatGroq(
    model_name="llama3-70b-8192",  # ✅ valid Groq model
    temperature=0,
    groq_api_key=os.getenv("GROQ_KEY")
)

if __name__ == "__main__":
    response = llm.invoke("What is the capital of France?")
    print(response.content)
    # Output: "The capital of France is Paris."

