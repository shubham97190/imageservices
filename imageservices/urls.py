from django.conf.urls import url
from . import views
from django.conf.urls import include

urlpatterns = [
    url(r'^get_image/$', views.GetImageView.as_view())
]