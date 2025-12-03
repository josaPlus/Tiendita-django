from django.db import models

class Carrito(models.Model):
    # idCarrito es el PK automático
    # El campo JSON según tu ER. Puede usarse para guardar un snapshot o logs.
    item = models.JSONField(default=dict, blank=True, null=True) 
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Campo opcional para saber si el carrito ya fue pagado (útil para el Checkout)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Carrito #{self.id} - Total: {self.total}"

class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True) # Ej: "RUTH15"
    descuento = models.IntegerField() # Ej: 15 para 15%
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo