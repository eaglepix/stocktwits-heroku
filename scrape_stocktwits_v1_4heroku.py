""" This is local version converting to cloud version
    Add pickle serialization and also bz2 compression
    Added few versions of uploads & downloads to/from GDrive based on formats
    Converting processes to functions
    GDrive access options:
    1) Upload to GDrive via creating new file in .pbz2 format
    2) Updating GDrive's existing .pbz2 file
    3) Download .csv file from GDrive to process
    4) Download .pbz2 file from GDrive to process

    Omitted local version of upload/download
    10 Jun 2021: This version is to be deployed on Heroku
    11 Jun 2021: Add json loads GOOGLE_APPLICATION_CREDENTIALS
                -   seems to be working on Heroku
                -   Already downloading pickle-pandas format (pbz2),
                    no need parsing Dtype
    21 Jul 2021: Debug and Upgrade Main_Process
                -   Return for Main_Process: short-term popularity df,
                    specified period (1 day) popularity df/ popularMidTerm
"""
import requests
from bs4 import BeautifulSoup
import time
import datetime as dt
from datetime import datetime
import pandas as pd
import re
import csv
import pickle
import bz2
# import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from apiclient import errors

import io
import os
# import mimetypes
from requests.models import HTTPError

local_gc_path = '../../googleDrive/client_secrets.json'

Gfolder_id = '1l8_5w9WLpgAxw3ANmPcdapgA4stIIrgW'  # Stocktwits
# newer version of stockTwits
download_csv_FileId = '1lxwOtMK1XwgU9IQVqJQ8j__kdqBxLWbg'
uploadFileName = 'stockTwits_trending.pbz2'
download_pbz2Id = '1NPpfVMEvLl9QpcK-jAcqIRgl0TejpzGN'
stocktwits_html_Id = '1DM_Pr7KKOt-RaogDo0FaqK8IWrk5hnye'

"""Getting Google Drive Credential and get the service module running"""
SCOPES = [
    'https://www.googleapis.com/auth/drive']  # full access here if used without .file

global SERVICE_ACCOUNT_FILE
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
API_NAME = 'drive'
API_VERSION = 'v3'
ctr = 1

if SERVICE_ACCOUNT_FILE == None:
    print('SERVICE_ACCOUNT_FILE is NONE, look into local...', ctr)
    ctr += 1
    try:
        SERVICE_ACCOUNT_FILE = local_gc_path
    except:
        print('Error in retrieving Google Authentication file')
        os.abort()

# # project name
gcp_project = os.environ.get('GCP_PROJECT')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)


#####################################################################
def upload_createFiles(fileInMemory, Gfolder_id, file_name, mime_type):
    """Uploading to GDrive via 'create' command - processed data in memory
        Important: For 'create' MUST include 'parents' in file_metadata, else it won't save correctly"""
    try:
        file_metadata = {
            'name': file_name,
            'parents': [Gfolder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(
            fileInMemory), mimetype=mime_type, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return print(f'Done! Successfully uploaded to Google Drive: {Gfolder_id}/{file_name}, File ID: {file["id"]}')
    except errors.HttpError as error:
        print('error in uploading to Google Drive')
        print(error)
        return None


def existingFile_update(fileInMemory, Gfolder_id, file_name, mime_type, file_id):
    """Uploading to GDrive via 'update' command - processed data in memory
        - Just updating the existing pbz2 file
        - omit updating file_metadata[body] (difficult to modify), just updating contents[media_body]"""
    try:
        # file_metadata = {
        #     'name' : file_name,
        #     'parents' : [Gfolder_id]
        # }
        media = MediaIoBaseUpload(io.BytesIO(
            fileInMemory), mimetype=mime_type, resumable=True)
        service.files().update(
            # body=file_metadata,
            fileId=file_id,
            media_body=media,
            # fields='id'
        ).execute()
        return print('Done! Successfully uploaded to Google Drive:', Gfolder_id+'/'+file_name)
    except errors.HttpError as error:
        print('error in uploading to Google Drive')
        print(error)
        return None


def download_csv_Files(file_id):
    """Downloading .csv Files"""
    request = service.files().get_media(fileId=file_id)
    stream = io.BytesIO()
    downloader = MediaIoBaseDownload(stream, request)
    done = False
    # Retry if we received HttpError
    for retry in range(0, 5):
        try:
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))

            decoded_content = stream.getvalue().decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            df = pd.DataFrame(my_list, columns=my_list[0]).drop(index=0)
            return df

        except HTTPError as error:
            print('There was an API error: {}. Try # {} failed.'.format(
                error.response, retry))


