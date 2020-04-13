import numpy as np
import math
import os
from pprint import pprint
from datetime import datetime
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import traceback
from tracks.models import Track
from django.conf import settings
from options.models import OptionSet

def googlehistoryselenium():

    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    import time, os
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options

    from datetime import datetime, timedelta , date

    out_dir = os.path.join(settings.TRACKS_DIR,"timeline")

    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    prefs = {'download.default_directory' :out_dir}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(OptionSet.get_option("CHROME_PATH"),options=options)

    initial_day= date.today()- timedelta(1)
    day=initial_day
    timeout=30

    missing_dates=get_missing_history_dates(min_date=OptionSet.get_option("MIN_DATE_GOOGLE_HISTORY"))

    for date in missing_dates:
        logger.info(date)
        date=date.strftime("%Y-%m-%d")
        driver.get("https://www.google.com/maps/timeline?pb=!1m2!1m1!1s%s" %date)

        try:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.ID, "identifierId")))
            driver.find_element_by_id("identifierId").send_keys(OptionSet.get_option("GMAIL"))
            #password = browser.find_element_by_class_name("find password field")
            driver.find_element_by_class_name("RveJvd").click()
            xpath1="//input[@name='password']"
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath1)))
            time.sleep(3)
            driver.find_element_by_xpath(xpath1).send_keys(OptionSet.get_option("GMAIL_PWD"))
            driver.find_element_by_class_name("RveJvd").click()
        except:
            pass
        try:
            xpath2="(.//*[normalize-space(text()) and normalize-space(.)='help'])[1]/following::i[1]"
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath2)))
            driver.find_element_by_xpath(xpath2).click()
            xpath3="(.//*[normalize-space(text()) and normalize-space(.)='Hide raw data'])[1]/following::div[2]"
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath3)))
            driver.find_element_by_xpath(xpath3).click()
            filename = max([os.path.join(out_dir,f) for f in os.listdir(out_dir)], key=os.path.getctime)
            logger.info("OK: %s" %filename)
        except Exception as e:
            logger.warning("KO: %s" %e)



    driver.close()

def get_date_history_files(file):
    date_string = file[8:18]

    return date_string


def get_history_files(min_date=None, find_in_db=True):

    import os
    import datetime

    out_dir = os.path.join(settings.TRACKS_DIR, "timeline")
    files = [{"name": f[:-4], "date": get_date_history_files(f), "extension": f[-4:]} for f in os.listdir(out_dir)]

    track_names = [t["name"] for t in files]

    if find_in_db:
        imported_tracks = Track.objects.filter(name_wo_path_wo_ext__in=track_names).values_list("name_wo_path_wo_ext","pk")
        imported_tracks_dict = {name: pk for name, pk in imported_tracks}
        for f in files:
            if f["name"] in imported_tracks_dict.keys():
                f.update({"pk":imported_tracks_dict[f["name"]]})
            else:
                f.update({"pk": None})

    if not min_date:
        try:
            min_date = min([f["date"] for f in files])
        except:
            traceback.print_exc()
            min_date = datetime.date(2017, 1, 1)

    max_date = datetime.date.today() - datetime.timedelta(days=1)

    import pandas as pd

    dates = pd.date_range(start=min_date, end=max_date).to_pydatetime().tolist()

    files_ok = []
    for d in dates:
        d_string = d.strftime("%Y-%m-%d")
        file_ = None
        pk=None
        extension=""
        for f in files:
            if f["date"] == d_string:
                file_ = f["name"]
                extension = f["extension"]
                if find_in_db:
                    pk = f["pk"]
                break
        files_ok.append({"date": d, "file": file_, "pk" : pk, "extension":extension})

    return files_ok

def get_missing_history_dates(min_date):
    files=get_history_files(min_date=min_date,find_in_db=False)

    files_missing=[f["date"] for f in files if not f["file"]]
    files_missing.sort(reverse=True)

    return files_missing