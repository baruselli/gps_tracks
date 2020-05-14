call venv\Scripts\activate.bat
rm -r dist
rm -r build
pyinstaller gps_tracks.spec
//pyinstaller --name=gps_tracks manage.py
