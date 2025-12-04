from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Carrito, Cupon, Producto, DetalleCarrito
from django.contrib.auth.decorators import login_required
from decimal import Decimal

# --- Función Auxiliar (privada) ---
@login_required
def _get_carrito(request):
    """Obtiene el carrito de la sesión o crea uno nuevo si no existe."""
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            return Carrito.objects.get(id=cart_id, pagado=False)
        except Carrito.DoesNotExist:
            pass # Si no existe, creamos uno nuevo abajo
            
    carrito = Carrito.objects.create(total=0.0)
    request.session['cart_id'] = carrito.id
    return carrito

# --- Rutas Públicas ---
@login_required
def ver_carrito(request):
    carrito = _get_carrito(request)
    # Obtenemos los detalles usando el related_name 'detalles' definido en models
    items = carrito.detalles.all().select_related('producto')
    
    # Recalculamos el total (Tu función subtotal())
    total = sum(item.subtotal for item in items)
    carrito.total = total
    carrito.save()

    # Lógica de Cupón (se guarda en sesión para persistencia)
    descuento_session = request.session.get('descuento_monto', 0)
    
    # Lo convertimos forzosamente a Decimal para poder restarlo
    descuento = Decimal(str(descuento_session))
    total_con_descuento = total - descuento

    return render(request, 'carrito.html', {
        'carrito': carrito,
        'items': items,
        'descuento': descuento,
        'total_final': max(total_con_descuento, 0) # Evitar negativos
    })

@login_required
def agregar_item(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        carrito = _get_carrito(request)
        cantidad_solicitada = int(request.POST.get('cantidad', 1))

        # 1. Tu lógica: verificarDisponibilidad()
        if cantidad_solicitada > producto.stock:
            messages.error(request, f"Error: Solo hay {producto.stock} unidades disponibles.")
            return redirect('catalogo')

        # 2. Verificar si ya existe en el carrito
        item, created = DetalleCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': 0, 'subtotal': 0}
        )

        # 3. Validar stock sumando lo que ya tengo en el carrito + lo nuevo
        cantidad_total = item.cantidad + cantidad_solicitada
        if cantidad_total > producto.stock:
            messages.error(request, f"No puedes agregar más. Ya tienes {item.cantidad} en carrito y solo quedan {producto.stock}.")
        else:
            item.cantidad = cantidad_total
            item.subtotal = item.producto.precio * item.cantidad
            item.save()
            messages.success(request, f"Agregado: {producto.nombre}")

    return redirect('catalogo')

@login_required
def actualizar_item(request, item_id):
    item = get_object_or_404(DetalleCarrito, id=item_id)
    
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad'))
        
        if nueva_cantidad <= 0:
            # Caso "Eliminar si es 0"
            return eliminar_item(request, item_id)
        
        # Validación estricta de stock nuevamente
        if nueva_cantidad > item.producto.stock:
            messages.error(request, f"Stock insuficiente para {nueva_cantidad} unidades.")
        else:
            item.cantidad = nueva_cantidad
            item.subtotal = item.producto.precio * item.cantidad
            item.save()
            messages.success(request, "Carrito actualizado")

    return redirect('ver_carrito')

@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(DetalleCarrito, id=item_id)
    item.delete()
    messages.warning(request, "Producto eliminado del carrito")
    return redirect('ver_carrito')

@login_required
def aplicar_cupon(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo').strip()
        try:
            cupon = Cupon.objects.get(codigo=codigo, activo=True)
            
            # Calcular descuento basado en el total actual del carrito
            carrito = _get_carrito(request)
            total_actual = sum(d.subtotal for d in carrito.detalles.all())
            
            monto_descuento = (total_actual * cupon.descuento) / 100
            
            # Guardamos el descuento en la sesión
            request.session['descuento_codigo'] = cupon.codigo
            request.session['descuento_monto'] = float(monto_descuento)
            
            messages.success(request, f"Cupón {codigo} aplicado: {cupon.descuento}% off")
            
        except Cupon.DoesNotExist:
            request.session['descuento_monto'] = 0
            messages.error(request, "Código de descuento inválido o expirado.")
            
    return redirect('ver_carrito')

@login_required
def checkout(request):
    # Si intentan entrar por la URL (GET), los devolvemos al carrito.
    if request.method != 'POST':
        return redirect('ver_carrito')

    carrito = _get_carrito(request)
    items = carrito.detalles.all()

    if not items:
        messages.error(request, "El carrito está vacío.")
        return redirect('catalogo')

    # Validación FINAL de stock
    for item in items:
        if item.cantidad > item.producto.stock:
            messages.error(request, f"Lo sentimos, el producto {item.producto.nombre} ya no tiene stock suficiente.")
            return redirect('ver_carrito')

    # Restar inventario
    for item in items:
        producto = item.producto
        producto.stock -= item.cantidad
        producto.save()
    
    # Cerrar carrito y ACTUALIZAR FECHA
    carrito.pagado = True    
    carrito.fecha = timezone.now() 
    carrito.save()
    
    # Limpiar sesión
    del request.session['cart_id']
    if 'descuento_monto' in request.session:
        del request.session['descuento_monto']

    # Mensaje de éxito y redirección
    messages.success(request, "¡Compra exitosa! Gracias por tu preferencia.")
    return redirect('catalogo')

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