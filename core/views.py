# -*- coding: utf-8 -*-

import os
from django.http import HttpResponse, HttpResponseRedirect
from core.models import Pasty
#from core.models import Source
#from core.sync import sync_rss_source

from django.views.generic.detail import DetailView


class IndexView(DetailView):
    template_name = 'base.html'
    model = Pasty
    context_object_name = 'default_pasty'

    def get_object(self, queryset=None):
        return self.model.rnd()
index = IndexView.as_view()


# FIXME почему вообще шаблон храниться так?
# FIXME кривой JS, нет 'var', использование XMLHttpRequest хотя целевая платформа не указана, сихронные запросы
# def home(request):
#     return HttpResponse(u'''
# <html>
#     <head>
#         <title>Пирожки :-)</title>
#         <link rel="stylesheet" type="text/css" href="/static/core/style.css" />
#     </head>
#     <body class="box">
#         <a class="nav sources" href="/sources">Источники &rarr;</a>
#         <div id="wrapper"></div>
#         <script type="text/javascript">
#             pasty = function() {
#                 xmlhttp = new XMLHttpRequest();
#                 xmlhttp.open("GET", "/one", false);
#                 xmlhttp.send();
#                 document.getElementById('wrapper').innerHTML = xmlhttp.responseText;
#             }
#             pasty();
#             setInterval(pasty, 15000);
#         </script>
#     </body>
# </html>
#     ''')

def one(request):
    return HttpResponse(
        Pasty.rnd().json_serialize(),
        mimetype='application/json'
    )
    # p = Pasty.rnd()
    # if p:
    # FIXME почему бы не передать p в контекст целиком?
    #     context = {'text': p.text, 'source': p.source, 'title': p.source_title()}
    #     return render(request, 'core/pasty.html', context)
    # else:
    #     return HttpResponse(u'<div class="box pasty">Нету пирожков :-(</div>')

# FIXME Зачем вообще 2 вьюшки на обработку формы. Form + FormView было бы лучше
# FIXME почему сдесь, а не в админке
# FIXME почему нет наследования шаблонов, если уж стили одинаковые.
# def sources(request):
#     sources = Source.objects.all()
#     context = { 'sources': sources }
#     return render(request, 'core/sync.html', context)
#
# def sync(request):
#     sources_id = request.POST.getlist('source')
#     if sources_id:
#         for src_id in sources_id:
#             source = Source.objects.get(pk=src_id)
#             sync_rss_source(source)
#     return HttpResponseRedirect(reverse('sources'))



