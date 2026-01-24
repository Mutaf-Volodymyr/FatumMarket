from typing import Dict, List, Tuple, Optional
from django.db.models import QuerySet, Min, Max, Count
from decimal import Decimal
from apps.products.models import Product, SpecificationName, SpecificationValue, ProductSpecification


class ProductFiltersBuilder:
    """Класс для построения фильтров на основе queryset товаров"""
    
    def __init__(self, queryset: QuerySet[Product]):
        self.queryset = queryset
    
    def build_filters(self) -> Dict:
        """
        Строит словарь с фильтрами для товаров:
        - specifications: фильтры по спецификациям
        - price_range: ценовой диапазон
        """
        return {
            'specifications': self._build_specification_filters(),
            'price_range': self._build_price_range(),
        }
    
    def _build_specification_filters(self) -> List[Dict]:
        """
        Строит фильтры по спецификациям.
        Возвращает список словарей с информацией о каждой спецификации и её значениях.
        """
        # Получаем все активные товары из queryset (без пагинации)
        product_ids = self.queryset.values_list('id', flat=True)
        
        # Получаем все спецификации, которые используются в этих товарах
        specifications = (
            ProductSpecification.objects
            .filter(product_id__in=product_ids)
            .select_related('specification_name', 'specification_value')
            .values(
                'specification_name_id',
                'specification_name__name',
                'specification_value_id',
                'specification_value__value'
            )
            .distinct()
        )
        
        # Группируем по названию спецификации
        spec_dict: Dict[int, Dict] = {}
        
        for spec in specifications:
            spec_name_id = spec['specification_name_id']
            spec_value_id = spec['specification_value_id']
            
            if spec_name_id not in spec_dict:
                spec_dict[spec_name_id] = {
                    'id': spec_name_id,
                    'name': spec['specification_name__name'],
                    'values': []
                }
            
            # Добавляем значение, если его еще нет
            value_exists = any(
                v['id'] == spec_value_id 
                for v in spec_dict[spec_name_id]['values']
            )
            
            if not value_exists:
                spec_dict[spec_name_id]['values'].append({
                    'id': spec_value_id,
                    'value': spec['specification_value__value']
                })
        
        # Преобразуем в список и сортируем
        result = list(spec_dict.values())
        for spec in result:
            spec['values'].sort(key=lambda x: x['value'])
        
        result.sort(key=lambda x: x['name'])
        
        return result
    
    def _build_price_range(self) -> Dict[str, Optional[Decimal]]:
        """
        Строит ценовой диапазон на основе queryset.
        Возвращает словарь с min_price и max_price.
        """
        price_agg = self.queryset.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        return {
            'min_price': price_agg['min_price'],
            'max_price': price_agg['max_price'],
        }



