from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import LoginForm, SpeechForm, InterviewForm, JudgeForm, UploadJudgesForm, EventForm, DownloadForm
import random
import string
from .utils import create_judges_from_csv, export_scores
from .models import Event, Judge, Student
from datetime import date
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

        urls = {
            'delete': reverse('student_delete'),
            'edit': reverse('student_edit'),
            'create': reverse('student_create')
        }

        data = {
            'events': event_dicts,
            'students': student_dicts,
            'urls': urls
        }

        return render(request, "grader/student_panel.html", context={'data': json.dumps(data)})

    else:
        return redirect(reverse('index'))


def student_delete(request):
    if request.user.is_superuser and request.method == 'POST':
        if not request.POST.get('id'):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must provide ID in post request'
            })

        try:
            to_delete = Student.objects.get(id=request.POST['id'])
        except Student.DoesNotExist:
            return JsonResponse({
                'result': 'fail',
                'message': 'Student does not exist'
            })

        to_delete.delete()
        return JsonResponse({
            'result': 'success',
            'message': 'Deletion succeeded'
        })


def student_edit(request):
    if request.user.is_superuser and request.method == 'POST':
        if not request.POST.get('id'):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must provide ID in post request'
            })

        try:
            student = Student.objects.get(id=request.POST['id'])
        except Student.DoesNotExist:
            return JsonResponse({
                'result': 'fail',
                'message': 'Student does not exist'
            })

        if not (request.POST.get('first_name') or
                request.POST.get('last_name') or
                request.POST.get('rank') or
                request.POST.get('event')):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must supply an attribute to edit'
            })

        if request.POST.get('first_name'):
            student.first_name = request.POST['first_name']
        if request.POST.get('last_name'):
            student.last_name = request.POST['last_name']
        if request.POST.get('rank'):
            student.rank = int(request.POST['rank'])
        if request.POST.get('event'):
            try:
                new_event = Event.objects.get(id=request.POST['event'])
            except Event.DoesNotExist:
                return JsonResponse({
                    'result': 'fail',
                    'message': 'Event does not exist'
                })

            student.event = new_event

        student.save()
        return JsonResponse({
            'result': 'success',
            'message': 'Edit succeeded'
        })


def student_create(request):
    if request.user.is_superuser and request.method == 'POST':
        new_student = Student()

        error = ""

        if request.POST.get("first_name"):
            new_student.first_name = request.POST['first_name']
        else:
            error += 'Must supply a first name. '

        if request.POST.get("last_name"):
            new_student.last_name = request.POST['last_name']
        else:
            error += 'Must supply a last name. '

        if request.POST.get('rank'):
            new_student.rank = int(request.POST['rank'])
        else:
            error += 'Must supply a rank. '

        if request.POST.get('event'):
            try:
                n_event = Event.objects.get(id=int(request.POST['event']))
                new_student.event = n_event
            except Event.DoesNotExist:
                error += 'Not a valid event id. '

        else:
            error += 'Must supply an event id. '

        if error == "":
            new_student.save()
            return JsonResponse({
                'result': 'success',
                'student': {
                    'id': new_student.id,
                    'first_name': new_student.first_name,
                    'last_name': new_student.last_name,
                    'rank': new_student.rank,
                    'event_id': new_student.event.id
                }
            })

        else:
            return JsonResponse({'result': 'fail', 'message': error})

