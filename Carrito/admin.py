from django.contrib import admin
from .models import Carrito, Cupon

@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descuento', 'activo')
    list_editable = ('activo',) # Para activar/desactivar rápido
    search_fields = ('codigo',)

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    # Veremos de quién es el carrito y si ya pagó
    list_display = ('id', 'total', 'pagado', 'fecha')
    list_filter = ('pagado', 'fecha')