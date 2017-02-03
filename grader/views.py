from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import LoginForm, SpeechForm, InterviewForm, UserForm, UploadJudgesForm, EventForm, DownloadForm
import random
import string
import csv
from .utils import export_scores, get_unique_username
from .models import Event, Judge, Student, Time, Occurrence
from datetime import datetime
import json
# Create your views here.


def index(request):
    if request.user.is_authenticated():
        return render(request, "grader/home.html", context={"name":request.user.first_name})
    else:
        return HttpResponseRedirect("login")


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
                'comp_id': _student.comp_id,
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
                request.POST.get('event') or
                request.POST.get('comp_id')):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must supply an attribute to edit'
            })

        if request.POST.get('comp_id'):
            student.comp_id = int(request.POST['comp_id'])
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
        if request.POST.get('comp_id'):
            new_student.comp_id = int(request.POST['comp_id'])
        else:
            error += 'Must supply an ID. '

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
                    'comp_id': new_student.comp_id,
                    'first_name': new_student.first_name,
                    'last_name': new_student.last_name,
                    'rank': new_student.rank,
                    'event_id': new_student.event.id
                }
            })

        else:
            return JsonResponse({'result': 'fail', 'message': error})


def students_create(request):
    if request.method == 'POST' and request.user.is_superuser:
        event_id = request.POST['event']
        student_reader = csv.reader(request.FILES['file'].read().decode('utf-8').splitlines())
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({
                'result': 'fail',
                'message': 'Event does not exist'
            })

        students = []
        for row in student_reader:
            student_id = row[0]
            full_name = row[1]
            first_name = full_name.split(' ')[0]
            last_name = full_name.split(' ')[1]

            new_student = Student.create(
                comp_id=int(student_id),
                first_name=first_name,
                last_name=last_name
            )

            students.append({
                'id': new_student.id,
                'comp_id': student_id,
                'first_name': first_name,
                'last_name': last_name,
                'event_id': event.id,
            })


        return JsonResponse({
            'result': 'success',
            'students': students
        })


def judge_panel_view(request):
    if request.user.is_superuser:
        event_dicts = []
        judge_dicts = []
        events = Event.objects.all()
        judges = Judge.objects.all()

        for _event in events:
            event_dict = {
                'id': _event.id,
                'name': _event.name,
                'date': _event.date.strftime('%Y-%m-%d'),
                'location': _event.location
            }

            event_dicts.append(event_dict)

        for _judge in judges:
            judge_dict = {
                'id': _judge.id,
                'event_id': _judge.event.id,
                'first_name': _judge.user.first_name,
                'last_name': _judge.user.last_name,
                'username': _judge.user.username,
                'password': _judge.password
            }

            judge_dicts.append(judge_dict)

        urls = {
            'delete': reverse('judge_delete'),
            'edit': reverse('judge_edit'),
            'create': reverse('judge_create'),
            'bulk_create': reverse('judges_create')
        }

        data = {
            'events': event_dicts,
            'judges': judge_dicts,
            'urls': urls
        }

        return render(request, "grader/judge_panel.html", context={'data': json.dumps(data)})

    else:
        return redirect(reverse('index'))


def judge_delete(request):
    if request.user.is_superuser and request.method == 'POST':
        if not request.POST.get('id'):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must provide ID in post request'
            })

        try:
            to_delete = Judge.objects.get(id=request.POST['id'])
        except Judge.DoesNotExist:
            return JsonResponse({
                'result': 'fail',
                'message': 'Judge does not exist'
            })

        to_delete.user.delete()
        return JsonResponse({
            'result': 'success',
            'message': 'Deletion succeeded'
        })


