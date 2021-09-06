
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

def path_to_url(filename):
    from import_app.utils import get_all_photo_dirs
    import os
    all_dirs = sorted(get_all_photo_dirs(), key=len,reverse=True)
    for dir_ in all_dirs:
        if dir_ in filename:
            rel_path_name = os.path.relpath(filename,dir_).replace("\\","/")
            break
    else:
        rel_path_name = os.path.relpath(filename,settings.MEDIA_BASE_DIR).replace("\\","/")
        dir_ = settings.MEDIA_BASE_DIR

    return match_url_path(dir_) + rel_path_name