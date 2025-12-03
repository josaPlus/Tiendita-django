from django.contrib import admin
from .models import Producto

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