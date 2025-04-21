import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import datetime as dt


def gettimeanddate(string):
    parts = string.split()
    date = parts[0]
    time = parts[1]
    return date + ' ' + time

def getstring(text):
    return text.split('\n')[0]

def preprocess(data):
    
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4} \d{1,2}\.\d{2})'
    split_data = re.split(pattern, data)[1:]
    messages = [msg.strip() for msg in split_data[1::2]]
    dates = re.findall(pattern, data)

    
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    df['message_date'] = df['message_date'].apply(lambda text: gettimeanddate(text))
    df.rename(columns={'message_date': 'date'}, inplace=True)
    
    users = []
    messages = []

    for msg in df['user_message']:
        
        entry = re.split(r'([\w\W]+?): ', msg, maxsplit=1)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages

    def getstring(text):
        return text.split('\n')[0]

    df['message'] = df['message'].apply(lambda text:getstring(text))

    df = df.drop(columns=['user_message'], axis=1)
    df = df[['date', 'user', 'message']]

    df = df.rename(columns={'date':'Date', 'user':'User', 'message':'Message'}) 

    df['User'] = df['User'].str.lstrip('- ')

    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y %H.%M')

    df['Only Date'] = pd.to_datetime(df['Date']).dt.date
    df['Year'] = pd.to_datetime(df['Date']).dt.year
    df['Month_num'] = pd.to_datetime(df['Date']).dt.month
    df['Month'] = pd.to_datetime(df['Date']).dt.month_name()
    df['Day'] = pd.to_datetime(df['Date']).dt.day
    df['Day_name'] = pd.to_datetime(df['Date']).dt.day_name()
    df['Hour'] = pd.to_datetime(df['Date']).dt.hour
    df['Minute'] = pd.to_datetime(df['Date']).dt.minute
    
    return df