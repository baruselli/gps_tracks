# gps_tracks

GPS Tracks is a Django application aimed at storing and visualizing GPS data files (gpx, kml, kmz, tcx, and some csv).

It is conceived as program to be run locally on the development server.

PostreSQL is required (it has been tested on version 10.3).


Run:

python manage.py runserver

then go to http://localhost:8000/ on a web browser (Chrome or Firefox).



Tests:

python manage.py test
