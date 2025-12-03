from django.contrib import admin
from .models import DetalleCarrito

@admin.register(DetalleCarrito)
class DetalleCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad', 'subtotal')
    raw_id_fields = ('carrito', 'producto') # Para que no cargue una lista gigante si tienes muchos productos