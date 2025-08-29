import praw
import json
from datetime import datetime, timezone
import time

class RedditScraper:
    def __init__(self, client_id, client_secret, user_agent, days_ago=365):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.cutoff_time = int(time.time() - days_ago * 24 * 60 * 60)

    def get_comments_data(self, comment):
        """Recursively get all comments and their replies"""
        comment_data = {
            'id': comment.id,
            'author': str(comment.author),
            'body': comment.body,
            'created_utc': comment.created_utc,
            'created_date': datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat(),
            'score': comment.score,
            'replies': []
        }
        
        # Get all replies if they exist
        if hasattr(comment, 'replies'):
            for reply in comment.replies:
                if isinstance(reply, praw.models.Comment):
                    comment_data['replies'].append(self.get_comments_data(reply))
        
        return comment_data

    def scrape_subreddit(self, subreddit_name, search_term=None):
        """Scrape posts from a specific subreddit"""
        print(f"Fetching posts from r/{subreddit_name} from the last year...")
        subreddit = self.reddit.subreddit(subreddit_name)
        posts_data = []

        # Get posts either by search or just new
        if search_term:
            submissions = subreddit.search(f'title:{search_term}', sort='new', time_filter='year', limit=None)
        else:
            submissions = subreddit.new(limit=None)

        for submission in submissions:
            # Stop if we reach posts older than a year
            if submission.created_utc < self.one_year_ago:
                break

            posts_data.append(self._process_submission(submission))
            print(f"Fetched post: {submission.title}")

        return posts_data

    def search_posts(self, subreddit="all", title=None, content=None, limit=None):
        """Search for posts with flexible criteria"""
        query_parts = []
        if title:
            query_parts.append(f'title:"{title}"')
        if content:
            query_parts.append(f'selftext:"{content}"')
        
        query = " AND ".join(query_parts) if query_parts else ""
        
        print(f"Searching r/{subreddit} for posts matching criteria:")
        if title:
            print(f"- Title contains: {title}")
        if content:
            print(f"- Content contains: {content}")
            
        posts_data = []
        posts_seen = 0

        # If no specific search terms, get posts by new
        if not query:
            submissions = self.reddit.subreddit(subreddit).new(limit=limit)
        else:
            submissions = self.reddit.subreddit(subreddit).search(
                query,
                sort='new',
                syntax='lucene',
                limit=limit
            )

        for submission in submissions:
            if submission.created_utc < self.cutoff_time:
                break
                
            if limit and posts_seen >= limit:
                break

            posts_data.append(self._process_submission(submission))
            posts_seen += 1
            print(f"Fetched post: {submission.title}")

        return posts_data

    def _process_submission(self, submission):
        """Process a submission and its comments"""
        submission.comments.replace_more(limit=None)
        comments_data = []
        
        for comment in submission.comments:
            if isinstance(comment, praw.models.Comment):
                comments_data.append(self.get_comments_data(comment))

        return {
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
            'selftext': submission.selftext,
            'permalink': submission.permalink,
            'comments': comments_data
        }

    def save_posts(self, posts_data, filename):
        """Save posts to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(posts_data)} posts to {filename}")
