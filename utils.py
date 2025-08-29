import argparse
import os

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
