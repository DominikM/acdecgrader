"""acdec URL Configuration
"""
from django.urls import re_path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include("grader.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
