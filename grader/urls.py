"""acdec URL Configuration
"""
from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name="index"),
    re_path(r'^login/$', views.login_view, name="login"),
    re_path(r'^logout/$', views.logout_view, name="logout"),
    re_path(r'^speech/$', views.speech, name="speech"),
    re_path(r'^interview/$', views.interview, name="interview"),
    re_path(r'^export/$', views.export, name="export"),
    re_path(r'^event/$', views.event, name="event"),
    re_path(r'^download/$', views.download, name="download"),

    re_path(r'^students/$', views.student_panel_view, name="student_panel"),
    re_path(r'^students/delete/$', views.student_delete, name="student_delete"),
    re_path(r'^students/edit/$', views.student_edit, name="student_edit"),
    re_path(r'^students/create/$', views.student_create, name="student_create"),
    re_path(r'^students/bulk_create/$', views.students_create, name='students_create'),

    re_path(r'^judges/$', views.judge_panel_view, name="judge_panel"),
    re_path(r'^judges/delete/$', views.judge_delete, name="judge_delete"),
    re_path(r'^judges/edit/$', views.judge_edit, name="judge_edit"),
    re_path(r'^judges/create/$', views.judge_create, name="judge_create"),
    re_path(r'^judges/bulk_create/$', views.judges_create, name="judges_create"),
    # url(r'^find_student/$', views.find_student, name="find_student")

    # url(r'^times/$', views.times_panel_view, name='times_panel'),
    # url(r'^times/delete/$', views.time_delete, name='time_delete'),
    # url(r'^times/edit/$', views.time_edit, name='time_edit'),
    # url(r'^times/create/$', views.time_create, name='time_create'),

    re_path(r'^assignments/$', views.assignments_view, name='assignments_view'),
    re_path(r'^assignments/create/$', views.assignment_create, name='assignment_create'),
    re_path(r'^assignments/bulk_create/$', views.assignments_create, name='assignments_create'),
    re_path(r'^assignments/edit/$', views.assignment_edit, name='assignment_edit'),
    re_path(r'^assignments/delete/$', views.assignment_delete, name='assignment_delete')

]
