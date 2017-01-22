import os, sys
import django
import csv
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acdec.settings')
django.setup()

from grader.models import Student, Event

event = Event.objects.create(
    name="Massachusetts State",
    date = date(month=1,day=1,year=2018),
    location = "MIT"
)

with open('sample_data.csv', 'r+') as sample_data_file:
    students = []
    student_reader = csv.reader(sample_data_file)
    for row in student_reader:
        students.append(
            Student(
                first_name=row[0],
                last_name=row[1],
                rank=row[2],
                event=event
            )
        )

    Student.objects.bulk_create(students)