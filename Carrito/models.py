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