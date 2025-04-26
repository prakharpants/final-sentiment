import requests
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# API Key (yours)
API_KEY = '8105e9fae81e42c6b9e81060cc055273'

# Fetch live headlines
def fetch_news_history():
    try:
        url = ('https://newsapi.org/v2/top-headlines?'
               'category=business&'
               'language=en&'
               f'apiKey={API_KEY}')
        response = requests.get(url)
        data = response.json()

        # Check if articles exist
        if data['status'] == 'ok' and len(data['articles']) > 0:
            return data['articles']
        else:
            print("No articles fetched. Please check your API key or parameters.")
            return []
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# Ask user for how many headlines they want to show
def ask_for_history():
    try:
        history = int(input("How many headlines would you like to see? (Enter number): "))
        if history < 1:
            print("Please enter a number greater than 0.")
            return ask_for_history()
        return history
    except ValueError:
        print("Invalid input. Please enter a number.")
        return ask_for_history()

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Display News and Sentiment Analysis
def display_news_and_sentiments():
    # Fetch news data
    articles = fetch_news_history()
    if not articles:
        return

    # Ask user how many headlines to display
    history_count = ask_for_history()
    headlines = [article['title'] for article in articles[:history_count]]

    # Check if we actually have headlines to display
    if not headlines:
        print("No headlines to display.")
        return

    # Print the headlines to the terminal
    print("\nFetched Headlines:\n")
    for idx, headline in enumerate(headlines, start=1):
        print(f"{idx}. {headline}")
    
    print("\nProcessing Sentiments...\n")

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

    # Print trading signals
    print("\nTrading Signals based on Live News:\n")
    for idx, (headline, signal) in enumerate(zip(headlines, signals), start=1):
        print(f"• {headline}")
        print(f"  Sentiment Score: {sentiment_scores[idx - 1]:.3f}")
        print(f"  Generated Signal: {signal}")
        print('-' * 80)

    # Plotting
    x = range(len(headlines))
    colors = {'Buy': 'green', 'Sell': 'red', 'Hold': 'blue'}

    plt.figure(figsize=(12, 6))
    for i in x:
        plt.scatter(i, sentiment_scores[i], color=colors[signals[i]])

    plt.title('Sentiment Analysis Trading Signals (Live News)')
    plt.xlabel('Headline Index')
    plt.ylabel('Sentiment Score')
    plt.show()

# Run the function
display_news_and_sentiments()
