from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq



llm = ChatGroq(
    model_name="llama3-70b-8192",  # ✅ valid Groq model
    temperature=0,
    #api_key='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'               # ✅ correct argument name
)

response = llm.invoke("What is the capital of France?")
print(response.content)