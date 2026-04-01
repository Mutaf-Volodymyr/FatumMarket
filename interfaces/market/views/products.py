from collections import defaultdict
from decimal import Decimal

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from apps.products.domain.product_filters import ProductFiltersBuilder
from apps.products.models import Brand, Category, Product, SpecificationValue
from interfaces.market.cart_utils import annotate_product_in_carts_by_request


def _get_pagination_url(request, page):
    """Строит URL для пагинации с сохранением всех параметров фильтров"""
    params = request.GET.copy()
    if page:
        params["page"] = page
    else:
        params.pop("page", None)
    return request.path + ("?" + params.urlencode() if params else "")


def product_list_view(request):
    """Product list page with category and brand filtering and pagination"""
    category_id = request.GET.get("category")
    brand_id = request.GET.get("brand")
    search_query = request.GET.get("search", "")
    page = request.GET.get("page", 1)

    # Базовый queryset (без фильтров по спецификациям и цене)
    products = (
        Product.objects.filter(is_active=True)
        .select_related("category", "brand")
        .prefetch_related("images")
    )

    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            # Get all descendants categories
            categories = category.get_descendants(include_self=True)
            products = products.filter(category__in=categories)
        except Category.DoesNotExist:
            pass

    if brand_id:
        try:
            brand = Brand.objects.get(id=brand_id)
            products = products.filter(brand=brand)
        except Brand.DoesNotExist:
            pass

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Build filters from base queryset (before applying filter parameters and pagination)
    filters_builder = ProductFiltersBuilder(products)
    filters = filters_builder.build_filters()

    # Get selected filters from request
    selected_specifications = request.GET.getlist("spec")
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort_by = request.GET.get("sort", "")

    # Apply filters
    if selected_specifications:
        # Конвертируем в int для фильтрации, фильтруем пустые значения
        spec_ids = []
        for spec_id in selected_specifications:
            try:
                spec_ids.append(int(spec_id))
            except (ValueError, TypeError):
                continue

        if spec_ids:
            # Фильтруем товары, которые имеют ВСЕ выбранные спецификации (AND логика)
            # Группируем спецификации по названию (specification_name)
            spec_values = SpecificationValue.objects.filter(id__in=spec_ids).select_related(
                "specification_name"
            )

            # Группируем по specification_name_id
            spec_groups = defaultdict(list)
            for sv in spec_values:
                spec_groups[sv.specification_name_id].append(sv.id)

            # Применяем фильтрацию: товар должен иметь значение из каждой группы
            # Внутри группы может быть OR, если выбрано несколько значений одной спецификации
            for name_id, value_ids in spec_groups.items():
                products = products.filter(
                    product_specification__specification_name_id=name_id,
                    product_specification__specification_value_id__in=value_ids,
                )

            products = products.distinct()

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except (ValueError, TypeError):
            pass

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except (ValueError, TypeError):
            pass

    # Apply sorting
    if sort_by == "price_asc":
        products = products.order_by("price")
    elif sort_by == "price_desc":
        products = products.order_by("-price")
    elif sort_by == "newest":
        products = products.order_by("-created_at")
    elif sort_by == "oldest":
        products = products.order_by("created_at")
    else:
        # Default sorting (by creation date, newest first)
        products = products.order_by("-created_at")

    products = annotate_product_in_carts_by_request(request=request, product=products)

    # Pagination (after all filters and sorting)
    total_products_count = products.count()
    paginator = Paginator(products, 12)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Get root categories (categories without parent) for tree display
    root_categories = Category.objects.filter(parent=None).order_by("position")
    # Get all brands
    brands = Brand.objects.all().order_by("name")

    return render(
        request,
        "market/product_list.html",
        {
            "products": products_page,
            "total_products_count": total_products_count,
            "root_categories": root_categories,
            "brands": brands,
            "filters": filters,
            "selected_category_id": category_id,
            "selected_brand_id": brand_id,
            "selected_specifications": selected_specifications,
            "selected_min_price": min_price,
            "selected_max_price": max_price,
            "search_query": search_query,
            "selected_sort": sort_by,
        },
    )


def product_detail_view(request, slug):
    """Product detail page"""
    product_queryset = (
        Product.objects.select_related("category", "brand")
        .prefetch_related(
            "images",
            "product_specification__specification_value",
            "product_specification__specification_name",
        )
        .filter(is_active=True)
    )

    # Annotate with cart status if user is authenticated
    product_queryset = annotate_product_in_carts_by_request(
        request=request, product=product_queryset
    )

    product = get_object_or_404(product_queryset, slug=slug)

    # Get related products from same category
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(
        id=product.id
    )[:4]

    return render(
        request,
        "market/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )
