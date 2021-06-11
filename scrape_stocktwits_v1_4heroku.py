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
"""
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pandas as pd
import re
import csv
import pickle, bz2
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from apiclient import errors

# MediaFileUpload
import io, os
# import mimetypes

from requests.models import HTTPError

Gfolder_id = '1l8_5w9WLpgAxw3ANmPcdapgA4stIIrgW'  # Stocktwits
download_csv_FileId = '1lxwOtMK1XwgU9IQVqJQ8j__kdqBxLWbg' # newer version of stockTwits
uploadFileName = 'stockTwits_trending.pbz2'
download_pbz2Id = '1NPpfVMEvLl9QpcK-jAcqIRgl0TejpzGN'

"""Getting Google Drive Credential and get the service module running"""
SCOPES = ['https://www.googleapis.com/auth/drive.file']

herokuEnvVar = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
API_NAME = 'drive'
API_VERSION = 'v3'

with open(herokuEnvVar) as f:
    SERVICE_ACCOUNT_FILE = json.load(f)

# project name
gcp_project = os.environ.get('GCP_PROJECT') 

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

#####################################################################
def upload_createFiles(fileInMemory, Gfolder_id, file_name, mime_type):
    """Uploading to GDrive via 'create' command - processed data in memory"""
    try:
        file_metadata = {
            'name' : file_name,
            'parents' : [Gfolder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(fileInMemory), mimetype=mime_type, resumable=True)
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return print('Done! Successfully uploaded to Google Drive:', Gfolder_id+'/'+file_name)
    except errors.HttpError as error :
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
        media = MediaIoBaseUpload(io.BytesIO(fileInMemory), mimetype=mime_type, resumable=True)
        service.files().update(
            # body=file_metadata,
            fileId=file_id,
            media_body=media,
            # fields='id'
        ).execute()
        return print('Done! Successfully uploaded to Google Drive:', Gfolder_id+'/'+file_name)
    except errors.HttpError as error :
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
                error.response, retry ))

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
                error.response, retry ))

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
    regex = "[-+]?\d+[.]?\d+|[0-9]"  #any kind of decimal, |or 0-9
    try:
        return float(re.findall(regex, str(x))[0])
    except:
        return None
#####################################################################
def initial_df_clean(df_toClean):
    # Converting relevant fields to datetime or numerals
    if df_toClean['created_at'].dtype=='datetime64[ns]':
        pass
    else:
        df_toClean['created_at'] = df_toClean['created_at'].apply(lambda x: timeString_conversion(x))
    for i in ['sentimentChange', 'trendingScore', 'volumeChange']:
        if df_toClean[i].dtype=='float64':
            pass
        else:
            df_toClean[i] = df_toClean[i].apply(lambda x: convert2Numeral(x) )
    return df_toClean

#############################################################################################
def stocktwits_trending_download():
    # Getting 30 messages from Trending list
    stocktwits_trending = requests.get('https://api.stocktwits.com/api/2/streams/trending.json').json()

    # Getting details in the 30 messages captured:
    stkList = []
    df_stkDetails = pd.DataFrame(columns=['ticker','title','body','sentiment','created_at','watchlist_count','user_id','username','userFollowers','userIdeas'])
    for i in enumerate(stocktwits_trending['messages']):
        symbol = i[1]['symbols'][0]['symbol']
        df_stkDetails = df_stkDetails.append({'ticker': symbol,
                                'title' : i[1]['symbols'][0]['title'],
                                'user_id' : i[1]['user']['id'],
                                'username' : i[1]['user']['username'],
                                'userFollowers' : i[1]['user']['followers'],
                                'userIdeas' : i[1]['user']['ideas'],
                                'watchlist_count': i[1]['symbols'][0]['watchlist_count'],
                                'sentiment': i[1]['entities']['sentiment'],
                                'body': i[1]['body'],
                                'created_at' : i[1]['created_at']
                                }, ignore_index=True)
            
        stkList.append(symbol)
        
    popularity = {j:stkList.count(j) for j in stkList}
    print('Popularity current 30:', dict(sorted(popularity.items(), key=lambda item: item[1], reverse=True)))
    df_stkDetails.sort_values(by=['created_at','ticker'], ascending=False, inplace=True)
    return df_stkDetails, popularity

################# Getting Trending API ##############################
def cleanUp(col, x):
    # Cleaning up downloaded Sentiments DF
    purgeLabels = ['sentimentChange":', 'trending":','trendingScore":','volumeChange":']
    try:
        if col == 'sentimentChange':
            return1 = x.strip(purgeLabels[0])
        elif col == 'trendingScore':
            return1 = x.strip(purgeLabels[2])
        elif col == 'volumeChange':
            return1 = x.strip(purgeLabels[3])
        elif col == 'trending':
            if 'true' in x:
                return  True
            else : return False
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
    for index in popularity.keys():
        try:
            time.sleep(1)
            x = requests.get('https://www.stocktwits.com/symbol/{}'.format(index))
            soup = BeautifulSoup(x.text, 'html.parser')
            texts = soup.findAll(text=True)
            Real_time=texts.index('Real-Time')
            Sentiment_index=texts[Real_time+1].index('sentimentChange')
            trending = texts[Real_time+1].index('trending')
            trendingScore = texts[Real_time+1].index('trendingScore')
            volumeChange = texts[Real_time+1].index('volumeChange')
            
            trending_sentiment['%s'%index]=[ texts[Real_time+1][Sentiment_index:Sentiment_index+22], 
                                            texts[Real_time+1][trending:trending+14],
                                            texts[Real_time+1][trendingScore:trendingScore+22],
                                            texts[Real_time+1][volumeChange:volumeChange+19],
                                        ]       
        except:
            pass

    ### clean up
    df_trending_sentiment = pd.DataFrame.from_dict(trending_sentiment, orient='index', columns=['sentimentChange', 'trending', 'trendingScore', 'volumeChange'])
    df_trending_sentiment['sentimentChange'] = df_trending_sentiment['sentimentChange'].apply(lambda x: cleanUp('sentimentChange', x))
    df_trending_sentiment['trending'] = df_trending_sentiment['trending'].apply(lambda x: cleanUp('trending', x))
    df_trending_sentiment['trendingScore'] = df_trending_sentiment['trendingScore'].apply(lambda x: cleanUp('trendingScore', x))
    df_trending_sentiment['volumeChange'] = df_trending_sentiment['volumeChange'].apply(lambda x: cleanUp('volumeChange', x))
    return df_trending_sentiment

def mergingAPI_df(df_stkDetails, df_trending_sentiment):
    ## Mapping
    df_stkDetails['sentimentChange'] = df_stkDetails['ticker'].map(df_trending_sentiment['sentimentChange'])
    df_stkDetails['trending'] = df_stkDetails['ticker'].map(df_trending_sentiment['trending'])
    df_stkDetails['trendingScore'] = df_stkDetails['ticker'].map(df_trending_sentiment['trendingScore'])
    df_stkDetails['volumeChange'] = df_stkDetails['ticker'].map(df_trending_sentiment['volumeChange'])
    # convert to numeric
    for i in ['watchlist_count', 'user_id', 'userFollowers', 'userIdeas']:
        df_stkDetails[i] = df_stkDetails[i].astype('int64')
    # convert created_at date:time
    df_stkDetails['created_at'] = df_stkDetails['created_at'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
    df_stkDetails.sort_values(by='created_at', ascending=False, inplace=True)
    return df_stkDetails

####################################################################################

def main():
    print('Downloading GDrive stockTwits_trending.pbz2')
    """ 2 options below to select """
    df_trendingDB = download_pbz2_Files(download_pbz2Id)
    # df_trendingDB = download_csv_Files(download_csv_FileId)

    print('Initial cleaning of DF')
    df_trendingDB = initial_df_clean(df_trendingDB)

    print('Download Stocktwits top 30 trending...')
    df_stkDetails, popularity = stocktwits_trending_download()
    print('Download Stocktwits 30 individual data...')
    df_trending_sentiment =  getTrendingStocksSentiment(popularity)
    print('Merging dataframes')
    df_stkDetails = mergingAPI_df(df_stkDetails, df_trending_sentiment)

    # Merging DB
    mergeDB = pd.concat([df_trendingDB,df_stkDetails])

    # db_popular = {k:list(mergeDB['ticker']).count(k) for k in mergeDB['ticker']}
    # print('Popularity from Database - Total:', len(mergeDB), dict(sorted(db_popular.items(), key=lambda item: item[1],  reverse=True)))
    # mergeDB.sort_values(by=['created_at'], ascending=False, inplace=True)
    # mergeDB.to_csv(r'C:\Users\kl\Documents\Python_files\Systems\Raw_data\Stocktwits\stockTwits_trending.csv', index=False)
    print(mergeDB.head(5))

    """ Uploading bz2 compressed pickle file """
    print('Compress and upload to GDrive')
    bz2_pickleObj = bz2.compress(pickle.dumps(mergeDB))
    # mime_types = [mimetypes.guess_type(file_names[i])[0] for i in range(len(file_names))]   # check up MIME type
    
    """ 2 options below to select """
    # upload_createFiles(bz2_pickleObj, Gfolder_id, uploadFileName, '*/pbz2')
    existingFile_update(bz2_pickleObj, Gfolder_id, uploadFileName, '*/pbz2', download_pbz2Id)

if __name__ == '__main__':
    main()
    print('Process successfully completed!')