def download_pbz2_Files(file_id):
    request = service.files().get_media(fileId=file_id)
    stream = io.BytesIO()
    downloader = MediaIoBaseDownload(stream, request)
    done = False
    # Retry if we received HttpError
    for retry in range(0, 5):
        try:
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))

            # bz2 decompression
            decompressed = bz2.decompress(stream.getvalue())

            pkl_file = pickle.loads(decompressed)
            df = pd.DataFrame(pkl_file)
            return df

        except HTTPError as error:
            print('There was an API error: {}. Try # {} failed.'.format(
                error.response, retry))

# def downloadFiles(file_id, credentials):
#     access_token = credentials.token
#     url = "https://www.googleapis.com/drive/v3/files/" + file_id + "?alt=media"
#     res = requests.get(url, headers={"Authorization": "Bearer " + access_token})

#     decoded_content = res.content.decode('utf-8')
#     cr = csv.reader(decoded_content.splitlines(), delimiter=',')
#     my_list = list(cr)
#     df = pd.DataFrame(my_list, columns=my_list[0]).drop(index=0)
#     return df

#####################################################################


def timeString_conversion(x):
    if type(x) is pd.Timestamp:
        return x
    else:
        try:
            return datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                return datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')
            except:
                print('Unable to parse date:', x)
                return x


def convert2Numeral(x):
    regex = "[-+]?\d+[.]?\d+|[0-9]"  # any kind of decimal, |or 0-9
    try:
        return float(re.findall(regex, str(x))[0])
    except:
        return None
#####################################################################


def initial_df_clean(df_toClean):
    # Converting relevant fields to datetime or numerals
    if df_toClean['created_at'].dtype == 'datetime64[ns]':
        pass
    else:
        df_toClean['created_at'] = df_toClean['created_at'].apply(
            lambda x: timeString_conversion(x))
    for i in ['sentimentChange', 'trendingScore', 'volumeChange']:
        if df_toClean[i].dtype == 'float64':
            pass
        else:
            df_toClean[i] = df_toClean[i].apply(lambda x: convert2Numeral(x))
    return df_toClean

#############################################################################################


def stocktwits_trending_download():
    # Getting 30 messages from Trending list
    stocktwits_trending = requests.get(
        'https://api.stocktwits.com/api/2/streams/trending.json').json()

    # Getting details in the 30 messages captured:
    stkList = []
    df_stkDetails = pd.DataFrame(columns=['ticker', 'title', 'body', 'sentiment', 'created_at',
                                 'watchlist_count', 'user_id', 'username', 'userFollowers', 'userIdeas'])
    for i in enumerate(stocktwits_trending['messages']):
        symbol = i[1]['symbols'][0]['symbol']
        df_stkDetails = df_stkDetails.append({'ticker': symbol,
                                              'title': i[1]['symbols'][0]['title'],
                                              'user_id': i[1]['user']['id'],
                                              'username': i[1]['user']['username'],
                                              'userFollowers': i[1]['user']['followers'],
                                              'userIdeas': i[1]['user']['ideas'],
                                              'watchlist_count': i[1]['symbols'][0]['watchlist_count'],
                                              'sentiment': i[1]['entities']['sentiment'],
                                              'body': i[1]['body'],
                                              'created_at': i[1]['created_at']
                                              }, ignore_index=True)

        stkList.append(symbol)

    popularity = {j: stkList.count(j) for j in stkList}
    print('Popularity current 30:', dict(
        sorted(popularity.items(), key=lambda item: item[1], reverse=True)))
    df_stkDetails.sort_values(
        by=['created_at', 'ticker'], ascending=False, inplace=True)
    return df_stkDetails, popularity

