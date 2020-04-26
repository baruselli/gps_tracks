import numpy as np
import math
import os
from tracks.models import *
from pprint import pprint
from datetime import datetime
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import numpy as np
import math
from pprint import pprint
import traceback
from options.models import OptionSet

def google_connection():
    try:
        """https://stackoverflow.com/questions/50573196/access-google-photo-api-with-python-using-google-api-python-client/50573233#50573233"""
        """https://developers.google.com/drive/api/v3/quickstart/python"""
        # TODO: form to upload credentials.json
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
                'https://www.googleapis.com/auth/photoslibrary']

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        if os.path.exists('auth/token.pickle'):
            with open('auth/token.pickle', 'rb') as token:
                creds = pickle.load(token)
                logger.info ("Using stored credentials in auth/token.pickle")
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            logger.info ("Credentials not valid or not existing")
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'auth/client_secrets.json', SCOPES) #'auth/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('auth/token.pickle', 'wb') as token:
                logger.info ("Saving credentials")
                pickle.dump(creds, token)
        return creds
    except Exception as e:
        logger.error("Error in google_connection: %s"%e)
        return None

def google_drive_tracks():
    try:
        from pydrive.auth import GoogleAuth
        from pydrive.drive import GoogleDrive

        import os

        logger.info("google_drive_tracks")
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()

        drive = GoogleDrive(gauth)

        downloaded_tracks = []

        dirs = OptionSet.get_option("GOOGLE_TRACKS_DIRS")
        dirs_list=dirs.split("\n")

        logger.info("starting...")
        for dir_ in dirs_list:
            dir_=dir_.strip()
            if dir_:
                logger.info("Looking in dir %s" %dir_)
                dir_name = drive.CreateFile(
                    {"id": "%s" %dir_}
                )["title"]

                file_list = drive.ListFile(
                    {"q": "'%s' in parents" %dir_}
                ).GetList()

                out_dir=os.path.join(settings.TRACKS_DIR, "google_drive",dir_name)
                import os
                try:
                    os.makedirs(out_dir)
                except:
                    pass

                existing_file_list = os.listdir(out_dir)

                for file1 in file_list:
                    if file1["title"] not in existing_file_list:
                        file_path= os.path.join(out_dir, file1["title"])
                        logger.info("%s" % (file_path))
                        file1.GetContentFile(file_path)
                        downloaded_tracks.append(file_path)

        logger.info("...done")
        return downloaded_tracks
    except Exception as e:
        logger.error("Error in google_drive_tracks: %s"%e)
        return []
       

def google_drive_photos():
    try:
        from pydrive.auth import GoogleAuth
        from pydrive.drive import GoogleDrive

        import os

        logger.info("google_drive_photos")

        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()

        drive = GoogleDrive(
            gauth
        )  # Create GoogleDrive instance with authenticated GoogleAuth instance

        existing_file_list = os.listdir(settings.PHOTOS_DIR)
        # print (existing_file_list)

        downloaded_photos=[]

        dirs = OptionSet.get_option("GOOGLE_PHOTOS_DIRS")

        dirs_list=dirs.split("\n")

        for d in dirs_list:
            d = d.strip()
            if d:
                logger.info("Looking in dir %s" %d)
                file_list = drive.ListFile(
                    {"q": "'%s' in parents" %d}
                ).GetList()
                for file1 in file_list:
                    # qui evito di scaricare cose che non sono foto
                    if (
                        "imageMediaMetadata" in file1
                        and "cameraMake" in file1["imageMediaMetadata"]
                    ):
                        # print (file1['originalFilename'])
                        # qui cerco che la foto non esista gia
                        if file1["originalFilename"] not in existing_file_list:
                            logger.info("downloading " + file1["originalFilename"])
                            photo_path= os.path.join(settings.PHOTOS_DIR, file1["originalFilename"])
                            file1.GetContentFile(photo_path)
                            downloaded_photos.append(photo_path)
        logger.info("done")
        return downloaded_photos
    except Exception as e:
        logger.error("Error in google_drive_photos: %s"%e)
        return []


def google_photos(only_last_year=False):
    try:
        import os.path
        import urllib.request
        from googleapiclient.discovery import build

        logger.info("google_photos")
        downloaded_photos=[]

        creds = google_connection()
        # service = build('drive', 'v3', credentials=creds)
        service = build('photoslibrary', 'v1', credentials=creds)

        existing_file_list = os.listdir(settings.PHOTOS_DIR)

        from options.models import OptionSet
        if only_last_year:
            min_year=datetime.now().year
        else:
            min_year= OptionSet.get_option("MIN_YEAR_GOOGLE_PHOTOS")

        year_list=range(min_year,datetime.now().year+1)

        for year in year_list:
            logger.info("Checking year %s" %year)
            nextpagetoken = 'Dummy'
            while nextpagetoken != '':
                nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
                results = service.mediaItems().search(
                    body={"pageSize": 100, "pageToken": nextpagetoken,
                        "filters": {"dateFilter": {"dates": [{"year": year}]}
                                    }}).execute()
                items = results.get('mediaItems', [])
                nextpagetoken = results.get('nextPageToken', '')
                for item in items:
                    if item["filename"] not in existing_file_list:
                        # here I (try to) filter real photos, not other images
                        if "mediaMetadata" in item and "photo" in item["mediaMetadata"] and item["mediaMetadata"]["photo"]:
                            logger.info("downloading " + item["filename"])
                            photo_path = os.path.join(settings.PHOTOS_DIR, item["filename"])
                            urllib.request.urlretrieve(item["baseUrl"]+"=d", photo_path) #=d needed for full image
                            downloaded_photos.append(photo_path)

        logger.info("End google_photos")

        return downloaded_photos
    except Exception as e:
        logger.error("Error in google_photos: %s"%e)
        return []

def download_tomtom(ext="csv"):

    try:
        import requests
        import os
        base = "https://mysports.tomtom.com"
        login = base + "/service/webapi/v2/auth/user/login"

        s = requests.session()
        from options.models import OptionSet
        params = {"email": OptionSet.get_option("TOMTOM_USER"), "password": OptionSet.get_option("TOMTOM_PASSWORD")}
        r1 = s.post(login, json=params)

        import zipfile
        logger.info("Download %s" %ext)
        all_data = base + "/service/webapi/v2/activity/zip/1.zip?format=%s"%ext
        r3 = s.get(all_data)
        out_file = os.path.join(settings.TRACKS_DIR, "tomtom_%s.zip"%ext)
        open(out_file, "wb").write(r3.content)
        zip_ref = zipfile.ZipFile(out_file, "r")
        out_path = os.path.join(settings.TRACKS_DIR, "tomtom")
        zip_ref.extractall(out_path)
        zip_ref.close()
        import glob
        files = [f for f in glob.glob(os.path.join(out_path , "*.%s" %ext))]
        return files
    except Exception as e:
        logger.error("Error in download_tomtom: %s"%e)
        return []

