"""Apcheduler imports"""
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution


"""My imports"""
from django import db
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import datetime

from news.models import Post, Category


logger = logging.getLogger(__name__)


def my_job():
    today_date = datetime.datetime.now()
    week_ago_date = today_date - datetime.timedelta(weeks=1)

    categories = Category.objects.all()

    for category in categories:
        subscribers_list = category.subscriber.all()
        post_list = Post.objects.filter(category=category, time__range=(week_ago_date, today_date))

        for subscriber in subscribers_list:
            html_content = render_to_string(
                'news/send_notify_weekly.html',
                {
                    'post_list': post_list,
                    'category': category,
                    'username':subscriber.username
                }
            )

            email_text = EmailMultiAlternatives(
                subject='Еженедельная рассылка новостей',
                body='123',
                from_email='nedgalkin@gmail.com',
                to=[subscriber.email],
            )
            email_text.attach_alternative(html_content, "text/html")
            email_text.send()

def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="*/5"),  # Every saturday
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