################# Getting Trending API ##############################


def cleanUp(col, x):
    # Cleaning up downloaded Sentiments DF
    purgeLabels = ['sentimentChange":', 'trending":',
                   'trendingScore":', 'volumeChange":']
    try:
        if col == 'sentimentChange':
            return1 = x.strip(purgeLabels[0])
        elif col == 'trendingScore':
            return1 = x.strip(purgeLabels[2])
        elif col == 'volumeChange':
            return1 = x.strip(purgeLabels[3])
        elif col == 'trending':
            if 'true' in x:
                return True
            else:
                return False
    except:
        return None

    try:
        return convert2Numeral(return1)
        # pd.to_numeric(return1.strip(','))
    except:
        return return1


def getTrendingStocksSentiment(popularity):
    trending_sentiment = {}
    # popularity.keys() are the disctinct tickers over 5 min period
    ctr = 1
    for index in popularity.keys():
        try:
            x = requests.get(
                'https://www.stocktwits.com/symbol/{}'.format(index))
            soup = BeautifulSoup(x.text, 'html.parser')
            texts = soup.findAll(text=True)
            Real_time = texts.index('Real-Time')
            Sentiment_index = texts[Real_time+1].index('sentimentChange')
            trending = texts[Real_time+1].index('trending')
            trendingScore = texts[Real_time+1].index('trendingScore')
            volumeChange = texts[Real_time+1].index('volumeChange')

            trending_sentiment['%s' % index] = [texts[Real_time+1][Sentiment_index:Sentiment_index+22],
                                                texts[Real_time +
                                                      1][trending:trending+14],
                                                texts[Real_time +
                                                      1][trendingScore:trendingScore+22],
                                                texts[Real_time +
                                                      1][volumeChange:volumeChange+19],
                                                ]
        except:
            pass
        if ctr < len(popularity):
            time.sleep(0.5)
            ctr += 1

    # clean up
    df_trending_sentiment = pd.DataFrame.from_dict(trending_sentiment, orient='index', columns=[
                                                   'sentimentChange', 'trending', 'trendingScore', 'volumeChange'])
    df_trending_sentiment['sentimentChange'] = df_trending_sentiment['sentimentChange'].apply(
        lambda x: cleanUp('sentimentChange', x))
    df_trending_sentiment['trending'] = df_trending_sentiment['trending'].apply(
        lambda x: cleanUp('trending', x))
    df_trending_sentiment['trendingScore'] = df_trending_sentiment['trendingScore'].apply(
        lambda x: cleanUp('trendingScore', x))
    df_trending_sentiment['volumeChange'] = df_trending_sentiment['volumeChange'].apply(
        lambda x: cleanUp('volumeChange', x))
    return df_trending_sentiment


