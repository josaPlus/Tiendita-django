from django.urls import path
from . import views

urlpatterns = [
    # Esta será http://localhost:8000/carrito/
    path('', views.ver_carrito, name='ver_carrito'),

    # Rutas de acción (agregar, actualizar, eliminar, cupon, checkout)
    # Fíjate que ya no necesito poner 'carrito/' al inicio
    path('agregar/<int:producto_id>/', views.agregar_item, name='agregar_item'),
    path('actualizar/<int:item_id>/', views.actualizar_item, name='actualizar_item'),
    path('eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('aplicar-cupon/', views.aplicar_cupon, name='aplicar_cupon'),
    path('checkout/', views.checkout, name='checkout'),
]