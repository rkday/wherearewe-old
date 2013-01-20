from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from waw_app import models

def input_form(request):
        t = get_template('input_form.html')
        html = t.render(RequestContext(request, {}))
        return HttpResponse(html)

def hello(request):
        return HttpResponse("Hello world")

def create_map(request):
    my_map = models.Map.objects.create(name=request.POST['mapname'])
    my_map.save()
    successes, failures = 0, 0
    if 'postcodes' in request.POST and request.POST['postcodes']:
        for line in request.POST['postcodes'].splitlines():
            try:
                constit = models.Postcode.objects.filter(postcode__startswith=line)[0].constituency
            except IndexError:
                errors += 1
                continue
            constit_count_qs = my_map.constituencycount_set.filter(constituency__exact=constit)
            if constit_count_qs:
                constit_count = constit_count_qs[0]
            else:
                constit_count = models.ConstituencyCount.objects.create(map=my_map, constituency=constit, count=0)
            constit_count.count += 1
            constit_count.save()
            successes += 1
    return HttpResponse("%d postcodes added, %d failures" % (successes, failures), "text/plain")

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
