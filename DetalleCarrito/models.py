from django.db import models

class DetalleCarrito(models.Model):
    # Relaciones usando strings para evitar 'Circular Imports'
    producto = models.ForeignKey('Producto.Producto', on_delete=models.CASCADE)
    carrito = models.ForeignKey('Carrito.Carrito', on_delete=models.CASCADE, related_name='detalles')
    
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Automatización: Calcular subtotal antes de guardar
        # Necesitamos instanciar el producto para obtener el precio real
        if not self.subtotal:
            self.subtotal = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Carrito #{self.carrito.id}"