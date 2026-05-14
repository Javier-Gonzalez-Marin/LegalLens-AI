from django.db import models
from django.contrib.auth.models import User 

class Contrato(models.Model):
    # Relacionamos el contrato con el abogado que lo sube
    abogado = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    cliente = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50)
    # Guardamos los resultados de la IA como JSON
    hallazgos = models.JSONField(default=list)
    puntos_clave = models.JSONField(default=list)

    def __str__(self):
        return f"{self.nombre} - {self.abogado.username}"
