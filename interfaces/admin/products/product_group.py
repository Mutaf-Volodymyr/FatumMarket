from django import forms
from django.contrib import admin
from django.forms import SelectMultiple

from apps.products.models import Product, ProductGroup, ProductSpecification, SpecificationValue


class ProductInlineForm(forms.ModelForm):
    specifications = forms.ModelMultipleChoiceField(
        queryset=SpecificationValue.objects.all(),
        required=False,
        widget=SelectMultiple(),
    )

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["specifications"].initial = self.instance.specifications.all()

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self._save_specifications(instance)
        else:
            old_save_m2m = self.save_m2m

            def new_save_m2m():
                specs = self.cleaned_data.pop("specifications", [])
                old_save_m2m()
                self.cleaned_data["specifications"] = specs
                self._save_specifications(instance)

            self.save_m2m = new_save_m2m
        return instance

    def _save_specifications(self, instance):
        instance.product_specification.all().delete()
        for spec_value in self.cleaned_data.get("specifications", []):
            ProductSpecification.objects.create(
                product=instance,
                specification_value=spec_value,
                specification_name_id=spec_value.specification_name_id,
            )


class ProductInline(admin.StackedInline):
    model = Product
    form = ProductInlineForm
    extra = 0
    fields = [
        "is_active",
        "quantity",
        "price",
        "old_price",
    ]

    def get_fields(self, request, obj=None):
        return self.fields + ["specifications"]


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)
    inlines = (ProductInline,)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if not obj.pk:
                group = form.instance
                obj.name = group.name
                obj.description = group.description
                obj.category_id = group.category_id
            obj.save()
        formset.save_m2m()
