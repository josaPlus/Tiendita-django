from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('accounts/', include('django.contrib.auth.urls')),
    # Tus rutas de la tienda
    path('carrito/', include('Carrito.urls')),
    # Redirige la raíz (hueco vacío) directamente al catálogo (o al login)
    path('', RedirectView.as_view(pattern_name='catalogo', permanent=False)),
]