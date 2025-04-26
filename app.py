import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import pytz
from pytz import timezone as pytz_timezone
import plotly.graph_objects as go
import os

# API Key (your personal key)
API_KEY = '8105e9fae81e42c6b9e81060cc055273'  # Replace with your actual API key

# Categories for filtering (we'll use a fixed set of categories for simplicity)
categories = ['business', 'technology', 'sports', 'entertainment', 'health', 'science', 'all']

# Fetch live headlines from News API
def fetch_news(category='business'):
    if category == 'all':
        url = f'https://newsapi.org/v2/top-headlines?language=en&apiKey={API_KEY}'
    else:
        url = f'https://newsapi.org/v2/top-headlines?category={category}&language=en&apiKey={API_KEY}'
    
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'ok' and len(data['articles']) > 0:
        articles = data['articles']
        headlines = [article['title'] for article in articles]
        urls = [article['url'] for article in articles]
        timestamps = [article['publishedAt'] for article in articles]
    else:
        articles = []
        headlines = []
        timestamps = []
    return headlines, urls, timestamps

# Streamlit App Layout
st.set_page_config(page_title="Sentiment Analysis Trading Signals", layout="wide")
st.title("Live News Sentiment Analysis for Trading")

# Dark Theme + Clean UI
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: #FFFFFF;
        font-family: Arial, sans-serif;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-size: 18px;
    }
    .stTextInput>label {
        color: #FFFFFF;
    }
    .stSelectbox>label {
        color: #FFFFFF;
    }
    .stSelectbox>div {
        background-color: #333333;
    }

    .news-item {
        margin-bottom: 20px;
        padding: 15px;
        border-radius: 5px;
    }

    .news-divider {
        border-bottom: 1px solid #444;
        margin: 15px 0;
    }

    .article-details {
        margin-bottom: 10px;
    }

    .signal-buy {
        color: #2ecc71; /* Green */
    }

    .signal-sell {
        color: #e74c3c; /* Red */
    }

    .signal-hold {
        color: #3498db; /* Blue */
    }

    .stApp {
        padding-left: 5%;
        padding-right: 5%;
    }

    .news-container {
        width: 80%;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Timezone selection for user
user_timezone = st.selectbox("Select Your Timezone", pytz.all_timezones)
tz = pytz_timezone(user_timezone)

# Category selection for news filter, including "All News"
category = st.selectbox("Select News Category", categories)

# Fetch the selected category's news
headlines, urls, timestamps = fetch_news(category)

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Analyze sentiments
sentiment_scores = []
for headline in headlines:
    sentiment = analyzer.polarity_scores(headline)
    sentiment_scores.append(sentiment['compound'])

# Generate Trading Signals
signals = []
for score in sentiment_scores:
    if score > 0.2:
        signals.append('Buy')
    elif score < -0.2:
        signals.append('Sell')
    else:
        signals.append('Hold')

# Display the news with dividers
st.markdown('<div class="news-container">', unsafe_allow_html=True)
for i, headline in enumerate(headlines):
    timestamp = timestamps[i]
    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    timestamp = timestamp.replace(tzinfo=pytz.utc).astimezone(tz)

    st.markdown(f'<div class="news-item">', unsafe_allow_html=True)
    st.subheader(headline)
    st.markdown(f'<p class="article-details"><strong>Published At:</strong> {timestamp.strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)
    signal_class = f"signal-{signals[i].lower()}"
    st.markdown(f'<p class="article-details"><strong>Signal:</strong> <span class="{signal_class}">{signals[i]}</span></p>', unsafe_allow_html=True)
    st.markdown(f'<p class="article-details"><strong>Sentiment Score:</strong> {sentiment_scores[i]:.2f}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="article-details"><a href="{urls[i]}" target="_blank" style="color: #3498db;">Read Full Article</a></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if i < len(headlines) - 1:
        st.markdown('<div class="news-divider"></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Interactive Sentiment Visualization with Plotly
if headlines:
    x = range(len(headlines))
    colors = {'Buy': 'green', 'Sell': 'red', 'Hold': 'blue'}

    fig = go.Figure()

    for i in x:
        fig.add_trace(go.Scatter(
            x=[i],
            y=[sentiment_scores[i]],
            mode='markers',
            marker=dict(color=colors[signals[i]], size=12),
            text=f"{headlines[i]}<br>Sentiment: {sentiment_scores[i]:.2f}<br>Signal: {signals[i]}",
            hoverinfo='text'
        ))

    fig.update_layout(
        title='Sentiment Analysis Trading Signals (Live News)',
        xaxis_title='Headline Index',
        yaxis_title='Sentiment Score',
        template='plotly_dark',
        hovermode='closest',
        showlegend=False
    )

    st.plotly_chart(fig)
else:
    st.info("No news headlines available.")
