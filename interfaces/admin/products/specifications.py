from django.contrib import admin

from apps.products.models.specifications import SpecificationName, SpecificationValue


@admin.register(SpecificationName)
class SpecificationNameAdmin(admin.ModelAdmin):
    search_fields = ("name",)




@admin.register(SpecificationValue)
class SpecificationValueAdmin(admin.ModelAdmin):
    search_fields = ("value", "specification_name__name")
    list_display = ('__str__',)
    list_filter = ('specification_name__name', )
