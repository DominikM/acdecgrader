"""acdec URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^login/$', views.login_view, name="login"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^speech/$', views.speech, name="speech"),
    url(r'^interview/$', views.interview, name="interview"),
    url(r'^export/$', views.export, name="export"),
    url(r'^event/$', views.event, name="event"),
    url(r'^download/$', views.download, name="download"),

    url(r'^students/$', views.student_panel_view, name="student_panel"),
    url(r'^students/delete/$', views.student_delete, name="student_delete"),
    url(r'^students/edit/$', views.student_edit, name="student_edit"),
    url(r'^students/create/$', views.student_create, name="student_create"),

    url(r'^judges/$', views.judge_panel_view, name="judge_panel"),
    url(r'^judges/delete/$', views.judge_delete, name="judge_delete"),
    url(r'^judges/edit/$', views.judge_edit, name="judge_edit"),
    url(r'^judges/create/$', views.judge_create, name="judge_create"),
    url(r'^judges/bulk_create/$', views.judges_create, name="judges_create"),
    # url(r'^find_student/$', views.find_student, name="find_student")

    url(r'^times/$', views.times_panel_view, name='times_panel'),
    url(r'^times/delete/$', views.time_delete, name='time_delete'),
    url(r'^times/edit/$', views.time_edit, name='time_edit'),
    url(r'^times/create/$', views.time_create, name='time_create')

]
