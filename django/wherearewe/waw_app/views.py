from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render_to_response

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
    if 'q' in request.POST and request.POST['q']:
        for line in request.POST['q'].splitlines():
            try:
                constit = models.Postcode.objects.filter(postcode__startswith=line)[0].constituency
            except IndexError:
                errors += 1
                continue
            constit_count_qs = my_map.constituencies.get(constituency=constit)
            if constit_count_qs:
                constit_count = constit_count_qs[0]
            else:
                constit_count = my_map.constituencies.create(constituency=constit, count=0)
            constit_count.count += 1
            constit_count.save()
            successes += 1
    return HttpResponse("%d postcodes added, %d failures" % (successes, failures), "text/plain")
