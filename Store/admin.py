from django.contrib import admin

from .models import Customer, Category, Type, Product, StockItem, Address, Order, OrderItem, Banner, Color, Payment
# Ou "from .models import *"

# Register your models here.
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Type)
admin.site.register(Product)
admin.site.register(StockItem)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Banner)
admin.site.register(Color)
admin.site.register(Payment)

