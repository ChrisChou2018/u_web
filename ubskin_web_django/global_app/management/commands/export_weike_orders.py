#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import os
import logging
import subprocess

from ubskin_web_django.common import update_out_order_data

INTERPRETER = "/usr/bin/python"



class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)
    def handle(self, *args, **options):
        update_out_order_data.export_weike_orders()