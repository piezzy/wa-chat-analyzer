import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
import wa_analyzer_backend.preprocess as preprocess
import re
import wa_analyzer_backend.stats as stats
import matplotlib.pyplot as plt
import numpy as np


st.sidebar.title("Whatsapp Chat Analyzer")


uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()


    data = bytes_data.decode("utf-8")


    df = preprocess.preprocess(data)

    user_list = df['User'].unique().tolist()


    if 'Group Notification' in user_list:
        user_list.remove('Group Notification')

    user_list.sort()

    user_list.insert(0, "Overall")
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox(
        "Show analysis with respect to", user_list)

    st.title("Whats App Chat Analysis for " + selected_user)
    if st.sidebar.button("Show Analysis"):

        num_messages, num_words, media_omitted, links = stats.fetch_stats(
            selected_user, df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total No.of Words")
            st.title(num_words)

        with col3:
            st.header("Media Shared")
            st.title(media_omitted)

        with col4:
            st.header("Total Links Shared")
            st.title(links)


        if selected_user == 'Overall':

            st.title('Most Busy Users')
            busycount, newdf = stats.fetch_busy_user(selected_user, df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(busycount.index, busycount.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(newdf)


        st.title('Word Cloud')
        df_img = stats.create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_img)
        st.pyplot(fig)


        top_words = stats.get_top_words(selected_user, df)
        top_words_df = pd.DataFrame(top_words, columns=['word', 'count'])

        fig, ax = plt.subplots()
        ax.barh(top_words_df['word'].astype(str), top_words_df['count'])
        plt.xticks(rotation='vertical')
        st.title('Most commmon words')
        st.pyplot(fig)


        emoji_df = stats.get_emoji_stats(selected_user, df)
        emoji_df.columns = ['Emoji', 'Count']

        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            emojicount = list(emoji_df['Count'])
            perlist = [(i/sum(emojicount))*100 for i in emojicount]
            emoji_df['Percentage use'] = np.array(perlist)
            st.dataframe(emoji_df)


        st.title("Monthly Timeline")
        time = stats.month_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(time['time'], time['Message'], color='green')
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        st.pyplot(fig)


        st.title("Activity Maps")

        col1, col2 = st.columns(2)

        with col1:

            st.header("Most Busy Day")

            busy_day = stats.week_activity_map(selected_user, df)

            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            plt.tight_layout()
            st.pyplot(fig)

        with col2:

            st.header("Most Busy Month")
            busy_month = stats.month_activity_map(selected_user, df)

            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            plt.tight_layout()
            st.pyplot(fig)
