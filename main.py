import os
from dotenv import load_dotenv
from models import RedditScraper
from utils import parse_args, ensure_data_dir, validate_credentials
from error_handler import ErrorHandler, RedditAPIError
import prawcore
import requests

# Load environment variables from .env file
load_dotenv()

def main():
    # Parse command line arguments
    args = parse_args()
    
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