def judge_edit(request):
    if request.user.is_superuser and request.method == 'POST':
        if not request.POST.get('id'):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must provide ID in post request'
            })

        try:
            judge = Judge.objects.get(id=request.POST['id'])
        except Judge.DoesNotExist:
            return JsonResponse({
                'result': 'fail',
                'message': 'Judge does not exist'
            })

        if not (request.POST.get('first_name') or
                request.POST.get('last_name') or
                request.POST.get('event')):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must supply an attribute to edit'
            })

        if request.POST.get('first_name'):
            judge.user.first_name = request.POST['first_name']
        if request.POST.get('last_name'):
            judge.user.last_name = request.POST['last_name']
        if request.POST.get('event'):
            try:
                new_event = Event.objects.get(id=request.POST['event'])
            except Event.DoesNotExist:
                return JsonResponse({
                    'result': 'fail',
                    'message': 'Event does not exist'
                })

            judge.event = new_event

        judge.user.save()
        judge.save()
        return JsonResponse({
            'result': 'success',
            'message': 'Edit succeeded'
        })


def judges_create(request):
    if request.user.is_superuser and request.method == 'POST':
        event_id = request.POST['event']
        judge_reader = csv.reader(request.FILES['file'].read().decode('utf-8').splitlines())
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({
                'result': 'fail',
                'message': 'Event does not exist'
            })

        judges = []
        for row in judge_reader:
            full_name = row[0]
            email = row[1]
            room = row[2]
            first_name = full_name.split(' ')[0]
            last_name = full_name.split(' ')[1]
            username = get_unique_username(first_name[0] + last_name)

            password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

            new_user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )

            new_judge = Judge.objects.create(
                room=room,
                event=event,
                user=new_user,
                password=password
            )

            judges.append({
                'id': new_judge.id,
                'first_name': first_name,
                'last_name': last_name,
                'event_id': event.id,
                'username': username,
                'password': password
            })

        return JsonResponse({
            'result': 'success',
            'judges': judges
        })


def judge_create(request):
    if request.user.is_superuser and request.method == 'POST':
        new_judge = Judge()
        new_user = User()

        error = ""

        if request.POST.get("first_name"):
            new_user.first_name = request.POST['first_name']
        else:
            error += 'Must supply a first name. '

        if request.POST.get("last_name"):
            new_user.last_name = request.POST['last_name']
        else:
            error += 'Must supply a last name. '

        if request.POST.get('event'):
            try:
                n_event = Event.objects.get(id=int(request.POST['event']))
                new_judge.event = n_event
            except Event.DoesNotExist:
                error += 'Not a valid event id. '

        else:
            error += 'Must supply an event id. '

        if error == "":
            new_user.username = get_unique_username(new_user.first_name[0] + new_user.last_name)

            new_judge.password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            new_user.set_password(new_judge.password)
            new_user.save()

            new_judge.user = new_user
            new_judge.save()
            return JsonResponse({
                'result': 'success',
                'judge': {
                    'id': new_judge.id,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name,
                    'event_id': new_judge.event.id,
                    'username': new_user.username,
                    'password': new_judge.password
                }
            })

        else:
            return JsonResponse({'result': 'fail', 'message': error})


def times_panel_view(request):
    if request.user.is_superuser:
        event_dicts = []
        time_dicts = []
        events = Event.objects.all()
        times = Time.objects.all().order_by('start')

        for _event in events:
            event_dict = {
                'id': _event.id,
                'name': _event.name,
                'date': _event.date.strftime('%Y-%m-%d'),
                'location': _event.location
            }

            event_dicts.append(event_dict)

        for _time in times:
            time_dict = {
                'id': _time.id,
                'event': _time.event.id,
                'start': _time.start.strftime('%H:%M'),
                'display_start': _time.start.strftime('%I:%M %p'),
                'name': _time.name
            }

            time_dicts.append(time_dict)


        urls = {
            'delete': reverse('time_delete'),
            'edit': reverse('time_edit'),
            #'create': reverse('judge_create'),
            #'bulk_create': reverse('judges_create')
        }


        data = {
            'events': event_dicts,
            'times': time_dicts,
            'urls': urls
        }

        return render(request, 'grader/times.html', context={'data': json.dumps(data)})

    else:
        return redirect(reverse('index'))


def time_delete(request):
    if request.user.is_superuser and request.method == 'POST':
        if not request.POST.get('id'):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must provide ID in post request'
            })

        try:
            to_delete = Time.objects.get(id=request.POST['id'])
        except Time.DoesNotExist:
            return JsonResponse({
                'result': 'fail',
                'message': 'Time does not exist'
            })

        to_delete.delete()
        return JsonResponse({
            'result': 'success',
            'message': 'Deletion succeeded'
        })


