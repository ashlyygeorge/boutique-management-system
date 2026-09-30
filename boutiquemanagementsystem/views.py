from django.shortcuts import render
from store.models import productdetails


# Create your views here.
def index(request):
    products = productdetails.objects.all().order_by('-id')[:6]

    return render(request, 'index.html', {
        'products': products
    })