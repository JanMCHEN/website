from celery import Celery
from django.core.mail import send_mail
from .settings import *
import django
import os

app = Celery('celery_tasks.task', broker=BROKER)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celery_tasks.settings')
django.setup()


@app.task
def send_email(email, username, token):
    url = 'http://127.0.0.1:8000/active/?token=%s' % token
    h_message = '<h1>{2},欢迎注册，请在两小时内点击下面的激活链接,未听说过请忽略</h1></br><a href={0}>{1}</a>'.format(url, token, username)
    try:
        send_mail(EMAIL_SUBJECT, message='', from_email=EMAIL_FROM, html_message=h_message, recipient_list=[email])
    except:
        pass

