
from django.conf import settings

def match_url_path(path):
    """associate an url to each media path"""
    if path == settings.MEDIA_BASE_DIR:
        return settings.MEDIA_URL
    elif settings.MEDIA_BASE_DIR in path:
        import os
        rel_path_name = os.path.relpath(path,settings.MEDIA_BASE_DIR).replace("\\","/")
        return settings.MEDIA_URL + rel_path_name + "/"
    else:
        return "/media_" + path.replace("/","_").replace("\\","_").replace(":","_").replace(" ","_").replace("'","_").replace('"',"_")+"/"
