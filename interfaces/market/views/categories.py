from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.products.models import Category, Product


def category_list_view(request, slug=None):
    """Показывает список подкатегорий категории или список категорий верхнего уровня"""
    if slug:
        category = get_object_or_404(Category, slug=slug)
        # Проверяем, есть ли подкатегории
        subcategories = category.get_children().order_by('position')
        if subcategories.exists():
            return render(request, 'market/category_list.html', {
                'parent_category': category,
                'categories': subcategories,
            })
        else:
            # Если подкатегорий нет, перенаправляем на страницу с товарами
            return redirect(f"{request.build_absolute_uri('/')}?category={category.id}")
    else:
        # Показываем категории верхнего уровня
        root_categories = Category.objects.filter(parent=None).order_by('position')
        return render(request, 'market/category_list.html', {
            'parent_category': None,
            'categories': root_categories,
        })

