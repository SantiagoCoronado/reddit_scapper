# Reddit Scraper

A flexible command-line tool to scrape and analyze Reddit posts based on various search criteria.

## Features

- Search across all of Reddit or specific subreddits
- Filter posts by title and/or content
- Customizable time frame for post collection
- Save results in JSON format
- Configurable post limit

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd reddit_scrapper
```

2. Install required packages:
```bash
pip install praw python-dotenv
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your Reddit API credentials in `.env`
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=reddit_scrapper by /u/YOUR_USERNAME
   ```

   To get Reddit API credentials:
   1. Visit https://www.reddit.com/prefs/apps
   2. Click "create another app..."
   3. Fill in the required information
   4. Once created, copy the client ID and client secret to your `.env` file

## Usage Examples

1. Search all of Reddit for posts with "padel" in the title:
```bash
python main.py -o title_includes_padel.json -t padel
```

2. Get all posts from r/Padel from the last 30 days:
```bash
python main.py -o recent_padel_posts.json -s Padel --timeframe 30
```

3. Search r/Padel for posts with "indoor" in the title and limit to 50 posts:
```bash
python main.py -o indoor_padel.json -s Padel -t indoor -l 50
```

4. Search for posts with "padel" in the title and "indoor" in the content:
```bash
python main.py -o indoor_padel_content.json -t padel -c indoor
```

## Command Line Arguments

- `-o, --output`: Output JSON file name (Required)
- `-s, --subreddit`: Subreddit to search (default: "all")
- `-t, --title`: Search for posts containing this term in their titles
- `-c, --content`: Search for posts containing this term in their content/body
- `-tf, --timeframe`: Number of days to look back (default: 365)
- `-l, --limit`: Maximum number of posts to retrieve (default: None)

## Output Format

The tool saves posts in JSON format with the following information for each post:
- Post ID
- Subreddit name
- Title
- URL
- Creation date
- Author
- Score
- Upvote ratio
- Number of comments
- Post content
- Permalink
- Comments data

## License

[Your chosen license]
