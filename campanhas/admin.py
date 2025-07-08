from django.contrib import admin
from .models import Campanha, Categoria, CampoPersonalizado, Entidade

@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'mestre', 'data_criacao')
    search_fields = ('nome', 'mestre__username')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'campanha')
    list_filter = ('campanha',)

@admin.register(CampoPersonalizado)
class CampoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'tipo', 'obrigatorio')
    list_filter = ('categoria', 'tipo')

@admin.register(Entidade)
class EntidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria')
    search_fields = ('nome',)
    list_filter = ('categoria',)