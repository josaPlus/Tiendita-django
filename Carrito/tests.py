from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from Carrito.models import Carrito, Cupon, Producto, DetalleCarrito
from django.contrib.messages import get_messages 

User = get_user_model()

# CASO DE PRUEBA 1: GESTIÓN DE ÍTEMS Y VALIDACIÓN DE STOCK

class GestionCarritoTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client = Client()
        self.client.login(username='tester', password='password123')
        
        self.producto_A = Producto.objects.create(
            nombre="Producto Test A",
            precio=100.00,
            stock=10
        )
        
        self.producto_B = Producto.objects.create(
            nombre="Producto Test B",
            precio=50.00,
            stock=5
        )
        
        self.url_agregar_A = reverse('agregar_item', args=[self.producto_A.id])
        self.url_ver_carrito = reverse('ver_carrito')
        
    # 1.1: Agregar Producto Exitosamente
    def test_agregar_item_exitoso(self):
        response = self.client.post(self.url_agregar_A, {'cantidad': 4})
        
        self.assertRedirects(response, reverse('catalogo'), status_code=302)

        item_creado = DetalleCarrito.objects.get(producto=self.producto_A)
        self.assertEqual(item_creado.cantidad, 4)
        
        self.assertEqual(item_creado.subtotal, Decimal('400.00'))

    # 1.2: Validación de Stock Insuficiente
    def test_validacion_stock_insuficiente(self):
        response = self.client.post(self.url_agregar_A, {'cantidad': 11})
        
        self.assertRedirects(response, reverse('catalogo'))
        
        self.assertFalse(DetalleCarrito.objects.filter(producto=self.producto_A).exists())
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Error: Solo hay 10 unidades disponibles.", [m.message for m in messages])

    # 1.3: Modificación y Recálculo de Subtotal
    def test_modificar_item_y_recalculo(self):
        # 1. Pre-condición: Agregar 2 unidades de Prod B al carrito
        self.client.post(reverse('agregar_item', args=[self.producto_B.id]), {'cantidad': 2})
        item_B = DetalleCarrito.objects.get(producto=self.producto_B)
        
        # URL de actualización usa el ID del DetalleCarrito
        url_actualizar = reverse('actualizar_item', args=[item_B.id])

        # 2. POST para cambiar la cantidad a 5
        self.client.post(url_actualizar, {'cantidad': 5})
        item_B.refresh_from_db()
        
        self.assertEqual(item_B.cantidad, 5) 

        self.assertEqual(item_B.subtotal, Decimal('250.00'))
        
        response = self.client.get(self.url_ver_carrito)
        self.assertEqual(response.context['carrito'].total, Decimal('250.00'))

# CASO DE PRUEBA 2: REGLAS DE NEGOCIO Y CHECKOUT

class ReglasNegocioTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='negocio_tester', password='password123')
        self.client = Client()
        self.client.login(username='negocio_tester', password='password123')
        
        # 1. Crear Productos
        self.prod_X = Producto.objects.create(nombre="Producto X", precio=100.00, stock=10)
        self.prod_Y = Producto.objects.create(nombre="Producto Y", precio=50.00, stock=5)
        
        # 2. Crear Cupón (RUTH15 = 15%)
        self.cupon_15 = Cupon.objects.create(codigo='RUTH15', descuento=15, activo=True)
        self.cupon_invalido = Cupon.objects.create(codigo='EXPIRADO', descuento=10, activo=False)
        
        # 3. Simular Carrito con Ítems (Total base: 2 * 100 + 1 * 50 = $250.00)
        # Importante: Esto crea el objeto Carrito en la DB
        self.client.post(reverse('agregar_item', args=[self.prod_X.id]), {'cantidad': 2}) 
        self.client.post(reverse('agregar_item', args=[self.prod_Y.id]), {'cantidad': 1})
        
        # Rutas
        self.url_aplicar_cupon = reverse('aplicar_cupon')
        self.url_checkout = reverse('checkout')

    #  2.1: Aplicación Correcta de Cupón (CU-03)
    def test_aplicacion_cupon_exitosa(self):
        # 1. Aplicar Cupón
        response = self.client.post(self.url_aplicar_cupon, {'codigo': 'RUTH15'})
        
        self.assertRedirects(response, reverse('ver_carrito'))
        
        total_base = Decimal('250.00')
        monto_descuento_esperado = Decimal('37.50')
        total_final_esperado = total_base - monto_descuento_esperado 
        
        self.assertEqual(self.client.session.get('descuento_monto'), float(monto_descuento_esperado))
        
        response_carrito = self.client.get(reverse('ver_carrito'))
        self.assertEqual(response_carrito.context['total_final'], total_final_esperado)

    # 2.2: Cupón Inválido (Flujo Alternativo CU-03)
    def test_aplicacion_cupon_invalido(self):
        # Intentar aplicar cupón expirado
        response = self.client.post(self.url_aplicar_cupon, {'codigo': 'EXPIRADO'})
        
        self.assertRedirects(response, reverse('ver_carrito'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Código de descuento inválido o expirado.", [m.message for m in messages])
        
        self.assertEqual(self.client.session.get('descuento_monto', 0), 0)

    # 2.3: Procesamiento de Checkout y Actualización de Stock (CU-04)
    def test_procesamiento_checkout(self):
        # 1. CORRECCIÓN APLICADA: Obtener el objeto Carrito activo antes del checkout
        carrito_activo = Carrito.objects.get(pagado=False) 
        
        # 2. Ejecutar checkout
        response = self.client.post(self.url_checkout)
        
        carrito_activo.refresh_from_db() 
        self.assertTrue(carrito_activo.pagado) 

        prod_X_final = Producto.objects.get(id=self.prod_X.id)
        self.assertEqual(prod_X_final.stock, 8)
        
        self.assertNotIn('cart_id', self.client.session)