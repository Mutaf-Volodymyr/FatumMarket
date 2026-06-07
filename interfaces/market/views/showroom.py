from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.delivery.models import PickupPlace


@require_GET
def showroom_view(request):
    showrooms = PickupPlace.objects.filter(show_room=True).order_by("position")
    return render(request, "market/showroom.html", {"showrooms": showrooms})
