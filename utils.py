import openai
import os
from openai import OpenAI  # Import the OpenAI class

def build_prompt(user_question, retrieved_chunks):
    prompt = "You are a helpful financial assistant designed to answer questions about investing, finance, and money management using information from Fidelity Learning Center.\n\n"
    prompt += "Here is some relevant information that might help answer the user's question:\n---\n"
    
    for chunk in retrieved_chunks:
        # Chunks are now plain text content from Pinecone
        prompt += f"Content: {chunk}\n---\n"
    
    prompt += f"\nUser Question: {user_question}\n\n"
    prompt += "Based on the financial information provided above, answer the user's question clearly and helpfully. If the context doesn't contain enough information to answer the question, please say so and provide general guidance where appropriate. Focus on being educational and helpful for someone learning about finance."
    return prompt

def format_response_with_references(response_text, retrieved_metadatas):
    """
    Formats the response text with references to the source documents.

    Args:
        response_text: The chatbot's response text.
        retrieved_metadatas: A list of metadata dictionaries returned from Pinecone.

    Returns:
        The formatted response text with references.
    """
    formatted_response = response_text + "\n\n"
    
    if retrieved_metadatas and len(retrieved_metadatas) > 0:
        formatted_response += "**Sources:**\n"
        seen_urls = set()  # To avoid duplicate URLs
        
        for i, metadata in enumerate(retrieved_metadatas, 1):
            if isinstance(metadata, dict):
                source = metadata.get("source", "Unknown Source")
                url = metadata.get("url", "")
                
                # Create a better display name from URL if source is generic
                display_name = source
                if source == "Fidelity Learn | Financial articles, webinars, and more | Fidelity" and url:
                    # Extract topic from URL
                    url_parts = url.split('/')
                    if len(url_parts) > 0:
                        topic = url_parts[-1].replace('-', ' ').title()
                        if topic:
                            display_name = f"Fidelity Learning Center - {topic}"
                
                # Only add unique URLs
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    if url != "":
                        formatted_response += f"- [{display_name}]({url})\n"
                    else:
                        formatted_response += f"- {display_name}\n"
    
    return formatted_response

def get_openai_response(prompt, retrieved_metadatas):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI()  # Create an instance of the OpenAI client
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        response_text = response.choices[0].message.content
        formatted_response = format_response_with_references(response_text, retrieved_metadatas)
        return formatted_response
    except Exception as e:
        return f"I apologize, but I encountered an error while generating a response: {str(e)}"