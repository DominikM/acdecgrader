from django import forms
from django.forms import SelectDateWidget, ModelChoiceField, inlineformset_factory
from django.contrib.auth.models import User
from .models import SpeechScore, InterviewScore, Judge, Event
from datetime import date


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", max_length=30, widget=forms.PasswordInput)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name',
            'date',
            'location'
        ]
        widgets = {
            'date': SelectDateWidget()
        }


JudgeInlineForm = inlineformset_factory(
    User,
    Judge,
    fields = [
        'room',
        'event'
    ]
)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name'
        ]
        inlines = [
            JudgeInlineForm
        ]


class UploadJudgesForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.filter(date__gte=date.today()))
    file = forms.FileField()


class DownloadForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all())
    type = forms.ChoiceField(widget=forms.RadioSelect,
                             choices=(
                                (1, "Detailed"),
                                (0, "Simple"))
                             )


class StudentIDForm(forms.Form):
    student_id = forms.IntegerField()


class SpeechForm(forms.ModelForm):
    student_id = forms.IntegerField()
    class Meta:
        model = SpeechScore
        fields = [
            'student_id',
            'student_first_name',
            'student_last_name',
            'development_score',
            'effectiveness_score',
            'correctness_score',
            'appropriateness_score',
            'value_score',
            'voice_score',
            'nonverbal_score',
            'content_score',
            'delivery_score',
            'overall_effect',
            'time_violations'
        ]


class InterviewForm(forms.ModelForm):
    student_id = forms.IntegerField()
    class Meta:
        model = InterviewScore
        fields = [
            'student_id',
            'student_first_name',
            'student_last_name',
            'voice_score',
            'language_score',
            'interpersonal_score',
            'nonverbal_score',
            'manner_score',
            'listening_score',
            'answering_score',
            'response_score',
            'overall_effect',
            'appearance_score'
        ]



