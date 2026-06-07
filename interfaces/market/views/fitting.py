from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.delivery.models import PickupPlace
from apps.fitting.domain import DraftFittingException, DraftFittingService
from apps.users.domain.customer_service import CustomerService
from apps.users.domain.schema import UserSchema
from base.micro_domains import FutureDatetime


def fitting_view(request):
    service = DraftFittingService(
        session_key=request.session.session_key,
        user=request.user,
    )

    products = service.get_draft_fitting_products()
    showrooms = PickupPlace.objects.filter(show_room=True).order_by("position")
    user = request.user if request.user.is_authenticated else None

    return render(
        request,
        "market/fitting.html",
        {
            "products": products,
            "showrooms": showrooms,
            "user": user,
        },
    )


@require_POST
def fitting_add_view(request, product_id):
    service = DraftFittingService(
        session_key=request.session.session_key,
        user=request.user,
    )

    service.add_product(product_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.http import JsonResponse

        fitting_count = service.get_draft_fitting_products().count()
        return JsonResponse({"success": True, "fitting_count": fitting_count})

    referer = request.META.get("HTTP_REFERER")
    return redirect(referer or "market:home")


@require_POST
def fitting_confirm_view(request):
    try:
        date_str = request.POST.get("date", "")
        if not date_str:
            raise DraftFittingException("Выберите дату и время примерки")

        show_room_id = request.POST.get("show_room_id")
        if not show_room_id:
            raise DraftFittingException("Выберите шоурум")

        customer_service = CustomerService(
            UserSchema(
                first_name=request.POST.get("first_name"),
                phone=request.POST.get("phone"),
                id=request.user.id if request.user.is_authenticated else None,
                email=request.POST.get("email"),
                last_name=None,
            )
        )

        fitting_service = DraftFittingService(
            user=request.user,
            session_key=request.session.session_key,
            customer_service=customer_service,
        )
        fitting = fitting_service.confirm_fitting(
            show_room_id=int(show_room_id),
            date=FutureDatetime(date_str),
        )
        phone = fitting.user.phone if fitting.user else request.POST.get("phone", "")
        messages.success(
            request,
            f"Запись на примерку создана! Мы свяжемся с вами по номеру {phone}.",
        )
        return redirect("market:fitting")
    except (DraftFittingException, ValueError) as e:
        messages.error(request, str(e))
        return redirect("market:fitting")


@require_POST
def fitting_remove_view(request, product_id):
    service = DraftFittingService(
        user=request.user,
        session_key=request.session.session_key,
    )
    service.remove_product(product_id)
    return redirect("market:fitting")
