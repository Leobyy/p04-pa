from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

class Campanha(models.Model):
    mestre = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    prologo = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Categoria(models.Model):
    campanha = models.ForeignKey(Campanha, on_delete=models.CASCADE, related_name='categorias')
    nome = models.CharField(max_length=50)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nome} ({self.campanha.nome})"

class CampoPersonalizado(models.Model):
    TIPOS_CAMPO = [
        ('texto', 'Texto'),
        ('numero', 'Número'),
        ('checkbox', 'Checkbox'),
        ('textarea', 'Texto Longo'),
    ]
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='campos')
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=10, choices=TIPOS_CAMPO)
    obrigatorio = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class Entidade(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='entidades')
    nome = models.CharField(max_length=100, default="")
    # Armazena os valores dos campos personalizados
    valores_campos = models.JSONField(encoder=DjangoJSONEncoder, default=dict)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome
    
    def get_valor_campo(self, campo_id):
        return self.valores_campos.get(str(campo_id), "")