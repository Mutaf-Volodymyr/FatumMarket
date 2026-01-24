from decimal import Decimal
import random
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import (
    Category,
    Brand,
    Product,
    SpecificationName,
    SpecificationValue,
    ProductSpecification,
)


class Command(BaseCommand):
    help = 'Генерирует фейковые данные: категории, бренды, спецификации и товары'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            type=int,
            default=5,
            help='Количество категорий верхнего уровня',
        )
        parser.add_argument(
            '--brands',
            type=int,
            default=10,
            help='Количество брендов',
        )
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Количество товаров',
        )

    def handle(self, *args, **options):
        categories_count = options['categories']
        brands_count = options['brands']
        products_count = options['products']

        self.stdout.write(self.style.SUCCESS('Начинаем генерацию фейковых данных...'))

        with transaction.atomic():
            # Создаем категории
            categories = self._create_categories(categories_count)
            self.stdout.write(self.style.SUCCESS(f'Создано категорий: {len(categories)}'))

            # Создаем бренды
            brands = self._create_brands(brands_count)
            self.stdout.write(self.style.SUCCESS(f'Создано брендов: {len(brands)}'))

            # Создаем спецификации
            specifications = self._create_specifications()
            self.stdout.write(self.style.SUCCESS(f'Создано спецификаций: {len(specifications)}'))

            # Создаем товары
            products = self._create_products(products_count, categories, brands, specifications)
            self.stdout.write(self.style.SUCCESS(f'Создано товаров: {len(products)}'))

        self.stdout.write(self.style.SUCCESS('✓ Генерация данных завершена успешно!'))

    def _create_categories(self, count):
        """Создает категории с иерархией"""
        category_names = [
            'Платья', 'Блузки', 'Юбки', 'Брюки', 'Верхняя одежда',
            'Аксессуары', 'Обувь', 'Нижнее белье', 'Спортивная одежда', 'Домашняя одежда'
        ]
        
        categories = []
        parent_categories = []
        
        # Создаем родительские категории
        for i in range(min(count, len(category_names))):
            name = category_names[i]
            if not Category.objects.filter(name=name).exists():
                category = Category.objects.create(
                    name=name,
                    position=i * 10
                )
                categories.append(category)
                parent_categories.append(category)
        
        # Создаем подкатегории для некоторых категорий
        if parent_categories:
            subcategories_data = {
                'Платья': ['Повседневные', 'Вечерние', 'Коктейльные', 'Летние'],
                'Блузки': ['Классические', 'Романтичные', 'Деловые'],
                'Брюки': ['Классические', 'Джинсы', 'Леггинсы', 'Широкие'],
                'Верхняя одежда': ['Пальто', 'Куртки', 'Парки', 'Жилеты'],
                'Обувь': ['Туфли', 'Ботинки', 'Сапоги', 'Кроссовки'],
            }
            
            for parent in parent_categories[:3]:  # Только для первых 3 категорий
                if parent.name in subcategories_data:
                    for j, sub_name in enumerate(subcategories_data[parent.name]):
                        if not Category.objects.filter(name=sub_name, parent=parent).exists():
                            subcategory = Category.objects.create(
                                name=sub_name,
                                parent=parent,
                                position=j * 10
                            )
                            categories.append(subcategory)
        
        return categories if categories else list(Category.objects.all())

    def _create_brands(self, count):
        """Создает бренды"""
        brand_names = [
            'Elegance', 'StyleHouse', 'FashionLine', 'ChicWear', 'Glamour',
            'Trendy', 'Classic', 'Modern', 'Luxury', 'Premium',
            'Boutique', 'Designer', 'Fashion', 'Style', 'Elite'
        ]
        
        brands = []
        for i in range(count):
            name = brand_names[i % len(brand_names)]
            # Добавляем номер для уникальности
            if i >= len(brand_names):
                name = f"{name} {i // len(brand_names) + 1}"
            
            if not Brand.objects.filter(name=name).exists():
                brand = Brand.objects.create(
                    name=name,
                    description=f'Описание бренда {name}. Качественная женская одежда.'
                )
                brands.append(brand)
        
        return brands if brands else list(Brand.objects.all()[:count])

    def _create_specifications(self):
        """Создает спецификации (размер, цвет, материал и т.д.)"""
        specs_data = {
            'Размер': {
                'values': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'unit': None
            },
            'Цвет': {
                'values': ['Черный', 'Белый', 'Красный', 'Синий', 'Зеленый', 'Желтый', 'Розовый', 'Бежевый'],
                'unit': None
            },
            'Состав': {
                'values': ['100% Хлопок', '100% Полиэстер', 'Хлопок 80%, Полиэстер 20%', 'Вискоза 70%, Полиэстер 30%'],
                'unit': None
            },
            'Длина': {
                'values': ['Короткая', 'Средняя', 'Длинная'],
                'unit': None
            },
            'Рукав': {
                'values': ['Без рукавов', 'Короткий', 'Длинный'],
                'unit': None
            },
        }
        
        specifications = {}
        position = 10
        
        for spec_name, data in specs_data.items():
            spec_name_obj, created = SpecificationName.objects.get_or_create(
                name=spec_name,
                defaults={
                    'position': position,
                    'unit_measurement': data['unit']
                }
            )
            position += 10
            
            values = []
            for value in data['values']:
                spec_value, created = SpecificationValue.objects.get_or_create(
                    specification_name=spec_name_obj,
                    value=value
                )
                values.append(spec_value)
            
            specifications[spec_name] = {
                'name': spec_name_obj,
                'values': values
            }
        
        return specifications

    def _create_products(self, count, categories, brands, specifications):
        """Создает товары"""
        if not categories:
            self.stdout.write(self.style.WARNING('Нет категорий! Создайте категории сначала.'))
            return []
        
        if not brands:
            self.stdout.write(self.style.WARNING('Нет брендов! Создайте бренды сначала.'))
            return []
        
        product_names = [
            'Платье', 'Блузка', 'Юбка', 'Брюки', 'Пальто', 'Куртка',
            'Жилет', 'Туфли', 'Ботинки', 'Сумка', 'Ремень', 'Шарф',
            'Кардиган', 'Свитер', 'Футболка', 'Джинсы', 'Леггинсы'
        ]
        
        colors = ['Черное', 'Белое', 'Красное', 'Синее', 'Розовое', 'Бежевое']
        
        products = []
        for i in range(count):
            # Генерируем название
            base_name = random.choice(product_names)
            color = random.choice(colors)
            name = f"{color} {base_name} {i + 1}"
            
            # Проверяем уникальность
            if Product.objects.filter(name=name).exists():
                name = f"{name} (вариант {i})"
            
            # Выбираем случайную категорию (включая подкатегории)
            category = random.choice(categories)
            
            # Выбираем случайный бренд
            brand = random.choice(brands) if random.random() > 0.1 else None  # 90% с брендом
            
            # Генерируем цены
            base_price = Decimal(str(random.randint(500, 5000)))
            has_discount = random.random() > 0.6  # 40% товаров со скидкой
            
            if has_discount:
                discount_percent = random.randint(10, 40)
                price = base_price * Decimal(str(1 - discount_percent / 100))
                old_price = base_price
            else:
                price = base_price
                old_price = None
            
            # Создаем товар
            product = Product.objects.create(
                name=name,
                description=f'Описание товара {name}. Качественная женская одежда из натуральных материалов. Подходит для повседневной носки.',
                is_active=random.random() > 0.2,  # 80% активных товаров
                quantity=random.randint(0, 100),
                price=price,
                old_price=old_price,
                category=category,
                brand=brand,
            )
            
            # Добавляем спецификации
            self._add_product_specifications(product, specifications)
            
            products.append(product)
        
        return products

    def _add_product_specifications(self, product, specifications):
        """Добавляет спецификации к товару"""
        # Размер (обязательно)
        if 'Размер' in specifications:
            size = random.choice(specifications['Размер']['values'])
            ProductSpecification.objects.get_or_create(
                product=product,
                specification_name=specifications['Размер']['name'],
                defaults={'specification_value': size}
            )
        
        # Цвет (обязательно)
        if 'Цвет' in specifications:
            color = random.choice(specifications['Цвет']['values'])
            ProductSpecification.objects.get_or_create(
                product=product,
                specification_name=specifications['Цвет']['name'],
                defaults={'specification_value': color}
            )
        
        # Состав (с вероятностью 80%)
        if 'Состав' in specifications and random.random() > 0.2:
            composition = random.choice(specifications['Состав']['values'])
            ProductSpecification.objects.get_or_create(
                product=product,
                specification_name=specifications['Состав']['name'],
                defaults={'specification_value': composition}
            )
        
        # Дополнительные спецификации (с вероятностью 50%)
        if 'Длина' in specifications and random.random() > 0.5:
            length = random.choice(specifications['Длина']['values'])
            ProductSpecification.objects.get_or_create(
                product=product,
                specification_name=specifications['Длина']['name'],
                defaults={'specification_value': length}
            )
        
        if 'Рукав' in specifications and random.random() > 0.5:
            sleeve = random.choice(specifications['Рукав']['values'])
            ProductSpecification.objects.get_or_create(
                product=product,
                specification_name=specifications['Рукав']['name'],
                defaults={'specification_value': sleeve}
            )



