from tracks.models import Track
from photos.models import Photo
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def get_tracks_n_years_ago(n_years=1,n_days=2,just_one=True):

    today = date.today()

    n_years_ago_0 =today - relativedelta(years=n_years)

    pm_days= list(range(n_days+1))+list(range(-1,-n_days-1,-1))
    #print(pm_days)
    dates = [n_years_ago_0+relativedelta(days=n) for n in pm_days]

    tracks_n_years_ago=Track.objects.filter(date__in=dates).exclude(groups__exclude_from_search=True)

    if just_one and tracks_n_years_ago:
        #take one randomly
        track=tracks_n_years_ago.order_by('?').first()
        photo=track.photos.all().order_by('?').first()
        return {"track":track,"dates":dates,"photo":photo}
    elif just_one and not tracks_n_years_ago:
        if n_days<7:
            return get_tracks_n_years_ago(n_years=n_years,n_days=n_days+1,just_one=True)
        else:
            # if still no tracks, try to take at least a photo!
            photo=Photo.objects.filter(time__date__in=dates).order_by('?').first()
            return {"track":None,"dates":dates,"photo":photo}
    else:
        return {"tracks":tracks_n_years_ago,"dates":dates,"photo":None}

