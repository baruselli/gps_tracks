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

        from options.models import OptionSet
        download_dir = OptionSet.get_option("PHOTOS_DOWNLOAD_DIR", default=settings.PHOTOS_DIR)


        from import_app.utils import find_files_in_dir,get_all_photo_dirs,name_wo_path
        dirs = get_all_photo_dirs()
        files = find_files_in_dir(dir_=dirs, extensions=[".jpg",])        
        existing_file_list=[name_wo_path(f) for f in files]

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
                            photo_path= os.path.join(download_dir, file1["originalFilename"])
                            logger.info("downloading " + photo_path)
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

        from options.models import OptionSet

        download_dir = OptionSet.get_option("PHOTOS_DOWNLOAD_DIR", default=settings.PHOTOS_DIR)

        #existing_file_list = os.listdir(download_dir)
        from import_app.utils import find_files_in_dir,get_all_photo_dirs,name_wo_path
        dirs = get_all_photo_dirs()
        files = find_files_in_dir(dir_=dirs, extensions=[".jpg",])        
        existing_file_list=[name_wo_path(f) for f in files]


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
                            photo_path = os.path.join(download_dir, item["filename"])
                            logger.info("downloading " + photo_path)
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
        filename=OptionSet.get_option("TOMTOM_FILENAME")
        logger.info("Download %s %s" %(filename,ext))
        all_data = base + "/service/webapi/v2/activity/zip/%s?format=%s"%(filename,ext)
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

def download_garmin():

    logger.info("download_garmin")

    import datetime

    from garminconnect import (
        Garmin,
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )

    files = []

    try:
        ## Initialize Garmin api with your credentials
        garmin_user=OptionSet.get_option("GARMIN_USER")
        garmin_password=OptionSet.get_option("GARMIN_PASSWORD")        
        api = Garmin(garmin_user, garmin_password)

        max_attempts = 3
        attempts = 0

        while attempts < max_attempts:
            try:
                logger.info("Garmin trying to login, %s" %attempts)
                api.login()
                break
            except (
                    GarminConnectConnectionError,
                    GarminConnectAuthenticationError,
                    GarminConnectTooManyRequestsError,
                ) as e:
                logger.info(e)
                attempts += 1
                import time
                time.sleep(1)

        ## Login to Garmin Connect portal


        activities = api.get_activities(0,9999) # 0=start, 1=limit

        out_path = os.path.join(settings.TRACKS_DIR, "garmin")
        try:
            os.mkdir(out_path)
        except:
            pass

        for activity in activities:
            from pprint import pprint
            #pprint(activity)
            activity_id = activity["activityId"]
            activity_name = activity["activityName"].replace(" ","_")
            activity_time = activity["startTimeLocal"].replace(":","-").replace(" ","_")
            logger.info("api.download_activities(%s, %s)", activity_id,activity_name)
            output_file = activity_time + "_" + activity_name + ".tcx"
            output_file_path = os.path.join(out_path, output_file)

            if not os.path.exists(output_file_path) and activity["distance"] and activity["distance"]>0:
                tcx_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.TCX)
                logger.info("downloading " + output_file_path)
                with open(output_file_path, "wb") as fb:
                    fb.write(tcx_data)
                files.append(output_file_path)

    except Exception as e:
        logger.error("Error in download_garmin: %s", e)

    return files