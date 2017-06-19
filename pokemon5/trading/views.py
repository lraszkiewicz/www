from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.http import HttpResponseForbidden

def main(request):
    return render(request, 'main.html', locals())

@csrf_exempt
@require_POST
def tradeAPI(request):
    return HttpResponseForbidden('TODO')