import os
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd
import chromadb
import uuid
load_dotenv()

client = chromadb.PersistentClient('vectorstore')
collection = client.get_or_create_collection(name="portfolio")

df = pd.read_csv('my_portfolio.csv')

llm = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0,
    #api_key=''
)

loader = WebBaseLoader(
    "https://careers.nike.com/omni-channel-services-specialist/job/R-64972",  # Optional, avoids 403
)

page_data = loader.load().pop().page_content

prompt_extract = PromptTemplate.from_template(
    """
    You are an expert in extracting information from job postings.
    Extract the following information from the job posting below:
    
    {page_data}

    Return ONLY the extracted information in JSON format:
    - Job Title
    - Company Name
    - Location
    - Job Description

    No preamble. No postamble. Just valid JSON.
    """
)

chain_extract = prompt_extract | llm

res = chain_extract.invoke({"page_data": page_data})

json_parser = JsonOutputParser()
json_response = json_parser.parse(res.content)

if not collection.count():
    for _, row in df.iterrows():
        collection.add(
            documents=[row['Techstack']],
            metadatas=[{"links": row['Links']}],
            ids=[str(uuid.uuid4())])



links = collection.query(
    query_texts=["Job Description"],n_results=2).get("metadatas",[])


job = json_response

prompt_email = PromptTemplate.from_template(
    """
    You are Mohan, Business development executive at AtLiQ.
    You are an expert in writing professional emails.
    Write a cover letter for the following job posting:

    Job Title: {job_title}
    Company Name: {company_name}
    Location: {location}
    Job Description: {job_description}

    Use the following links to support your application:
    {links}

    The email should be concise, professional, and tailored to the job.
    """
)

chain_email = prompt_email | llm
res = chain_email.invoke({
    "job_title": job.get("Job Title"),
    "company_name": job.get("Company Name"),
    "location": job.get("Location"),
    "job_description": job.get("Job Description"),
    "links": links
})


