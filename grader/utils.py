from django.core.files import File
from django.contrib.auth.models import User
from .models import SpeechScore, InterviewScore, Event
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

def export_scores(response, event_id, detailed):
    speech_scores = []
    interview_scores = []
    overall_scores = []
    event = Event.objects.get(id=event_id)
    judges = Judge.objects.filter(event=event)
    csv_writer = csv.writer(response)

    if detailed:
        speech_fieldnames = ['Student ID', 'Student', 'Judge', 'Room', 'Speech Development',
                             'Effectiveness', 'Correctness', 'Appropriateness',
                             'Speech Value', 'Voice', 'Non-Verbal', 'Content',
                             'Delivery', 'Overall Effectiveness', 'Time Penalty', 'Overall']

        interview_fieldnames = ['Student ID', 'Student', 'Judge', 'Room', 'Voice',
                                'Language Usage', 'Interpersonal Skills', 'Non-Verbal Language',
                                'Manner', 'Listening Skills', 'Answering Skills',
                                'Responses', 'Overall Effectiveness', 'Appearance', 'Overall']

        csv_writer.writerow(["Speeches"])
        csv_writer.writerow(speech_fieldnames)
        for speech in SpeechScore.objects.filter(grader=judges):
            csv_writer.writerow([
                speech.student_id,
                speech.student_first_name + ' ' + speech.student_last_name,
                speech.grader.first_name + ' ' + speech.grader.last_name,
                Judge.objects.get(username=speech.grader.username).room,
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

        csv_writer.writerow(["Interviews"])
        csv_writer.writerow(interview_fieldnames)
        for interview in InterviewScore.objects.filter(grader=judges):
            csv_writer.writerow([
                interview.student_id,
                interview.student_first_name + ' ' + interview.student_last_name,
                interview.grader.first_name + ' ' + interview.grader.last_name,
                Judge.objects.get(username=interview.grader.username).room,
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

    else:
        student_ids_speeches = SpeechScore.objects.filter(grader=judges).values_list('student_id', flat=True).distinct()
        student_ids_interview = InterviewScore.objects.filter(grader=judges).values_list('student_id', flat=True).distinct()
        for id in student_ids_speeches:
            scores = SpeechScore.objects.filter(student_id=id)
            sum = 0
            for score in scores:
                sum += score.overall_score
            average = round(float(sum)/len(scores), 2)
            speech_scores.append((id,
                                  scores.first().student_first_name + ' ' +
                                    scores.first().student_last_name,
                                  average))

        for id in student_ids_interview:
            scores = InterviewScore.objects.filter(student_id=id)
            sum = 0
            for score in scores:
                sum += score.overall_score
            average = round(float(sum)/len(scores), 2)
            interview_scores.append((id,
                                  scores.first().student_first_name + ' ' +
                                    scores.first().student_last_name,
                                  average))

        s_success = []
        i_success = []

        for s_score in speech_scores:
            for i_score in interview_scores:
                if i_score[0] == s_score[0]:
                    overall_scores.append((s_score[0],
                                           s_score[1],
                                           s_score[2],
                                           i_score[2]))
                    i_success.append(i_score)
                    s_success.append(s_score)

        print(s_success)
        print(speech_scores)

        for s_score in list(set(speech_scores)-set(s_success)):
            overall_scores.append((s_score[0],
                                   s_score[1],
                                   s_score[2],
                                   "No Interview Score"))

        for i_score in list(set(interview_scores)-set(i_success)):
            overall_scores.append((i_score[0],
                                   i_score[1],
                                   "No Speech Score",
                                   i_score[2]))

        fieldnames = ['Student ID', 'Name', 'Speech', 'Interview']
        csv_writer.writerow(fieldnames)
        for score in overall_scores:
            csv_writer.writerow(score)

    return response
