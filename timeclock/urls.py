from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', login_required(views.ClockInOutView.as_view()), name="clockinout"),
    url(r'^timecards/$', login_required(views.PunchList.as_view()), name="timecards"),
    #url(r'^punchform/$', login_required(views.SearchForm.as_view()), name="punchform"),
]
