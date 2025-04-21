import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
from PIL import Image
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
from textblob import TextBlob
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import emoji
import nltk
import re

import wa_analyzer_backend.preprocess as preprocess
import wa_analyzer_backend.stats as stats

nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words_id = stopwords.words('indonesian')

extract = URLExtract()

st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")
st.title("📊 WhatsApp Chat Analyzer")

# ========================
# Custom Styling
# ========================
st.markdown("""
<style>
    .main {
        background-color: #f9f9f9;
        color: #2c3e50;
    }
    .sidebar .sidebar-content {
        background-color: #ecf0f1;
    }
    .stTable {
        background-color: #ffffff;
    }
    h1, h2, h3, h4 {
        color: #2c3e50;
    }
    .metric-card {
        padding: 1rem;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# Upload Section
# ========================
uploaded_file = st.sidebar.file_uploader("📂 Upload Chat File (.txt)", type=["txt"])
if uploaded_file is not None:
    bytes_data = uploaded_file.read()
    data = bytes_data.decode("utf-8")
    df = preprocess.preprocess(data)

    user_list = df['User'].unique().tolist()
    user_list = [user for user in user_list if user != "Group Notification"]
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Analyze for", user_list)

    if st.sidebar.button("🚀 Show Analysis"):
        num_messages, total_words, num_media, num_links = stats.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("#### 💬 Messages")
            st.metric(label="Total", value=num_messages)

        with col2:
            st.markdown("#### 📝 Words")
            st.metric(label="Total", value=total_words)

        with col3:
            st.markdown("#### 🖼️ Media")
            st.metric(label="Shared", value=num_media)

        with col4:
            st.markdown("#### 🔗 Links")
            st.metric(label="Shared", value=num_links)

        if selected_user == 'Overall':
            st.subheader('👥 Most Busy Users')
            busycount, newdf = stats.fetch_busy_user(selected_user, df)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(busycount, x=busycount.index, y=busycount.values, color=busycount.index,
                                title="Top Contributors", labels={'y': 'Messages'})
                st.plotly_chart(fig)
            with col2:
                st.dataframe(newdf)
            
        # Monthly Timeline
        st.subheader("⏳ Monthly Activity")
        timeline = stats.month_timeline(selected_user, df)
        fig = px.line(timeline, x='time', y='Message', title='Messages Over Time')
        st.plotly_chart(fig)

        # Word Cloud
        st.subheader("☁️ Word Cloud")
        df_wc = stats.create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # Top Words
        st.subheader("🔤 Most Common Words")
        common_words = stats.get_top_words(selected_user, df)
        common_df = pd.DataFrame(common_words, columns=['Word', 'Frequency'])
        fig = px.bar(common_df.sort_values(by='Frequency'), x='Frequency', y='Word', orientation='h')
        st.plotly_chart(fig)

        # Emoji Stats
        st.subheader("😊 Emoji Usage")
        emoji_df = stats.get_emoji_stats(selected_user, df)
        if not emoji_df.empty:
            emoji_df.columns = ['Emoji', 'Count']
            emoji_df['% Usage'] = (emoji_df['Count'] / emoji_df['Count'].sum() * 100).round(2)

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df.head(10))
            with col2:
                fig = px.pie(emoji_df.head(10), values='Count', names='Emoji', title='Top 10 Emoji')
                st.plotly_chart(fig)

        # Activity Map
        st.subheader("🗓️ Daily and Monthly Activity")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Active Days**")
            busy_day = stats.week_activity_map(selected_user, df)
            st.bar_chart(busy_day)

        with col2:
            st.markdown("**Active Months**")
            busy_month = stats.month_activity_map(selected_user, df)
            st.bar_chart(busy_month)

        # Sentiment Analysis
        st.subheader("🧠 Sentiment Analysis")
        sentiment_score = stats.sentiment_analysis(selected_user, df)
        sentiment_label = stats.interpret_sentiment(sentiment_score)
        st.metric("Average Sentiment", f"{sentiment_score:.2f}", sentiment_label)

        # Message Length Analysis
        st.subheader("📝 Message Length Summary")
        st.dataframe(stats.message_length_analysis(selected_user, df))

        # Top URLs
        st.subheader("🔗 Top URLs")
        top_urls = stats.top_urls_shared(selected_user, df)
        st.dataframe(pd.DataFrame(top_urls, columns=['URL', 'Count']))

        # User Segmentation
        if selected_user == "Overall":
            st.subheader("👥 User Segmentation (KMeans)")
            segmented_df = stats.user_segmentation(df)
            st.dataframe(segmented_df)

        # Heatmap Activity
        st.subheader("📊 User Activity Heatmap")
        fig, ax = plt.subplots(figsize=(12, 6))
        stats.heatmap_activity(df)
        st.pyplot(fig)

        # Topic Modeling
        st.subheader("🧩 Topic Modeling (LDA)")
        topics = stats.topic_modeling(selected_user, df)
        for t in topics:
            st.write(t)
