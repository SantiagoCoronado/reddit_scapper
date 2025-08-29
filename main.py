import argparse
import os
from dotenv import load_dotenv
from models import RedditScraper

# Load environment variables from .env file
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(
        description='Reddit Post Scraper - A tool to scrape and save Reddit posts with flexible search criteria',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Search all of Reddit for posts about AI
  python main.py -o data/ai_posts.json -t "artificial intelligence"

  # Get recent posts from r/Programming (last 30 days)
  python main.py -o data/programming_posts.json -s Programming --timeframe 30

  # Search r/Technology for posts about ChatGPT (limit to 50 posts)
  python main.py -o data/chatgpt_tech.json -s Technology -t chatgpt -l 50

  # Find gaming posts discussing performance issues
  python main.py -o data/gaming_performance.json -s Gaming -t performance -c "fps|lag|stuttering"

  # Get trending posts from r/WorldNews in the last week
  python main.py -o data/weekly_news.json -s WorldNews --timeframe 7
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

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Get Reddit API credentials from environment variables
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')

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
    scraper.save_posts(posts_data, args.output)

if __name__ == "__main__":
    main()

print("Searching all of Reddit for posts containing 'padel' in their titles from the last year...")

# Use Reddit's search functionality to find posts across all subreddits
for submission in reddit.subreddit("all").search(
    'title:padel', 
    sort='new', 
    time_filter='year', 
    limit=None
):
    # Stop if we reach posts older than a year
    post_time = submission.created_utc
    if post_time < one_year_ago:
        break
        
    # Extract post data and comments
    submission.comments.replace_more(limit=None)  # Expand all "load more comments" links
    comments_data = []
    for comment in submission.comments:
        if isinstance(comment, praw.models.Comment):
            comments_data.append(get_comments_data(comment))
    
    post_data = {
        'id': submission.id,
        'subreddit': str(submission.subreddit),
        'title': submission.title,
        'url': submission.url,
        'created_utc': submission.created_utc,
        'created_date': datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat(),
        'author': str(submission.author),
        'score': submission.score,
        'upvote_ratio': submission.upvote_ratio,
        'num_comments': submission.num_comments,
        'selftext': submission.selftext,  # Post content/body
        'permalink': submission.permalink,
        'comments': comments_data
    }
    
    posts_data.append(post_data)
    print(f"Fetched post: {submission.title}")

print(f"\nTotal posts collected: {len(posts_data)}")

# Save to JSON file
output_file = 'title_includes_padel.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(posts_data, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(posts_data)} posts from all subreddits to {output_file}")
