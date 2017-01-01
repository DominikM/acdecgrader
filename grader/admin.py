from django.contrib import admin
from .models import SpeechScore, InterviewScore, Judge, Event
# Register your models here.

admin.site.register(Judge)
admin.site.register(SpeechScore)
admin.site.register(InterviewScore)
admin.site.register(Event)
