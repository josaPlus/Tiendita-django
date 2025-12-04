from django.urls import path
from . import views

urlpatterns = [
    # Fila 2 de la imagen: /carrito (GET)
    path('', views.ver_carrito, name='ver_carrito'), 

    # Fila 3: /carrito/agrega/:id (POST) - Nota el cambio a "agrega"
    path('agrega/<int:producto_id>/', views.agregar_item, name='agregar_item'),

    # Fila 4: /carrito/actualizar/:id (POST)
    path('actualizar/<int:item_id>/', views.actualizar_item, name='actualizar_item'),

    # Fila 5: /carrito/eliminar/:id (POST)
    path('eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),

    # Fila 6: /carrito/aplicar-cupon
    path('aplicar-cupon/', views.aplicar_cupon, name='aplicar_cupon'),

    # Fila 7: /checkout (POST) - (En realidad será /carrito/checkout)
    path('checkout/', views.checkout, name='checkout'),
    
    # Fila 1: /catalogo - (En realidad será /carrito/catalogo)
    path('catalogo/', views.catalogo, name='catalogo'),

    # Sirve para poblar la BD. Ruta final: /carrito/cargar-productos/
    path('cargar-productos/', views.cargar_productos, name='cargar_productos'),
]