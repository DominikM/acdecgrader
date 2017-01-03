from django.db import models
from django.contrib.auth.models import User


class Judge(User):
    room = models.CharField(null=True, max_length=10)
    event = models.ForeignKey('Event', null=True)

    class Meta:
        verbose_name = 'Judge'
        verbose_name_plural = 'Judges'

    def __str__(self):
        return self.first_name + " " + self.last_name


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    event = models.ForeignKey('Event')
    # TODO: how to point a student at a specific time slot and at a judge?

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return self.first_name + " " + self.last_name


grading_system = (
    (0, "0 - Poor"),
    (100, "1 - Poor"),
    (200, "2 - Poor"),
    (300, "3 - Fair"),
    (400, "4 - Fair"),
    (500, "5 - Good"),
    (600, "6 - Good"),
    (700, "7 - Very Good"),
    (800, "8 - Very Good"),
    (900, "9 - Excellent"),
    (1000, "10 - Excellent"),
)


class Score(models.Model):
    student_id = models.IntegerField()
    student_first_name = models.CharField(max_length=30)
    student_last_name = models.CharField(max_length=30)
    overall_score = models.IntegerField(blank=True)
    grader = models.ForeignKey(User)


class SpeechScore(Score):
    development_score = models.IntegerField(choices=grading_system)
    effectiveness_score = models.IntegerField(choices=grading_system)
    correctness_score = models.IntegerField(choices=grading_system)
    appropriateness_score = models.IntegerField(choices=grading_system)
    value_score = models.IntegerField(choices=grading_system)
    voice_score = models.IntegerField(choices=grading_system)
    nonverbal_score = models.IntegerField(choices=grading_system)

    content_score = models.IntegerField(choices=grading_system)
    delivery_score = models.IntegerField(choices=grading_system)
    overall_effect = models.IntegerField(choices=grading_system)

    time_violations = models.IntegerField(choices=(
        (-100, "Both Speeches"),
        (-70, "Prepared Only"),
        (-30, "Impromptu Only"),
        (0, "No Penalty")
    ))

    def save(self, *args, **kwargs):
        overall = (self.development_score*.1 + self.effectiveness_score*.1 +
                   self.correctness_score*.1 +
                   self.appropriateness_score*.1 + self.value_score*.1 +
                   self.voice_score*.1 + self.nonverbal_score*.1 +
                   self.content_score*.1 + self.delivery_score*.1 +
                   self.overall_effect*.1 + self.time_violations)
        self.overall_score = overall
        super(SpeechScore, self).save(*args, **kwargs)

    def __str__(self):
        return self.student_first_name + ' ' + self.student_last_name + "'s Speech judged by " + str(self.grader.judge)


class InterviewScore(Score):
    voice_score = models.IntegerField(choices=grading_system)
    language_score = models.IntegerField(choices=grading_system)
    interpersonal_score = models.IntegerField(choices=grading_system)
    nonverbal_score = models.IntegerField(choices=grading_system)
    manner_score = models.IntegerField(choices=grading_system)
    listening_score = models.IntegerField(choices=grading_system)
    answering_score = models.IntegerField(choices=grading_system)
    response_score = models.IntegerField(choices=grading_system)
    overall_effect = models.IntegerField(choices=grading_system)
    appearance_score = models.IntegerField(choices=grading_system)

    def save(self, *args, **kwargs):
        overall = (
            self.voice_score*.1 + self.language_score*.1 + self.interpersonal_score*.1 +
            self.nonverbal_score*.1 + self.manner_score*.1 + self.listening_score*.1 +
            self.answering_score*.1 + self.response_score*.1 + self.overall_effect*.1 +
            self.appearance_score*.1
        )
        self.overall_score = overall
        super(InterviewScore, self).save(*args, **kwargs)

    def __str__(self):
        return self.student_first_name + ' ' + self.student_last_name + "'s Interview judged by " + str(self.grader.judge)


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Room(models.Model):
    location = models.CharField(max_length=20)


