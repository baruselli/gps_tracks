
from django.conf import settings

def match_url_path(path):
    """associate an url to each media path"""
    if path == settings.MEDIA_BASE_DIR:
        return settings.MEDIA_URL
    else:
        return "/media_" + path.replace("/","_").replace("\\","_").replace(":","_").replace(" ","_").replace("'","_").replace('"',"_")+"/"
