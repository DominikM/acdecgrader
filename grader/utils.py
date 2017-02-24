from django.core.files import File
from django.contrib.auth.models import User
from .models import SpeechScore, InterviewScore, Event, Student, Occurrence
from collections import defaultdict
import csv
from .models import Judge
import io
import string
import random


def get_unique_username(username):
    num = 1
    tmp_username = username
    while User.objects.filter(username=tmp_username).count():
        tmp_username = username + str(num)

    return tmp_username

def export_scores(response, event_id, type):
    speech_scores = []
    interview_scores = []
    overall_scores = []
    event = Event.objects.get(id=event_id)
    speech_scores = SpeechScore.objects.filter(event=event)
    interview_scores = InterviewScore.objects.filter(event=event)
    students = Student.objects.filter(event=event)
    csv_writer = csv.writer(response)

    students_and_speech_scores = defaultdict(list)
    students_and_interview_scores = defaultdict(list)

    # we need to collect all scores (including the ones that aren't associated with a time)
    for speech in speech_scores:
        try:
            student = speech.occurrence.student
        except Occurrence.DoesNotExist:
            student = Student.objects.get(comp_id=speech.student_id)
        students_and_speech_scores[student].append(speech)

    for interview in interview_scores:
        try:
            student = interview.occurrence.student
        except Occurrence.DoesNotExist:
            student = Student.objects.get(comp_id=interview.student_id)
        students_and_interview_scores[student].append(interview)

    if type is 0: # then it is refined

        # calculate average speech scores
        students_average_speech = defaultdict(int)

        for student, speeches in students_and_speech_scores.items():
            if len(speeches):
                students_average_speech[student] = sum([speech.overall_score for speech in speeches])/len(speeches)

        # calculate average interview scores
        students_average_interview = defaultdict(int)

        for student, interviews in students_and_interview_scores.items():
            if len(speeches):
                students_average_interview[student] = sum([interview.overall_score for interview in interviews])/len(interviews)

        csv_writer.writerow(['Student ID', 'Student', 'Overall Speech', 'Overall Interview'])

        for student in Student.objects.all():
            csv_writer.writerow([
                student.comp_id,
                student.first_name + ' ' + student.last_name,
                students_average_speech[student],
                students_average_interview[student]
            ])

    if type is 1:  # speech
        speech_fieldnames = ['Student ID', 'Student', 'Judge', 'Room', 'Speech Development',
                             'Effectiveness', 'Correctness', 'Appropriateness',
                             'Speech Value', 'Voice', 'Non-Verbal', 'Content',
                             'Delivery', 'Overall Effectiveness', 'Time Penalty', 'Overall']

        csv_writer.writerow(speech_fieldnames)
        for speech in speech_scores:
            try:
                student = speech.occurrence.student
            except Occurrence.DoesNotExist:
                student = Student.objects.get(comp_id=speech.student_id)

            csv_writer.writerow([
                student.comp_id,
                student.first_name + ' ' + student.last_name,
                speech.grader.first_name + ' ' + speech.grader.last_name,
                speech.grader.judge.room,
                speech.development_score,
                speech.effectiveness_score,
                speech.correctness_score,
                speech.appropriateness_score,
                speech.value_score,
                speech.voice_score,
                speech.nonverbal_score,
                speech.content_score,
                speech.delivery_score,
                speech.overall_effect,
                speech.time_violations,
                speech.overall_score
            ])

    if type is 2:  # interview
        interview_fieldnames = ['Student ID', 'Student', 'Judge', 'Room', 'Voice',
                                'Language Usage', 'Interpersonal Skills', 'Non-Verbal Language',
                                'Manner', 'Listening Skills', 'Answering Skills',
                                'Responses', 'Overall Effectiveness', 'Appearance', 'Overall']

        csv_writer.writerow(interview_fieldnames)
        for interview in interview_scores:
            try:
                student = interview.occurrence.student
            except Occurrence.DoesNotExist:
                student = Student.objects.get(comp_id=interview.student_id)

            csv_writer.writerow([
                student.comp_id,
                student.first_name + ' ' + student.last_name,
                interview.grader.first_name + ' ' + interview.grader.last_name,
                interview.grader.judge.room,
                interview.voice_score,
                interview.language_score,
                interview.interpersonal_score,
                interview.nonverbal_score,
                interview.manner_score,
                interview.listening_score,
                interview.answering_score,
                interview.response_score,
                interview.overall_effect,
                interview.appearance_score,
                interview.overall_score
            ])

    return response
