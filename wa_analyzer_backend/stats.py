from sklearn.cluster import KMeans
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
from textblob import TextBlob

import seaborn as sns
import emoji
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

extract = URLExtract()

nltk.download('stopwords')
stop_words_id = stopwords.words('indonesian')

def fetch_stats(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]
        
    num_messages = df.shape[0]
    words = []
    for msg in df['Message']:
        words.append(len(msg.split()))
        
    # for now only indonesian language
    media_sent = df[df['Message'] == '<Media tidak disertakan>']
    
    links = []
    for msg in df['Message']:
        links.append(extract.find_urls(msg))
    
    return num_messages, len(words), media_sent.shape[0], len(links)

def fetch_busy_user(selected_user, df):
    
    df = df[df['User'] != 'group_notification']
    count = df['User'].value_counts().head()
    
    newdf = pd.DataFrame((df['User'].value_counts()/df.shape[0])*100)
    return count, newdf

def create_word_cloud(selected_user, df):
    
    if selected_user !=  'Overall':
        df = df[df['User'] == selected_user]
        
    df = df[df['User'] != 'group_notification']
    df = df[df['Message'] != '<Media tidak disertakan>']
        
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    
    df_wc = wc.generate(df['Message'].str.cat(sep = " "))
    
    return df_wc
        
def get_top_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]

    df = df[~df['Message'].str.fullmatch(r"<.*?tidak disertakan>")]

    words = []

    for message in df['Message']:
        words.extend(message.lower().split())

    stopwords = {}
    filtered_words = [word for word in words if word not in stopwords]

    common_words = Counter(filtered_words).most_common(20)
    return common_words

def get_emoji_stats(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]
        
    emojis = []
    
    for msg in df['Message']:
        emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])
        
    emoji_df = pd.DataFrame(Counter(emojis).most_common(20))
    
    return emoji_df

def month_timeline(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]
    
    temp = df.groupby(['Year', 'Month_num', 'Month']).count()['Message'].reset_index()
    
    time = []
    for i in range(temp.shape[0]):
        time.append(temp['Month'][i]+' - '+str(temp['Year'][i]))
    temp['time'] = time
    return temp

def month_activity_map(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['User']== selected_user]
    
    return df['Month'].value_counts()

def week_activity_map(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['User']== selected_user]
    
    return df['Day_name'].value_counts()

from textblob import TextBlob

def sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]
    
    sentiments = []
    for msg in df['Message']:
        sentiment = TextBlob(msg).sentiment.polarity
        sentiments.append(sentiment)
    
    avg_sentiment = sum(sentiments) / len(sentiments) if len(sentiments) > 0 else 0
    return avg_sentiment

def interpret_sentiment(sentiment_score):
    if sentiment_score > 0:
        return "Positif"
    elif sentiment_score < 0:
        return "Negatif"
    else:
        return "Netral"

def message_length_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]
    
    df['message_length'] = df['Message'].apply(lambda x: len(x))
    df['word_count'] = df['Message'].apply(lambda x: len(x.split()))
    
    return df[['User', 'message_length', 'word_count']].describe()

def top_urls_shared(selected_user, df, n=5):
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]
    
    urls = []
    for msg in df['Message']:
        urls.extend(extract.find_urls(msg))
    
    common_urls = Counter(urls).most_common(n)
    return common_urls

def user_segmentation(df):
    df['message_count'] = df.groupby('User')['Message'].transform('count')
    df = df.drop_duplicates(subset=['User'])
    kmeans = KMeans(n_clusters=3, random_state=0)
    df['cluster'] = kmeans.fit_predict(df[['message_count']])
    return df[['User', 'message_count', 'cluster']]

def heatmap_activity(df):
    df['hour'] = pd.to_datetime(df['Date']).dt.hour
    df['day'] = pd.to_datetime(df['Date']).dt.dayofweek
    
    activity_matrix = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
    sns.heatmap(activity_matrix, cmap="YlGnBu", annot=True, fmt="d")
    
def user_activity_vs_hour(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]

    activity_time_hour = df.groupby('Hour').size()
    return activity_time_hour

def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

def topic_modeling(selected_user, df, num_topics=5, n_top_words=10):
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]
    
    df['Message'] = df['Message'].apply(clean_text)
    
    vectorizer = CountVectorizer(stop_words=stop_words_id)
    dtm = vectorizer.fit_transform(df['Message'])
    
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dtm)
    
    topics = []
    for i, topic in enumerate(lda.components_):
        topic_words = [vectorizer.get_feature_names_out()[index] for index in topic.argsort()[-n_top_words:]]
        topics.append(f"Topik {i + 1}: {', '.join(topic_words)}")
    
    return topics
