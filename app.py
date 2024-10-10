import openai
import requests
from datetime import datetime
from huggingface_hub import HfApi
import gradio as gr

# Set up our API keys for OpenAI and Hugging Face
OPENAI_API_KEY = "openai-api-key"
HF_API_TOKEN = "hf-api-token"
HF_REPO_ID = "hf-repo-id"

# Initialize APIs
openai.api_key = OPENAI_API_KEY
hf_api = HfApi()

# Step 1: Fetch Arxiv Papers (Computer Science Section)
def fetch_arxiv_papers():
    url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=5&sortBy=submittedDate&sortOrder=descending"
    response = requests.get(url)
    papers = parse_arxiv_response(response.text)
    return papers

def parse_arxiv_response(xml_response):
    # Simplified parsing logic
    papers = []
    # Code to parse XML response (PLEASE ADDRESS)
    # Extract title, authors, abstract, and PDF URL of each paper (Selenium? Parser?)
    return papers

# Step 2: Analyze Paper with o1 Preview API - could be other cheaper api too
def check_feasibility(paper_content):
    prompt = f"Analyze the following paper and determine if it is implementable in code:\n\n{paper_content}"
    response = openai.Completion.create(
        engine="text-davinci-002",  # Replace with o1 preview engine
        prompt=prompt,
        max_tokens=200
    )
    return response['choices'][0]['text'].strip()

# Step 3: Generate Documentation and Code Sample (may want to chain in results from prior feasibility step in the input here too)
def generate_docs_and_code(paper_content):
    prompt = f"Generate simplified documentation and code samples for this paper:\n\n{paper_content}"
    response = openai.Completion.create(
        engine="text-davinci-002",  # Replace with o1 preview engine
        prompt=prompt,
        max_tokens=500
    )
    return response['choices'][0]['text'].strip()

# Step 4: Push Dataset to Hugging Face Hub
def push_to_huggingface(papers_data):
    # Prepare dataset (JSON, CSV, etc.)
    dataset_path = "papers_dataset.json"  # Example dataset
    with open(dataset_path, "w") as f:
        f.write(str(papers_data))
    
    hf_api.upload_file(
        path_or_fileobj=dataset_path,
        path_in_repo="papers_dataset.json",
        repo_id=HF_REPO_ID,
        token=HF_API_TOKEN
    )

# Main Agentic AI Loop
def process_papers_and_push():
    papers = fetch_arxiv_papers()
    results = []
    
    for paper in papers:
        # Extract paper details
        title = paper.get("title")
        abstract = paper.get("abstract")
        
        # Step 2: Check feasibility with o1 API
        feasibility = check_feasibility(abstract)
        
        # Step 3: Generate documentation and code
        docs_and_code = generate_docs_and_code(abstract)
        
        # Prepare result
        result = {
            "title": title,
            "abstract": abstract,
            "feasibility": feasibility,
            "docs_and_code": docs_and_code
        }
        results.append(result)
    
    # Step 4: Push dataset to Hugging Face Hub
    push_to_huggingface(results)
    
    return results

# Step 5: Display Results in Gradio UI
def display_results():
    results = process_papers_and_push()
    
    def format_result(result):
        formatted = f"**Title:** {result['title']}\n\n"
        formatted += f"**Abstract:** {result['abstract']}\n\n"
        formatted += f"**Feasibility Evaluation:** {result['feasibility']}\n\n"
        formatted += f"**Docs & Code:** {result['docs_and_code']}\n\n"
        return formatted
    
    output = "\n\n".join([format_result(result) for result in results])
    return output

# Gradio UI
app = gr.Interface(
    fn=display_results,
    inputs=None,
    outputs="markdown",
    title="Arxiv Papers Feasibility & Code Generator"
)

if __name__ == "__main__":
    app.launch()
