# Academic Decathlon Speech and Interview Grader

This tool is used to allow judges to remotely input the scores for competitor's speech/impromptu and interview scores. This tool has been used at the Connecticut and Massachusetts State competitions.

## Setup 

1. Create file `acdec/local_settings.py` and populate with a `SECRET_KEY`
2. Run `python manage.py makemigrations grader`
3. Run `python manage.py migrate`
4. (Optional) Create a superuser `python manage.py createsuperuser`
5. Install dependencies for semantic-ui `npm install semantic-ui`
6. Run `python manage.py runserver`
