from django.urls import path
from . import views

app_name = 'campanhas'

urlpatterns = [
    # Campanhas
    path('', views.CampanhaListView.as_view(), name='list'),
    path('nova/', views.CampanhaCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.CampanhaUpdateView.as_view(), name='update'),
    path('<int:pk>/', views.CampanhaDetailView.as_view(), name='detail'),
    
    # Categorias
    path('<int:campanha_id>/categoria/nova/', views.CategoriaCreateView.as_view(), name='categoria-create'),
    path('categoria/<int:pk>/', views.CategoriaDetailView.as_view(), name='categoria-detail'),
    
    # Campos
    path('categoria/<int:categoria_id>/campo/novo/', views.CampoCreateView.as_view(), name='campo-create'),

    # Entidades
    path('categoria/<int:categoria_id>/entidade/nova/', views.EntidadeCreateView.as_view(), name='entidade-create'),
    path('categoria/<int:categoria_id>/entidades/', views.EntidadeListView.as_view(), name='entidade-list'),
    path('entidade/<int:pk>/', views.EntidadeDetailView.as_view(), name='entidade-detail'),

    #Views de Delete
    path('campanha/<int:pk>/delete/', views.CampanhaDeleteView.as_view(), name='campanha-delete'),
    path('categoria/<int:pk>/delete/', views.CategoriaDeleteView.as_view(), name='categoria-delete'),
    path('campo/<int:pk>/delete/', views.CampoDeleteView.as_view(), name='campo-delete'),
    path('entidade/<int:pk>/delete/', views.EntidadeDeleteView.as_view(), name='entidade-delete'),

    #ExportarCSV
    path('campanha/<int:pk>/exportar/', views.exportar_campanha_csv, name='campanha-exportar'),
]