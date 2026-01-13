
from apps.products.models import Product


class ProductManagerException(Exception):
    pass

class ProductSaleManager:

    def __init__(self, product_ids: list[int]):
        self._product_ids = product_ids
        self._products_dict = None
        self._queryset = None


    @property
    def products_dict(self):
        if self._products_dict is not None:
            return self._products_dict

    def _get_product_dict(self) -> dict[int, Product]:

        self._products_dict = {i.id: i for i in self.get_queryset()}

        if len(self._products_dict) != len(self._product_ids):
            raise ProductManagerException('Not all products found')

        return self._products_dict


    def get_queryset(self):
        if self._queryset is not None:
            return self._queryset
        self._queryset = Product.objects.select_for_update().filter(
                pk__in=self._product_ids,
                is_active=True,
            ).distinct()
        return self._queryset


    def update_queryset_quantity(self) -> int:
        count = Product.objects.bulk_update(self.products_dict.values(), fields=['quantity'])
        return count


    def update_product_quantity(self, *, product_id: int, sale_qty: int) -> int:
        product = self.get_product_by_id(product_id)

        if product.quantity < sale_qty:
            raise ProductManagerException('Product quantity less than sale quantity')

        product.quantity -= sale_qty

        return product.quantity


    def get_product_by_id(self, product_id: int) -> Product:
        try:
            product = self.products_dict[product_id]
        except KeyError:
            raise ProductManagerException('Product not found')
        return product


