from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re
import numpy as np
from scipy.special import softmax
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import os
import tweepy
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Load model and vectorizer
try:
    model = joblib.load('svm_sentiment_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
except Exception as e:
    logger.error(f"Error loading model or vectorizer: {e}")
    raise

# Gemini API setup
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    logger.error(f"Gemini configuration failed: {e}")
    gemini_model = None

# Twitter API setup
try:
    # Using tweepy.Client for v2 API
    twitter_client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True  # Automatically wait if rate limit is hit
    )
except Exception as e:
    logger.error(f"Twitter API configuration failed: {e}")
    twitter_client = None

# Dummy text cleaner
def clean_text(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+|\#\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower().strip()

# Local model sentiment analysis
def predict_local_sentiment(text):
    try:
        cleaned_text = clean_text(text)
        vectorized_text = vectorizer.transform([cleaned_text])
        if hasattr(model, 'decision_function'):
            scores = model.decision_function(vectorized_text)[0]
        else:
            scores = model.predict_proba(vectorized_text)[0]
        probabilities = softmax(scores)
        sentiment_scores = {
            'positive': round(probabilities[2] * 100, 2),
            'neutral': round(probabilities[1] * 100, 2),
            'negative': round(probabilities[0] * 100, 2)
        }
        return sentiment_scores
    except Exception as e:
        logger.error(f"Local model prediction error: {e}")
        raise

# Gemini sentiment analysis
def predict_gemini_sentiment(text):
    if not gemini_model:
        logger.warning("Gemini model not initialized")
        return {'error': 'Gemini model not initialized'}

    try:
        prompt = (
            f"Analyze the sentiment of this text (positive, neutral, negative) and provide the result strictly in this format:\n"
            f"Positive: X%\nNeutral: Y%\nNegative: Z%\n"
            f"Where X, Y, Z are percentages that sum to 100%. Do not include any additional text or explanations.\n"
            f"Text: {text}"
        )

        response = gemini_model.generate_content(prompt, request_options={'timeout': 10})
        logger.info(f"Gemini raw response for text '{text}':\n{response.text}")

        gemini_result = {'text_sentiment': None}

        # Parse text sentiment
        positive, neutral, negative = None, None, None
        lines = response.text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Positive:'):
                match = re.search(r'Positive:\s*(\d+\.?\d*)%?', line, re.IGNORECASE)
                if match:
                    positive = float(match.group(1))
            elif line.startswith('Neutral:'):
                match = re.search(r'Neutral:\s*(\d+\.?\d*)%?', line, re.IGNORECASE)
                if match:
                    neutral = float(match.group(1))
            elif line.startswith('Negative:'):
                match = re.search(r'Negative:\s*(\d+\.?\d*)%?', line, re.IGNORECASE)
                if match:
                    negative = float(match.group(1))

        # Validate and normalize sentiment scores
        if positive is not None and neutral is not None and negative is not None:
            total = positive + neutral + negative
            if total > 0:
                positive = (positive / total) * 100
                neutral = (neutral / total) * 100
                negative = (negative / total) * 100
                gemini_result['text_sentiment'] = {
                    'positive': round(positive, 2),
                    'neutral': round(neutral, 2),
                    'negative': round(negative, 2)
                }
            else:
                return {'error': 'Gemini returned invalid sentiment scores (sum is 0)'}
        else:
            return {'error': 'Gemini response format incorrect, expected "Positive: X%\nNeutral: Y%\nNegative: Z%"'}

        return gemini_result
    except Exception as e:
        logger.error(f"Gemini prediction error: {str(e)}")
        return {'error': f'Gemini prediction failed: {str(e)}'}

# Function to extract tweet ID from URL
def extract_tweet_id(tweet_url):
    match = re.search(r'status/(\d+)', tweet_url)
    if match:
        return match.group(1)
    return None

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    if not twitter_client:
        return jsonify({'error': 'Twitter API client not initialized'}), 503

    try:
        data = request.get_json()
        if not data or 'tweetUrl' not in data:
            return jsonify({'error': 'Missing tweetUrl in request'}), 400

        tweet_url = data['tweetUrl']
        if not tweet_url.strip():
            return jsonify({'error': 'Tweet URL cannot be empty'}), 400

        # Extract tweet ID from URL
        tweet_id = extract_tweet_id(tweet_url)
        if not tweet_id:
            return jsonify({'error': 'Invalid tweet URL format'}), 400

        # Fetch tweet using Twitter API v2
        try:
            tweet = twitter_client.get_tweet(tweet_id, tweet_fields=['text'])
            if not tweet.data:
                return jsonify({'error': 'Tweet not found or inaccessible'}), 404
            tweet_text = tweet.data.text
        except tweepy.errors.TooManyRequests:
            logger.warning("Rate limit exceeded, waiting to retry...")
            return jsonify({'error': 'Twitter API rate limit exceeded. Please try again later or use text input mode.'}), 429
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {str(e)}")
            return jsonify({'error': f'Twitter API error: {str(e)}'}), 500

        # Perform sentiment analysis on the fetched tweet text
        local_sentiment = predict_local_sentiment(tweet_text)
        gemini_result = predict_gemini_sentiment(tweet_text)

        # Calculate overall sentiment for Local model
        local_overall_sentiment = None
        if local_sentiment:
            sentiments = {
                'Positive': local_sentiment['positive'],
                'Neutral': local_sentiment['neutral'],
                'Negative': local_sentiment['negative']
            }
            local_overall_sentiment = max(sentiments, key=sentiments.get)

        # Calculate overall sentiment for Gemini model
        gemini_overall_sentiment = None
        if gemini_result.get('text_sentiment'):
            sentiments = {
                'Positive': gemini_result['text_sentiment']['positive'],
                'Neutral': gemini_result['text_sentiment']['neutral'],
                'Negative': gemini_result['text_sentiment']['negative']
            }
            gemini_overall_sentiment = max(sentiments, key=sentiments.get)

        return jsonify({
            'text': tweet_text,
            'local_sentiment': local_sentiment,
            'gemini_sentiment': gemini_result,
            'local_overall_sentiment': local_overall_sentiment,
            'gemini_overall_sentiment': gemini_overall_sentiment
        })

    except Exception as e:
        logger.error(f"Unexpected error in /analyze: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/analyze-text', methods=['POST'])
def analyze_text_sentiment():
    try:
        data = request.get_json()
        if not data or 'tweetText' not in data:
            return jsonify({'error': 'Missing tweetText in request'}), 400

        text = data['tweetText']
        if not text.strip():
            return jsonify({'error': 'Tweet text cannot be empty'}), 400

        local_sentiment = predict_local_sentiment(text)
        gemini_result = predict_gemini_sentiment(text)

        # Calculate overall sentiment for Local model
        local_overall_sentiment = None
        if local_sentiment:
            sentiments = {
                'Positive': local_sentiment['positive'],
                'Neutral': local_sentiment['neutral'],
                'Negative': local_sentiment['negative']
            }
            local_overall_sentiment = max(sentiments, key=sentiments.get)

        # Calculate overall sentiment for Gemini model
        gemini_overall_sentiment = None
        if gemini_result.get('text_sentiment'):
            sentiments = {
                'Positive': gemini_result['text_sentiment']['positive'],
                'Neutral': gemini_result['text_sentiment']['neutral'],
                'Negative': gemini_result['text_sentiment']['negative']
            }
            gemini_overall_sentiment = max(sentiments, key=sentiments.get)

        return jsonify({
            'text': text,
            'local_sentiment': local_sentiment,
            'gemini_sentiment': gemini_result,
            'local_overall_sentiment': local_overall_sentiment,
            'gemini_overall_sentiment': gemini_overall_sentiment
        })
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
