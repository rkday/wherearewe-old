import itertools
from utils import get_constituency_list

constituencies = get_constituency_list(open("constituencies.kml"))
colour_cycle = itertools.cycle(["#ff0000", "#00ff00", "#0000ff"])

print "var constituency_polygons = {"
for name in sorted(constituencies.keys()):
    simple_constit = constituencies[name].simplify(0.01)
    print """"{0}": {4}
        'exterior_coordinates': {2},
        'interior_coordinates': {3}{5},
    """.format(
            name, 
            colour_cycle.next(), 
            [[x, y] for x,y in list(simple_constit.exterior.coords)], 
            [[[x,y] for x,y in list(i.coords)] for i in list(simple_constit.interiors)], 
            '{', 
            '}')
print "}"
