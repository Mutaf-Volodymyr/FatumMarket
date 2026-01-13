from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.products.models import Brand


def brand_list_view(request):
    """Показывает список всех брендов"""
    brands = Brand.objects.all().order_by('name')
    
    # Пагинация
    page = request.GET.get('page', 1)
    paginator = Paginator(brands, 20)  # 20 брендов на странице
    try:
        brands_page = paginator.page(page)
    except PageNotAnInteger:
        brands_page = paginator.page(1)
    except EmptyPage:
        brands_page = paginator.page(paginator.num_pages)
    
    return render(request, 'market/brand_list.html', {
        'brands': brands_page,
    })