def mergingAPI_df(df_stkDetails, df_trending_sentiment):
    # Mapping
    df_stkDetails['sentimentChange'] = df_stkDetails['ticker'].map(
        df_trending_sentiment['sentimentChange'])
    df_stkDetails['trending'] = df_stkDetails['ticker'].map(
        df_trending_sentiment['trending'])
    df_stkDetails['trendingScore'] = df_stkDetails['ticker'].map(
        df_trending_sentiment['trendingScore'])
    df_stkDetails['volumeChange'] = df_stkDetails['ticker'].map(
        df_trending_sentiment['volumeChange'])
    # convert to numeric
    for i in ['watchlist_count', 'user_id', 'userFollowers', 'userIdeas']:
        df_stkDetails[i] = df_stkDetails[i].astype('int64')
    # convert created_at date:time
    df_stkDetails['created_at'] = df_stkDetails['created_at'].apply(
        lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
    df_stkDetails.sort_values(by='created_at', ascending=False, inplace=True)
    return df_stkDetails


def popular_Xdays(mergeDB, popularPeriod):
    """Compiling Popularity over x days"""
    print(f'Compiling popularity over past {popularPeriod} days')
    from_period = datetime.now() - dt.timedelta(popularPeriod)
    mergeDB.reset_index(drop=True, inplace=True)
    carvedOutDB = mergeDB.loc[mergeDB['created_at'] > from_period]
    popularMidTerm = carvedOutDB[['ticker', 'title']].groupby(
        'ticker').count().sort_values(by='title').tail(20)
    popular_dict = carvedOutDB[['ticker', 'created_at', 'sentimentChange', 'trending',
                                'trendingScore', 'volumeChange']].groupby('ticker').last().to_dict('series')
    for colNames in ['sentimentChange', 'trending', 'trendingScore', 'volumeChange']:
        popularMidTerm[colNames] = popularMidTerm.index.map(
            popular_dict[colNames])
    print('popularMidTerm:\n', popularMidTerm)
    return popularMidTerm


def mergePopular_update(df_trending_sentiment, popularMidTerm, popularPeriod, html_fileName, file_id):
    # File already initialised - ongoing just update it
    """ Merging Both popular dataframes to html and save"""

    html_save = ("<h1>Short Term Popularity</h1>" +
                 df_trending_sentiment.to_html() +
                 "<br><hr><br><h1>Medium Term Popularity (" +
                 str(popularPeriod) + "days)</h1>" + popularMidTerm.to_html())
    
    # Convert from strings to StringIO then to BytesIO
    sio = io.StringIO(html_save)
    b = bytes(sio.read(), encoding='utf-8')
    bio = io.BytesIO(b)

    # file_metadata = {'name': html_fileName, 'parents': [Gfolder_id] }  #No need for update
    try:
        media = MediaIoBaseUpload(bio, mimetype='text/html', resumable=True)
        service.files().update(
            # body=file_metadata,
            fileId=file_id,
            media_body=media,
            # fields='id'
        ).execute()
        return print('Done! Successfully uploaded to Google Drive:', Gfolder_id+'/'+html_fileName)
    except errors.HttpError as error:
        print('error in uploading to Google Drive')
        print(error)
        return None

####################################################################################


def main_process():
    print('Downloading GDrive stockTwits_trending.pbz2')
    """ 2 options below to select """
    df_trendingDB = download_pbz2_Files(download_pbz2Id)
    # df_trendingDB = download_csv_Files(download_csv_FileId)

    print('Initial cleaning of DF')
    df_trendingDB = initial_df_clean(df_trendingDB)

    print('Download Stocktwits top 30 trending...')
    df_stkDetails, popularity = stocktwits_trending_download()
    print('Download Stocktwits 30 individual data...')
    df_trending_sentiment = getTrendingStocksSentiment(popularity)
    print('Merging dataframes')
    df_stkDetails = mergingAPI_df(df_stkDetails, df_trending_sentiment)

    # Merging DB
    mergeDB = pd.concat([df_trendingDB, df_stkDetails])
    print(mergeDB.tail(5))

    """ Uploading bz2 compressed pickle file """
    print('Compress and upload to GDrive')
    # print('Ends here, not compressed and not uploaded')
    bz2_pickleObj = bz2.compress(pickle.dumps(mergeDB))
    # mime_types = [mimetypes.guess_type(file_names[i])[0] for i in range(len(file_names))]   # check up MIME type

    """ 2 options below to select """
    # upload_createFiles(bz2_pickleObj, Gfolder_id, uploadFileName, '*/pbz2')
    existingFile_update(bz2_pickleObj, Gfolder_id,
                        uploadFileName, '*/pbz2', download_pbz2Id)

    """ Compiling Popularity over x days & Upload result to G-Drive """
    popularPeriod = 1  # in previous no. of days
    popularMidTerm = popular_Xdays(mergeDB, popularPeriod)
    mergePopular_update(df_trending_sentiment, popularMidTerm, popularPeriod,
                        'Stocktwits_Popular.html', stocktwits_html_Id)

    return df_trending_sentiment, popularMidTerm, popularPeriod


if __name__ == '__main__':
    main_process()
    print('Process successfully completed!')
