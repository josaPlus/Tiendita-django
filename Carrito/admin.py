from django.contrib import admin
from .models import Carrito, Cupon, DetalleCarrito, Producto

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

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista
    list_display = ('nombre', 'precio', 'stock', 'id') 
    # Barra de búsqueda
    search_fields = ('nombre', 'descripcion')
    # Filtros laterales
    list_filter = ('precio',)
    # Para poder editar el stock directo desde la lista (opcional)
    list_editable = ('stock', 'precio')

@admin.register(DetalleCarrito)
class DetalleCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad', 'subtotal')
    raw_id_fields = ('carrito', 'producto') # Para que no cargue una lista gigante si tienes muchos productos