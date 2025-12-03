from django.db import models

class Carrito(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)    
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Carrito #{self.id} - Total: {self.total}"

class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.IntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo
    
class DetalleCarrito(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE, related_name='detalles')
    
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Carrito #{self.carrito.id}"

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2) # Usar Decimal es mejor para dinero que Double
    stock = models.IntegerField() # Vital para tu requerimiento de validación

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock}"