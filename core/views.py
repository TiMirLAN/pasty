# -*- coding: utf-8 -*-

from django.http import HttpResponse
from core.models import Pasty

from django.views.generic.detail import DetailView


class IndexView(DetailView):
    template_name = 'base.html'
    model = Pasty
    context_object_name = 'default_pasty'

    def get_object(self, queryset=None):
        return self.model.objects.get_random()
index = IndexView.as_view()

def one(request):
    return HttpResponse(
        Pasty.objects.get_random().json_serialize(),
        mimetype='application/json'
    )



