# Reddit Scraper

A flexible command-line tool to scrape and analyze Reddit posts based on various search criteria.

## Features

- Search across all of Reddit or specific subreddits
- Filter posts by title and/or content
- Customizable time frame for post collection
- Save results in JSON format
- Configurable post limit
- **Smart Research Assistant**: Get AI-powered suggestions for Reddit research strategies
- **Multi-LLM Support**: Choose between Anthropic Claude or OpenAI ChatGPT

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd reddit_scrapper
```

2. Install required packages:
```bash
pip install praw python-dotenv requests
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API credentials in `.env`

   **For Reddit Scraping:**
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=reddit_scrapper by /u/YOUR_USERNAME
   ```

   **For Research Assistant (choose one or both):**
   ```
   # For Anthropic Claude
   CLAUDE_API_KEY=your_claude_api_key_here
   CLAUDE_MODEL=claude-sonnet-4-20250514  # Optional: defaults to claude-sonnet-4-20250514

   # For OpenAI ChatGPT
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4  # Optional: defaults to gpt-4
   ```

   **Getting API credentials:**
   
   *Reddit API:*
   1. Visit https://www.reddit.com/prefs/apps
   2. Click "create another app..."
   3. Fill in the required information
   4. Copy the client ID and client secret to your `.env` file

   *Anthropic API:*
   1. Visit https://console.anthropic.com/
   2. Sign up/login and go to API Keys
   3. Create a new API key and copy it to your `.env` file

   *OpenAI API:*
   1. Visit https://platform.openai.com/api-keys
   2. Sign up/login and create a new API key
   3. Copy the API key to your `.env` file

## Usage Examples

### Reddit Scraping

1. Search all of Reddit for posts about AI:
```bash
python main.py -o ai_posts.json -t "artificial intelligence"
```

2. Get recent posts from r/Programming (last 30 days):
```bash
python main.py -o programming_posts.json -s Programming --timeframe 30
```

3. Search r/Technology for posts about ChatGPT (limit to 50 posts):
```bash
python main.py -o chatgpt_tech.json -s Technology -t chatgpt -l 50
```

4. Find gaming posts discussing performance issues:
```bash
python main.py -o gaming_performance.json -s Gaming -t performance -c "fps|lag|stuttering"
```

### Research Assistant

5. Get research suggestions using Anthropic Claude (default):
```bash
python main.py -r "What are the best programming languages for beginners?"
```

6. Get research suggestions using OpenAI ChatGPT:
```bash
python main.py -r "How can I learn machine learning effectively?" -p openai
```

7. Research emerging tech trends with Claude:
```bash
python main.py -r "What are the latest trends in artificial intelligence?" -p anthropic
```

## Command Line Arguments

### Reddit Scraping Mode
- `-o, --output`: Output JSON file name (Required for scraping)
- `-s, --subreddit`: Subreddit to search (default: "all")
- `-t, --title`: Search for posts containing this term in their titles
- `-c, --content`: Search for posts containing this term in their content/body
- `-tf, --timeframe`: Number of days to look back (default: 365)
- `-l, --limit`: Maximum number of posts to retrieve (default: None)

### Research Assistant Mode
- `-r, --research`: Research question to send to LLM API (skips scraping)
- `-p, --provider`: LLM provider to use: `anthropic` or `openai` (default: `anthropic`)

## Changing LLM Models

You can customize which specific models to use by setting environment variables in your `.env` file:

### Anthropic Claude Models
```bash
# Available Claude models (set in .env)
CLAUDE_MODEL=claude-sonnet-4-20250514      # Latest Sonnet 4 (default)
CLAUDE_MODEL=claude-3-5-sonnet-20241022    # Claude 3.5 Sonnet
CLAUDE_MODEL=claude-3-5-haiku-20241022     # Claude 3.5 Haiku (faster, cheaper)
CLAUDE_MODEL=claude-3-opus-20240229        # Claude 3 Opus (most capable)
```

### OpenAI ChatGPT Models  
```bash
# Available OpenAI models (set in .env)
OPENAI_MODEL=gpt-4                         # GPT-4 (default)
OPENAI_MODEL=gpt-4-turbo                   # GPT-4 Turbo (faster)
OPENAI_MODEL=gpt-4o                        # GPT-4o (latest)
OPENAI_MODEL=gpt-3.5-turbo                 # GPT-3.5 Turbo (cheaper)
```

### Example Usage with Different Models

1. Use Claude 3.5 Haiku for faster responses:
```bash
# Set in .env: CLAUDE_MODEL=claude-3-5-haiku-20241022
python main.py -r "Quick research question" -p anthropic
```

2. Use GPT-4 Turbo for faster OpenAI responses:
```bash
# Set in .env: OPENAI_MODEL=gpt-4-turbo  
python main.py -r "Research question" -p openai
```

3. Switch providers on the fly:
```bash
# Use Claude (default)
python main.py -r "Question for Claude"

# Use OpenAI
python main.py -r "Same question for ChatGPT" -p openai
```

## Output Format

### Reddit Scraping Output

The tool automatically saves all output files in the `data` directory within the project. You don't need to specify the directory in the command - just provide the desired filename and it will be placed in the correct location.

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

### Research Assistant Output

The Research Assistant provides structured suggestions directly to your terminal, including:

- **Relevant Subreddits**: 3-5 specific subreddit recommendations with explanations
- **Search Keywords**: Multiple keyword sets for different aspects of your research
- **Timeframe Recommendations**: Suggested time ranges based on topic patterns  
- **Data Collection Strategy**: Brief explanation of how the suggestions help your research

The output is formatted for easy reading and can be used directly with the scraping commands.

## License

[Your chosen license]
