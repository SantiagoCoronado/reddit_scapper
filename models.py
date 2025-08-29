import praw
import json
from datetime import datetime, timezone
import time
import re

class RedditScraper:
    def __init__(self, client_id, client_secret, user_agent, days_ago=365):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.cutoff_time = int(time.time() - days_ago * 24 * 60 * 60)

    def _clean_comment_text(self, text):
        """Clean Reddit comment text for LLM processing"""
        if not text or text in ['[deleted]', '[removed]']:
            return None
            
        # Remove /u/username mentions
        text = re.sub(r'/u/\w+', '', text)
        # Remove /r/subreddit mentions
        text = re.sub(r'/r/\w+', '', text)
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'~~(.*?)~~', r'\1', text)     # Strikethrough
        text = re.sub(r'\^\((.*?)\)', r'\1', text)   # Superscript
        text = re.sub(r'`(.*?)`', r'\1', text)       # Code
        # Remove quotes
        text = re.sub(r'^&gt;.*$', '', text, flags=re.MULTILINE)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text if text else None

    def _is_quality_comment(self, comment):
        """Filter low-quality comments"""
        if not hasattr(comment, 'body') or not comment.body:
            return False
            
        # Skip deleted/removed comments
        if comment.body in ['[deleted]', '[removed]']:
            return False
            
        # Skip very short comments
        if len(comment.body) < 20:
            return False
            
        # Skip heavily downvoted comments
        if hasattr(comment, 'score') and comment.score < -5:
            return False
            
        return True

    def get_comments_data(self, comment, depth=0, max_depth=2):
        """Get comment data with quality filtering and limited depth"""
        if not self._is_quality_comment(comment) or depth > max_depth:
            return None
            
        cleaned_body = self._clean_comment_text(comment.body)
        if not cleaned_body:
            return None
            
        comment_data = {
            'id': comment.id,
            'author': str(comment.author),
            'body': cleaned_body,
            'created_utc': comment.created_utc,
            'created_date': datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat(),
            'score': comment.score,
            'word_count': len(cleaned_body.split()),
            'char_count': len(cleaned_body),
            'replies': []
        }
        
        # Get replies with limited depth
        if hasattr(comment, 'replies') and depth < max_depth:
            for reply in comment.replies:
                if isinstance(reply, praw.models.Comment):
                    reply_data = self.get_comments_data(reply, depth + 1, max_depth)
                    if reply_data:
                        comment_data['replies'].append(reply_data)
        
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
        """Process a submission and its comments with optimized fetching"""
        # Limit comment expansion to improve speed
        submission.comments.replace_more(limit=5)
        comments_data = []
        
        # Sort comments by score to get the best ones first
        top_comments = sorted(
            [c for c in submission.comments if isinstance(c, praw.models.Comment)],
            key=lambda x: x.score,
            reverse=True
        )
        
        # Limit to top 150 comments for LLM processing
        comment_count = 0
        max_comments = 150
        
        for comment in top_comments:
            if comment_count >= max_comments:
                break
                
            comment_data = self.get_comments_data(comment)
            if comment_data:
                comments_data.append(comment_data)
                comment_count += 1

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
            'comments': comments_data,
            'processed_comments': len(comments_data)
        }

    def save_posts(self, posts_data, filename):
        """Save posts to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(posts_data)} posts to {filename}")
