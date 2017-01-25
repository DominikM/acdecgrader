from django.test import TestCase, Client
from .views import *
from .models import *
import datetime
import json


class GraderViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.event1 = Event.objects.create(
            name="Event1",
            date=datetime.date(2000, 1, 1),
            location="Stanford"
        )
        cls.event2 = Event.objects.create(
            name="Event2",
            date=datetime.date(2000, 1, 2),
            location="MIT"
        )
        cls.judge1 = Judge.objects.create_user(
            username="bobdylan",
            email="bob@dylan.com",
            password="12345",
            first_name="Bob",
            last_name="Dylan",
            room="1",
            event=cls.event1
        )
        cls.judge2 = Judge.objects.create_user(
            username="jeffbridges",
            email="jeff@bridges.com",
            password='12345',
            first_name='Jeff',
            last_name='Bridges',
            room='1',
            event=cls.event2
        )
        cls.student1 = Student.objects.create(
            first_name="Bob",
            last_name="Bitdiddle",
            event=cls.event1,
            rank=0
        )
        cls.student2 = Student.objects.create(
            first_name="Harry",
            last_name="Potter",
            event=cls.event2,
            rank=2
        )
        cls.admin = User.objects.create_superuser(
            'dominikm',
            'dominikm@mit.edu',
            '12345'
        )

    def setUp(self):
        self.client = Client()

    def test_student_panel_view(self):
        self.client.force_login(self.admin)
        response = self.client.get('/students/')
        student_json = response.context['data']

        actual_student_json = {
            'events': [
                {'id': self.event1.id, 'name': self.event1.name, 'date': self.event1.date.strftime('%Y-%m-%d'), 'location': self.event1.location},
                {'id': self.event2.id, 'name': self.event2.name, 'date': self.event2.date.strftime('%Y-%m-%d'), 'location': self.event2.location},
            ],
            'students': [
                {'id': self.student1.id, 'event_id': self.student1.event.id,
                 'first_name': self.student1.first_name, 'last_name': self.student1.last_name, 'rank': self.student1.rank},
                {'id': self.student2.id, 'event_id': self.student2.event.id,
                 'first_name': self.student2.first_name, 'last_name': self.student2.last_name, 'rank': self.student2.rank},
            ],
            'urls': {
                'delete': reverse('student_delete'),
                'edit': reverse('student_edit')
            }
        }

        actual_student_json = json.dumps(actual_student_json)

        self.assertEqual(student_json, actual_student_json)

    def test_delete_student(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            '/students/delete/',
            {'id': self.student1.id}
        )

        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Student.DoesNotExist):
            Student.objects.get(id=self.student1.id)

    def test_edit_student(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            '/students/edit/',
            {
                'id': self.student1.id,
                'first_name': 'Jeff',
                'last_name': 'La',
                'rank': 1,
                'event': self.event2.id
            }
        )

        updated_student = Student.objects.get(id=self.student1.id)

        self.assertEqual(updated_student.first_name, 'Jeff')
        self.assertEqual(updated_student.last_name, 'La')
        self.assertEqual(updated_student.rank, 1)
        self.assertEqual(updated_student.event, self.event2)


    def test_student_create(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            '/students/create/',
            {
                'first_name': 'Bob',
                'last_name': 'Bitdiddle',
                'rank': 2,
                'event': self.event2.id
            }
        )

        if self.assertEqual(response.status_code, 200) and \
            self.assertEqual(response.POST['result'], 'success'):

            new_student = Student.objects.get(last_name='Bitdiddle', first_name='Bob')

            self.assertEqual(new_student.first_name, 'Bob')
            self.assertEqual(new_student.last_name, 'Bitdiddle')
            self.assertEqual(new_student.rank, 2)
            self.assertEqual(new_student.event, self.event2)

