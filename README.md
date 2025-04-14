# SnipBox - Short Note Saving App
SnipBox is a Django Rest Framework-based backend API for saving short snippets, tagging them, and retrieving based on users.

## Features
- User authentication via JWT
- Create, update, delete, and view your own snippets
- Tags to group snippets
- Tag reuse (no duplicate titles)
- Simple API structure with DRF
- Docker support (optional)
- Sending basic email is implemented (update smtp user host and password in settings.py for working in local)

IMPORTANT!
For running project in your local, sign up into mailtrap and get credentials for Django , and please update in settings.py file for proper working , 
otherwise send mail error will occur. Due to security purpose I hided my data from settings.py file.

# settings.py 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER = 'xxxxxxxxxxxxxxxxxxx'  #update proper host user
EMAIL_HOST_PASSWORD = 'xxxxxxxxxxxxx' #update proper host password

Please update  EMAIL_HOST_USER and EMAIL_HOST_PASSWORD


## Installation Instructions

git clone https://github.com/freeeda22/snipbox.git

cd snipbox

python -m venv venv

source venv/bin/activate  # or `venv\Scripts\activate` on Windows

pip install -r requirements.txt

Please update  EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py from a mailtrap account

Run the server:
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


Dockerfile Composing Command : 

docker-compose up --build

