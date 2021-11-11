from django.shortcuts import render
from django.http import HttpResponse
from . import covid

def index(request):
    context = {}
    if request.method == 'POST':
        c = covid.Covid_Ontario_Active_Case()
        line_graph = c.get_line_graph()
        heatmap = c.get_heatmap()
        context['line_graph'] = line_graph
        context['heatmap'] = heatmap
        context['request_method'] = 'post_method'
    else:
        context['request_method'] = 'get_method'
    return render(request, "index.html", context)
