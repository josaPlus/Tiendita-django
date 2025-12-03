from django.urls import path
from . import views # Importamos las vistas de ESTA carpeta

urlpatterns = [
    # Ruta raíz de esta app (que será http://localhost:8000/)
    path('', views.catalogo, name='home'),
    
    # Ruta explícita (http://localhost:8000/catalogo)
    path('catalogo/', views.catalogo, name='catalogo'),
    path('cargar-productos/', views.cargar_productos, name='cargar_productos'),
]