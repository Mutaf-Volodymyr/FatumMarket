from celery import shared_task


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def validate_and_geocode_address(self, address_id):
    from apps.address.models import Address
    from apps.address.domain.geocoding import geocode_address

    address = Address.objects.get(id=address_id)

    result, error = geocode_address(address.raw_address)

    if error:
        address.is_validated = False
        address.validation_error = error
        address.save(update_fields=["is_validated", "validation_error"])
        return

    addr = result["address"]

    address.latitude = result["lat"]
    address.longitude = result["lon"]
    address.city = addr.get("city") or addr.get("town") or ""
    address.street = addr.get("road") or ""
    address.house = addr.get("house_number") or ""

    address.is_validated = True
    address.validation_error = ""

    address.save()

