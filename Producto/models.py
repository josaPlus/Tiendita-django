from django.db import models

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2) # Usar Decimal es mejor para dinero que Double
    stock = models.IntegerField() # Vital para tu requerimiento de validación

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock}"