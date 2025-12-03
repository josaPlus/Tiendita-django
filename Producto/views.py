from django.shortcuts import render
from .models import Producto
from Carrito.models import Carrito
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your views here.
@login_required
def catalogo(request):
    # Lógica equivalente a self.productos_disponibles
    productos = Producto.objects.all().order_by('id')
    
    # Obtener carrito de la sesión para el contador del badge
    cart_id = request.session.get('cart_id')
    cantidad_items = 0
    if cart_id:
        try:
            carrito = Carrito.objects.get(id=cart_id)
            # Contamos cuántos productos únicos hay
            cantidad_items = carrito.detalles.count() 
        except Carrito.DoesNotExist:
            pass

    return render(request, 'catalogo.html', {
        'productos': productos,
        'cantidad_items': cantidad_items
    })

def cargar_productos(request):
    lista_productos = [
        {"nombre": "Laptop Gamer", "descripcion": "Potente laptop para juegos de última generación.", "stock": 15, "precio": 1299.99},
        {"nombre": "Smartphone Pro", "descripcion": "Teléfono con la mejor cámara del mercado.", "stock": 40, "precio": 999.50},
        {"nombre": "Teclado Mecánico RGB", "descripcion": "Teclado con switches azules y luces personalizables.", "stock": 75, "precio": 89.90},
        {"nombre": "Monitor Curvo 27\"", "descripcion": "Experiencia inmersiva con alta tasa de refresco.", "stock": 25, "precio": 349.00},
        {"nombre": "Silla Ergonómica", "descripcion": "Comodidad total para largas horas de trabajo.", "stock": 30, "precio": 199.99},
        {"nombre": "Auriculares Inalámbricos", "descripcion": "Sonido de alta fidelidad con cancelación de ruido.", "stock": 120, "precio": 149.50},
        {"nombre": "Cafetera Express", "descripcion": "El mejor café para empezar tus mañanas.", "stock": 50, "precio": 79.00},
        {"nombre": "Zapatillas Deportivas", "descripcion": "Calzado ligero ideal para correr.", "stock": 200, "precio": 119.95},
        {"nombre": "Mochila Antirrobo", "descripcion": "Diseño seguro con puerto de carga USB.", "stock": 80, "precio": 59.99},
        {"nombre": "Libro 'El Arte de Programar'", "descripcion": "La guía definitiva para desarrolladores.", "stock": 150, "precio": 29.99},
        {"nombre": "Smartwatch Fit", "descripcion": "Monitorea tu salud y actividad física.", "stock": 90, "precio": 219.00},
        {"nombre": "Cámara de Seguridad WiFi", "descripcion": "Vigilancia 24/7 accesible desde tu celular.", "stock": 60, "precio": 49.99},
        {"nombre": "Botella de Agua Inteligente", "descripcion": "Te recuerda beber agua y mantiene la temperatura.", "stock": 110, "precio": 39.50},
        {"nombre": "Disco Duro Externo 2TB", "descripcion": "Almacenamiento extra para todos tus archivos.", "stock": 55, "precio": 74.99},
        {"nombre": "Mousepad XL", "descripcion": "Superficie amplia y deslizamiento preciso.", "stock": 300, "precio": 19.99}
    ]

    contador = 0
    for data in lista_productos:
        # get_or_create evita duplicados: solo crea si no existe el nombre
        obj, created = Producto.objects.get_or_create(
            nombre=data['nombre'],
            defaults={
                'descripcion': data['descripcion'],
                'stock': data['stock'],
                'precio': data['precio']
            }
        )
        if created:
            contador += 1

    return HttpResponse(f"""
        <h1>Proceso Terminado</h1>
        <p>Se agregaron <strong>{contador}</strong> productos nuevos al inventario.</p>
        <a href='/'>Ir al Catálogo</a>
    """)