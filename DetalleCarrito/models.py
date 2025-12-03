from django.db import models

class DetalleCarrito(models.Model):
    producto = models.ForeignKey('Producto.Producto', on_delete=models.CASCADE)
    carrito = models.ForeignKey('Carrito.Carrito', on_delete=models.CASCADE, related_name='detalles')
    
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Carrito #{self.carrito.id}"