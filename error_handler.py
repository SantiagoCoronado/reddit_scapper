import prawcore
import requests
from typing import Optional


class RedditAPIError(Exception):
    """Custom exception for Reddit API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ErrorHandler:
    """Centralized error handling for Reddit API operations"""
    
    @staticmethod
    def handle_reddit_api_error(error: prawcore.exceptions.ResponseException) -> None:
        """Handle Reddit API response errors"""
        status_code = error.response.status_code
        
        error_messages = {
            401: "Invalid Reddit API credentials. Please check your credentials in the .env file.",
            403: "Access forbidden. Your Reddit app may not have the required permissions.",
            404: "The requested subreddit or resource was not found. Please verify the subreddit name is correct.",
            429: "Rate limit exceeded. Please wait before making more requests.",
            500: "Reddit servers are experiencing issues. Please try again later.",
            502: "Reddit servers are experiencing issues. Please try again later.",
            503: "Reddit servers are experiencing issues. Please try again later."
        }
        
        if status_code in error_messages:
            message = error_messages[status_code]
        elif status_code >= 500:
            message = "Reddit servers are experiencing issues. Please try again later."
        else:
            message = f"Reddit API request failed with status code {status_code}. Please check your search parameters and try again."
        
        raise RedditAPIError(message, status_code)
    
    @staticmethod
    def handle_network_error(error: requests.RequestException) -> None:
        """Handle network-related errors"""
        if isinstance(error, requests.exceptions.ConnectionError):
            message = "Network connection error. Please check your internet connection and try again."
        elif isinstance(error, requests.exceptions.Timeout):
            message = "Request timed out. Please try again later."
        elif isinstance(error, requests.exceptions.RequestException):
            message = "Network error occurred. Please check your connection and try again."
        else:
            message = f"Network error: {str(error)}"
        
        raise RedditAPIError(message)
    
    @staticmethod
    def handle_credentials_error(missing_credentials: list) -> None:
        """Handle missing credentials error"""
        message = f"Missing required Reddit API credentials: {', '.join(missing_credentials)}"
        raise RedditAPIError(message)
    
    @staticmethod
    def handle_general_error(error: Exception) -> None:
        """Handle general unexpected errors"""
        message = f"An unexpected error occurred: {str(error)}"
        raise RedditAPIError(message)
    
    @staticmethod
    def print_error(error: RedditAPIError) -> None:
        """Print formatted error message to console"""
        print(f"Error: {error.message}")
        
        # Add helpful hints based on error type
        if error.status_code == 401:
            print("Make sure you have created a Reddit app and are using the correct Client ID and Secret.")
        elif error.status_code == 429:
            print("Consider reducing the frequency of your requests or increasing timeframe between searches.")
        elif error.status_code == 404:
            print("Double-check the subreddit name spelling and ensure it exists.")