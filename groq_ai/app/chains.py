import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()
class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, 
                            groq_api_key=os.getenv("GROQ_API_KEY"), 
                            model_name="llama3-70b-8192")

    def extract_jobs(self, cleaned_text):
        prompt = PromptTemplate.from_template(
            """
            You are an expert in extracting information from job postings.
            Extract the following information from the job posting below:

            {cleaned_text}

            Return ONLY the extracted information in JSON format:
            - Job Title
            - Company Name
            - Location
            - Job Description

            No preamble. No postamble. Just valid JSON.
            """
        )

        chain = prompt | self.llm
        try:
            response = chain.invoke({"cleaned_text": cleaned_text})
            json_parser = JsonOutputParser()
            response = json_parser.parse(response.content)
        except OutputParserException as e:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return response if isinstance(response, list) else [response]
    
    def generate_email(self, job , links):
        prompt_email = PromptTemplate.from_template(
            """
            You are an expert in writing cold emails.
            Write a cold email to the hiring manager of the company {company_name} for the job title {job_title}.
            The job is located in {location} and the job description is as follows:
            {job_description}

            Use the following links to understand my skills and experience:
            {links}

            Make sure to include a subject line, a greeting, a body, and a closing.
            """
        )
        chain_email = prompt_email | self.llm
        response = chain_email.invoke({
            "company_name": job.get("Company Name", "Unknown Company"),
            "job_title": job.get("Job Title", "Unknown Job Title"),
            "location": job.get("Location", "Unknown Location"),
            "job_description": job.get("Job Description", "No description provided."),
            "links": links
        })
        return response.content if response else "No email generated."
