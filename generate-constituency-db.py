#!/usr/bin/python
import sys
sys.path.append("./django/wherearewe")
import wherearewe.settings
from django.core.management import setup_environ
setup_environ(wherearewe.settings)
import waw_app.models
from utils import get_constituency_list
import csv

with open("constituency_population.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        waw_app.models.Constituency.objects.create(name=row['Constituency'], population=int(row['Population'].replace(",",""))).save()
