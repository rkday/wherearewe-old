from django.db import models

class Map(models.Model):
    name = models.CharField(max_length=30)
    postcodes = models.ManyToManyField('Postcode')
    constituencies = models.ManyToManyField('ConstituencyCount')

class Postcode(models.Model):
    postcode = models.CharField(max_length=30)
    constituency = models.ForeignKey('Constituency')

# Constituencies have some information which relates to them specifically -
# e.g. population - and some which relates only to their representation on a
# particular map, e.g. count of postcodes in that constituency. We divide these
# separate concepts into the 'Constituency' and 'ConstituencyCount' models.

class Constituency(models.Model):
    name = models.CharField(max_length=200)
    population = models.IntegerField()

class ConstituencyCount(models.Model):
    constituency = models.ForeignKey('Constituency')
    count = models.IntegerField()


