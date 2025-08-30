import os
import json
from dotenv import load_dotenv
from models import RedditScraper
from utils import parse_args, ensure_data_dir, validate_credentials
from error_handler import ErrorHandler, RedditAPIError
import prawcore
import requests

# Load environment variables from .env file
load_dotenv()

def get_system_prompt():
    """Extract system prompt from prompt.md file."""
    try:
        with open('prompt.md', 'r', encoding='utf-8') as f:
            prompt_content = f.read()
    except FileNotFoundError:
        raise RedditAPIError("prompt.md file not found")
    except Exception as e:
        raise RedditAPIError(f"Error reading prompt.md: {str(e)}")
    
    # Extract system prompt (assuming it's after "## System Prompt")
    system_prompt = ""
    try:
        lines = prompt_content.split('\n')
        in_system_section = False
        for line in lines:
            if line.strip() == "## System Prompt":
                in_system_section = True
                continue
            elif line.startswith("## ") and in_system_section:
                break
            elif in_system_section:
                system_prompt += line + '\n'
        
        system_prompt = system_prompt.strip()
        if not system_prompt:
            raise ValueError("No system prompt found")
            
        return system_prompt
    except Exception as e:
        raise RedditAPIError(f"Error parsing system prompt from prompt.md: {str(e)}")

def call_anthropic_api(research_question, system_prompt):
    """Send request to Anthropic Claude API."""
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        raise RedditAPIError("CLAUDE_API_KEY environment variable is required for Anthropic")
    
    # Get model from environment variable, default to claude-sonnet-4-20250514
    model = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01'
    }
    
    data = {
        'model': model,
        'max_tokens': 1000,
        'system': system_prompt,
        'messages': [
            {
                'role': 'user',
                'content': f'Research Query: "{research_question}"\n\nPlease provide Reddit scraping suggestions to help gather data for this research.'
            }
        ]
    }
    
    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'content' in result and result['content']:
            return result['content'][0]['text']
        else:
            raise RedditAPIError("No response content received from Anthropic API")
    else:
        raise RedditAPIError(f"Anthropic API error: {response.status_code} - {response.text}")

def call_openai_api(research_question, system_prompt):
    """Send request to OpenAI GPT API."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RedditAPIError("OPENAI_API_KEY environment variable is required for OpenAI")
    
    # Get model from environment variable, default to gpt-4
    model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        'model': model,
        'max_tokens': 1000,
        'messages': [
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': f'Research Query: "{research_question}"\n\nPlease provide Reddit scraping suggestions to help gather data for this research.'
            }
        ]
    }
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and result['choices']:
            return result['choices'][0]['message']['content']
        else:
            raise RedditAPIError("No response content received from OpenAI API")
    else:
        raise RedditAPIError(f"OpenAI API error: {response.status_code} - {response.text}")

def research_assistant(research_question, provider):
    """Send research question to specified LLM provider and display response."""
    try:
        # Get system prompt
        system_prompt = get_system_prompt()
        
        # Call appropriate API
        if provider == 'anthropic':
            response_text = call_anthropic_api(research_question, system_prompt)
        elif provider == 'openai':
            response_text = call_openai_api(research_question, system_prompt)
        else:
            raise RedditAPIError(f"Unsupported provider: {provider}")
        
        print(response_text)
        
    except requests.RequestException as e:
        ErrorHandler.print_error(RedditAPIError(f"Network error communicating with {provider} API: {str(e)}"))
    except RedditAPIError as e:
        ErrorHandler.print_error(e)
    except Exception as e:
        ErrorHandler.print_error(RedditAPIError(f"Unexpected error: {str(e)}"))

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Handle research mode
    if args.research:
        research_assistant(args.research, args.provider)
        return
    
    # Get Reddit API credentials from environment variables
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')

    # Validate credentials
    try:
        validate_credentials(client_id, client_secret, user_agent)
    except RedditAPIError as e:
        ErrorHandler.print_error(e)
        print("Please set the following environment variables:")
        for cred in ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']:
            if not os.getenv(cred):
                print(f"  - {cred}")
        return

    # Ensure data directory exists and get full output path
    data_dir = ensure_data_dir()
    output_path = os.path.join(data_dir, args.output)
    if not output_path.endswith('.json'):
        output_path += '.json'

    try:
        # Initialize the scraper with custom timeframe
        scraper = RedditScraper(client_id, client_secret, user_agent, 
                               days_ago=args.timeframe)

        # Perform the search with the provided criteria
        posts_data = scraper.search_posts(
            subreddit=args.subreddit,
            title=args.title,
            content=args.content,
            limit=args.limit
        )

        # Save the results
        scraper.save_posts(posts_data, output_path)
    except prawcore.exceptions.ResponseException as e:
        try:
            ErrorHandler.handle_reddit_api_error(e)
        except RedditAPIError as api_error:
            ErrorHandler.print_error(api_error)
        return
    except requests.RequestException as e:
        try:
            ErrorHandler.handle_network_error(e)
        except RedditAPIError as net_error:
            ErrorHandler.print_error(net_error)
        return
    except Exception as e:
        try:
            ErrorHandler.handle_general_error(e)
        except RedditAPIError as gen_error:
            ErrorHandler.print_error(gen_error)
        return

if __name__ == "__main__":
    main()
