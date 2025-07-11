import json
import os
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_helper import llm  # Assuming llm is defined in llm_helper.py

def clean_surrogates(s):
    if isinstance(s, str):
        return s.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
    return s

def get_unified_tags (post_with_metadata):
    unique_tags = set()
    for post in post_with_metadata:
        if 'tags' in post and post['tags']:
            unique_tags.update(post['tags'])
        else:
            print("Warning: Post missing 'tags' key or empty tags:", post)
    if not unique_tags:
        print("No tags found to unify. Skipping tag unification.")
        return {}       
    unique_tags_list = ', '.join(unique_tags)
    template = '''I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list. 
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search". 
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
    2. Each tag should be follow title case convention. example: "Motivation", "Job Search"
    3. Output should be a JSON object, No preamble
    3. Output should have mapping of original tag and the unified tag. 
       For example: {{"Jobseekers": "Job Search",  "Job Hunting": "Job Search", "Motivation": "Motivation}}
    
    Here is the list of tags: 
    {tags}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"tags": str(unique_tags_list)})
    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return res
    

def process_post(raw_file_path, processed_file_path='data/processed_posts.json'):
    enriched_posts = []
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)
        for post in posts:
            # Clean all string fields in the post
            clean_post = {k: clean_surrogates(v) for k, v in post.items()}
            metadata = extract_metadata(clean_post['text'])
            post_with_metadata = {**clean_post, **metadata}
            enriched_posts.append(post_with_metadata)
    # Save processed posts
    unified_tags = get_unified_tags(enriched_posts)
    for post in enriched_posts:
        current_tags = post['tags']
        new_tags = {unified_tags[tag] for tag in current_tags}
        post['tags'] = list(new_tags)

    with open(processed_file_path, encoding='utf-8', mode="w") as outfile:
        json.dump(enriched_posts, outfile, indent=4)
        

def extract_metadata(text):
    # Remove invalid unicode surrogates
    clean_text = text.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
    template = PromptTemplate.from_template(
        """
        You are an expert in analyzing text.
        Extract the following metadata from the text below:
        Text should be in English and related to mental health, motivation, or inspiration.
        
        {text}

        Return ONLY the extracted metadata in JSON format:
        - line_count: Number of lines in the text
        No Preamble. No postamble. Just valid JSON.
        """
    )
    chain = template | llm
    try:
        response = chain.invoke({"text": clean_text})
        json_parser = JsonOutputParser()
        metadata = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse metadata.")
    # Ensure 'tags' key exists
    if 'tags' not in metadata:
        metadata['tags'] = []
    return metadata

if __name__ == "__main__":
    process_post('data/raw_posts.json', 'data/processed_posts.json')