#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import subprocess
import time
import datetime


from django.core.management.base import BaseCommand, CommandError

from ubskin_web_django.member import models as member_models

# from ubskin_web_django.common import sched

INTERPRETER = "/usr/bin/python"



class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)
    def handle(self, *args, **options):
        user_order = member_models.UserOrder
        time_delta = datetime.timedelta(days=10)
        today = datetime.datetime.now()
        expire_date = today-time_delta
        time_time = time.mktime(expire_date.timetuple())
        user_order.objects.filter(create_time__lt=int(time_time), order_status='shipped').update(
            order_status = 'received'
        )