def time_edit(request):
    if request.user.is_superuser and request.method == 'POST':
        if not request.POST.get('id'):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must provide ID in post request'
            })

        try:
            edit_time = Time.objects.get(id=request.POST['id'])
        except Time.DoesNotExist:
            return JsonResponse({
                'result': 'fail',
                'message': 'Time does not exist'
            })

        if not (request.POST.get('name') or
                request.POST.get('start')):
            return JsonResponse({
                'result': 'fail',
                'message': 'Must supply an attribute to edit'
            })

        if request.POST.get('name'):
            edit_time.name = request.POST['name']
        if request.POST.get('start'):
            edit_time.start = datetime.strptime(request.POST['start'], '%H:%M').time()
        if request.POST.get('event'):
            try:
                new_event = Event.objects.get(id=request.POST['event'])
            except Event.DoesNotExist:
                return JsonResponse({
                    'result': 'fail',
                    'message': 'Event does not exist'
                })

            edit_time.event = new_event

        edit_time.save()
        return JsonResponse({
            'result': 'success',
            'message': 'Edit succeeded',
            'time': {
                'id': edit_time.id,
                'event': edit_time.event.id,
                'start': edit_time.start.isoformat(),
                'display_start': edit_time.start.strftime('%I:%M %p'),
                'name': edit_time.name
            }
        })


def time_create(request):
    if request.user.is_superuser and request.method == 'POST':
        new_time = Time()

        error = ""

        if request.POST.get("name"):
            new_time.name = request.POST['name']
        else:
            error += 'Must supply a name. '

        if request.POST.get("start"):
            new_time.start = datetime.strptime(request.POST['start'], '%H:%M').time()
        else:
            error += 'Must supply a start time. '

        if request.POST.get('event'):
            try:
                n_event = Event.objects.get(id=int(request.POST['event']))
                new_time.event = n_event
            except Event.DoesNotExist:
                error += 'Not a valid event id. '

        else:
            error += 'Must supply an event id. '

        if error == "":
            new_time.save()
            return JsonResponse({
                'result': 'success',
                'time': {
                    'id': new_time.id,
                    'name': new_time.name,
                    'event': new_time.event.id,
                    'start': new_time.start.isoformat(),
                    'display_start': new_time.start.strftime('%I:%M %p')
                }
            })

        else:
            return JsonResponse({'result': 'fail', 'message': error})


def assignments_view(request):
    if request.user.is_superuser:
        events = Event.objects.all()
        event_dicts = []
        for event in events:
            event_dicts.append({
                'id': event.id,
                'name': event.name,
                'date': event.date.isoformat(),
                'location': event.location
            })

        judges = Judge.objects.all()
        judge_dicts = []
        for judge in judges:
            judge_dicts.append({
                'first_name': judge.user.first_name,
                'last_name': judge.user.last_name,
                'room': judge.room,
                'event': judge.event.id,
            })

        students = Student.objects.all()
        student_dicts = []
        for student in students:
            student_dicts.append({
                'first_name': student.first_name,
                'last_name': student.last_name,
                'event': student.event.id,
                'rank': student.rank
            })

        times = Time.objects.all()
        time_dicts = []
        for time in times:
            time_dicts.append({
                'event': time.event.id,
                'start': time.start.isoformat(),
                'display_start': time.start.strftime('%I:%M %p'),
            })

        occurrences = Occurrence.objects.all()
        occurrence_dicts = []
        for occ in occurrences:
            occurrence_dicts.append({
                'judge': occ.judge.id,
                'student': occ.student.id,
                'time': occ.time.id,
                'type': occ.type
            })

        urls = {}

        data = {
            'events': event_dicts,
            'judges': judge_dicts,
            'students': student_dicts,
            'times': time_dicts,
            'occurrences': occurrence_dicts,
            'urls': urls
        }

        return render(request, 'grader/time_assignments.html', context={'data': json.dumps(data)})
