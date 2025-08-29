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
    if not all([client_id, client_secret, user_agent]):
        print("Error: Reddit API credentials are not set. Please set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT environment variables.")
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
        if e.response.status_code == 401:
            print("Error: Invalid Reddit API credentials. Please check your credentials in the .env file.")
            print("Make sure you have created a Reddit app and are using the correct Client ID and Secret.")
            return
        else:
            print(f"Error: Reddit API returned an error: {e}")
            return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

if __name__ == "__main__":
    main()
    # Stop further execution if credentials are not set (handled in main)
