from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import django.db
from waw_app import models
import time
from django.db import transaction

def input_form(request):
        t = get_template('input_form.html')
        html = t.render(RequestContext(request, {}))
        return HttpResponse(html)

def hello(request):
        return HttpResponse("Hello world")

@transaction.commit_on_success()
def create_map(request):
    basetime = time.time()
    timings = {"line manipulation": 0, "getting constituency": 0, "getting count": 0, "saving count": 0}
    my_map = models.Map.objects.create(name=request.POST['mapname'])
    my_map.save()
    timings['creating map'] = time.time() - basetime
    successes, failures = 0, 0
    p_objs = models.Postcode.objects
    cc_objs = models.ConstituencyCount.objects
    if 'postcodes' in request.POST and request.POST['postcodes']:
        postcodes = [line.replace(" ", "").upper() for line in request.POST['postcodes'].splitlines()]
        for line in postcodes:
            local_basetime = time.time()
            if len(line) == 0:
                continue
            timings["line manipulation"] += time.time() - local_basetime
            local_basetime = time.time()
            try:
                constit = p_objs.filter(postcode__istartswith=line)[0].constituency_id
            except IndexError:
                failures += 1
                continue
            timings["getting constituency"] += time.time() - local_basetime
            local_basetime = time.time()
            constit_count_qs = my_map.constituencycount_set.filter(constituency_id__exact=constit)
            if constit_count_qs:
                constit_count = constit_count_qs[0]
            else:
                constit_count = cc_objs.create(map=my_map, constituency_id=constit, count=0)
            timings["getting count"] += time.time() - local_basetime
            local_basetime = time.time()
            constit_count.count += 1
            constit_count.save()
            timings["saving count"] += time.time() - local_basetime
            successes += 1
        #insert_all_postcodes.delay(request.POST['mapname'], postcodes)
        #increment_constituency_counts.delay(request.POST['mapname'], constituencies)
    return HttpResponse("%d postcodes added, %d failures\n%f\n%s\n" % (successes, failures, time.time() - basetime, str(timings)), "text/plain")

def produce_map(request, mapname):
    colours = ColourCoordinator.new()
    constituency_hash = {}
    response = "var constituency_info = {"
    my_map = models.Map.objects.get(name=mapname)
    first = 1
    for constituency in models.Constituency.objects.all():
        if not first:
            response += ",\n"
        else:
            first = 0
        response += "'{0}' {{'text': '{0}',".format(constituency.name)
        try:
            count = my_map.constituencycount_set.get(constituency=constituency).count
        except:
            count = 0
        response += "'count': {0},".format(count)
        response += "'colour': '{0}' }}".format(_get_colour_from_count(count))
    response += "}"
    return HttpResponse(response, "text/javascript")

def _get_colour_from_count(count):
    colours = get_colour_mapping
