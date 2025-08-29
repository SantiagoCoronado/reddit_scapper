import os
from dotenv import load_dotenv
from models import RedditScraper
import prawcore  # For handling Reddit API errors
from utils import parse_args, ensure_data_dir

# Load environment variables from .env file
load_dotenv()

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Get Reddit API credentials from environment variables
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')

    # Check if credentials are set
    missing_credentials = []
    if not client_id:
        missing_credentials.append('REDDIT_CLIENT_ID')
    if not client_secret:
        missing_credentials.append('REDDIT_CLIENT_SECRET')
    if not user_agent:
        missing_credentials.append('REDDIT_USER_AGENT')
    
    if missing_credentials:
        print(f"Error: Missing required Reddit API credentials: {', '.join(missing_credentials)}")
        print("Please set the following environment variables:")
        for cred in missing_credentials:
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
        status_code = e.response.status_code
        if status_code == 401:
            print("Error: Invalid Reddit API credentials. Please check your credentials in the .env file.")
            print("Make sure you have created a Reddit app and are using the correct Client ID and Secret.")
        elif status_code == 403:
            print("Error: Access forbidden. Your Reddit app may not have the required permissions.")
        elif status_code == 429:
            print("Error: Rate limit exceeded. Please wait before making more requests.")
            print("Consider reducing the frequency of your requests or increasing timeframe between searches.")
        elif status_code == 404:
            print("Error: The requested subreddit or resource was not found.")
            print("Please verify the subreddit name is correct.")
        elif status_code >= 500:
            print("Error: Reddit servers are experiencing issues. Please try again later.")
        else:
            print(f"Error: Reddit API request failed with status code {status_code}.")
            print("Please check your search parameters and try again.")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

if __name__ == "__main__":
    main()
    # Stop further execution if credentials are not set (handled in main)
