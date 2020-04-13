from django.conf.urls import url
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    url(r"^$", views.MenuView.as_view(), name="index"),
    # url(r"^base/point/$", views.PointView.as_view(), name="point"),
    url(r"^base/emptymap/$", views.EmptyMap.as_view(), name="emptymap"),
    url(r"^base/test$", views.TestView.as_view(), name="test"),
    url(r"^base/statistics/$", views.Statistics.as_view(), name="statistics"),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
]