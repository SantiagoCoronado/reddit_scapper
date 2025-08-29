import argparse
import os
from dotenv import load_dotenv
from models import RedditScraper
import prawcore  # For handling Reddit API errors

# Load environment variables from .env file
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(
        description='Reddit Post Scraper - A tool to scrape and save Reddit posts with flexible search criteria',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Search all of Reddit for posts about AI
  python main.py -o ai_posts.json -t "artificial intelligence"

  # Get recent posts from r/Programming (last 30 days)
  python main.py -o programming_posts.json -s Programming --timeframe 30

  # Search r/Technology for posts about ChatGPT (limit to 50 posts)
  python main.py -o chatgpt_tech.json -s Technology -t chatgpt -l 50

  # Find gaming posts discussing performance issues
  python main.py -o gaming_performance.json -s Gaming -t performance -c "fps|lag|stuttering"

  # Get trending posts from r/WorldNews in the last week
  python main.py -o weekly_news.json -s WorldNews --timeframe 7
        '''
    )
    
    # Required arguments
    parser.add_argument('--output', '-o', type=str, required=True,
                      help='Output JSON file name where the scraped posts will be saved')
    
    # Optional arguments with defaults
    parser.add_argument('--subreddit', '-s', type=str, default='all',
                      help='Subreddit to search (default: "all" for all of Reddit)')
    parser.add_argument('--title', '-t', type=str,
                      help='Search for posts containing this term in their titles')
    parser.add_argument('--content', '-c', type=str,
                      help='Search for posts containing this term in their content/body')
    parser.add_argument('--timeframe', '-tf', type=int, default=365,
                      help='Number of days to look back (default: 365 days)')
    parser.add_argument('--limit', '-l', type=int, default=None,
                      help='Maximum number of posts to retrieve (default: None, retrieves all matching posts)')
    
    return parser.parse_args()

def ensure_data_dir():
    """Create the data directory if it doesn't exist."""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

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
