from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .forms import LoginForm, SpeechForm, InterviewForm, JudgeForm, UploadJudgesForm, EventForm, DownloadForm
import random
import string
from .utils import create_judges_from_csv, export_scores
from .models import Event, Judge, Student
from datetime import date
from django.core import serializers
import json
# Create your views here.


def index(request):
    if request.user.is_authenticated():
        return render(request, "grader/home.html", context={"name":request.user.first_name})
    else:
        return HttpResponseRedirect("login")


def import_judge(request):
    if request.user.is_superuser:
        if request.method == "POST":
            judge_data = JudgeForm(request.POST)
            if judge_data.is_valid():
                judge = judge_data.save(commit=False)
                judge.username = judge.first_name[0] + judge.last_name
                password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                judge.set_password(password)
                judge.save()

                return render(request, "grader/import_success.html", context={"username":judge.username, "password": password})
            else:
                return render(request, "grader/import.html", context={"form": judge_data})
        else:
            judge_form = JudgeForm()
            judge_form.fields['event'].queryset = Event.objects.filter(date__gte=date.today())
            return render(request, "grader/import.html", context={"form": judge_form, "batch_form": UploadJudgesForm()})


def import_judges(request):
    if request.user.is_superuser:
        if request.method == "POST":
            judges_data = UploadJudgesForm(request.POST, request.FILES)
            if judges_data.is_valid():
                event_id = request.POST['event']
                judges = create_judges_from_csv(request.FILES['file'], event_id)
                return render(request, 'grader/batch_import_success.html', context={"judges": judges})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            return HttpResponse("Wrong password or username. Click back to go back.")

    else:
        login_form = LoginForm()
        return render(request, "grader/login.html", context={"login_form":login_form})


def speech(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            score_data = SpeechForm(request.POST)
            if score_data.is_valid():
                score = score_data.save(commit=False)
                score.grader = request.user
                score.save()
                return HttpResponseRedirect("/")
            else:
                return render(request, "grader/speech.html", context={'form':score_data})
        else:
            speech_score_form = SpeechForm()
            return render(request, "grader/speech.html", context={'form':speech_score_form})

    else:
        return HttpResponseRedirect("/")


def interview(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            score_data = InterviewForm(request.POST)
            if score_data.is_valid():
                score = score_data.save(commit=False)
                score.grader = request.user
                score.save()
                return HttpResponseRedirect("/")
            else:
                return render(request, "grader/speech.html", context={'form':score_data})
        else:
            interview_score_form = InterviewForm()
            return render(request, "grader/interview.html", context={'form':interview_score_form})

    else:
        return HttpResponseRedirect("/")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

"""
@csrf_exempt
def find_student(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        judge_id = request.POST['judge_id']
        type = request.POST['type']
        user = User.objects.get(id=judge_id)
        judge = user.__subclasses__()[0]
        try:
            student = Student.objects.get(student_id=student_id)
            name = student.first_name + " " + student.last_name
            if type == 'speech':
                if student.speech_room == judge.room:
                    return JsonResponse({'name': name, 'exists': True, 'correct': True})
                else:
                    return JsonResponse({'name': name, 'exists': True, 'correct': False})
            if type == 'interview':
                if student.interview_room == judge.room:
                    return JsonResponse({'name': name, 'exists': True, 'correct': True})
                else:
                    return JsonResponse({'name': name, 'exists': True, 'correct': False})
        except ObjectDoesNotExist:
            return JsonResponse({'exists': False})
"""

def download(request):
    if request.user.is_superuser:
        if request.method == "POST":
            event_choice = DownloadForm(request.POST)
            event = int(request.POST['event'])
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="scores.csv"'
            response = export_scores(response, event, int(request.POST['type']))
            print(request.POST['type'])
            return response
        else:
            return render(request, "grader/download_scores.html", context={'form':DownloadForm()})


def export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scores.csv"'
    response = export_scores(response)

    return response


def event(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            event_data = EventForm(request.POST)
            if event_data.is_valid():
                event_data.save()
                return HttpResponseRedirect("/")
            else:
                return render(request, "grader/create_event.html", context={'form':event_data})

        else:
            form = EventForm()
            return render(request, "grader/create_event.html", context={'form':form})


def student_panel_view(request):
    if request.user.is_superuser:
        event_dicts = []
        student_dicts = []
        events = Event.objects.all()
        students = Student.objects.all()

        for _event in events:
            event_dict = {
                'id': _event.id,
                'name': _event.name,
                'date': _event.date.strftime('%Y-%m-%d'),
                'location': _event.location
            }

            event_dicts.append(event_dict)

        for _student in students:
            student_dict = {
                'id': _student.id,
                'event_id': _student.event.id,
                'first_name': _student.first_name,
                'last_name': _student.last_name,
                'rank': _student.rank
            }

            student_dicts.append(student_dict)

        data = {
            'events': event_dicts,
            'students': student_dicts
        }

        return render(request, "grader/student_panel.html", context={'data': json.dumps(data)})
