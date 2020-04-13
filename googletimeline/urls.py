from django.conf.urls import url
from . import views


urlpatterns = [

url(r"^download_googlehistory", views.GoogleHistorySeleniumView.as_view(),  name="download_googlehistory", ),
url(r"^history_files", views.GoogleHistoryFilesView.as_view(), name="history_files", ),
url(r"^import_history_files", views.ImportGoogleHistoryFilesView.as_view(), name="import_history_files", ),

]