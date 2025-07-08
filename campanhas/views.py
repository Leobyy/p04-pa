from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Campanha, Categoria, CampoPersonalizado, Entidade
from .forms import CampanhaForm, CategoriaForm, CampoForm, EntidadeForm
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

class CadastroUsuarioView(CreateView):
    template_name = 'cadastro.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('campanhas:list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Loga o usuário automaticamente após cadastro
        return response

class CampanhaListView(LoginRequiredMixin, ListView):
    model = Campanha
    template_name = 'campanhas/campanha_list.html'
    context_object_name = 'campanhas'

    def get_queryset(self):
        return Campanha.objects.filter(mestre=self.request.user)

class CampanhaCreateView(LoginRequiredMixin, CreateView):
    model = Campanha
    form_class = CampanhaForm
    template_name = 'campanhas/campanha_form.html'
    success_url = reverse_lazy('campanhas:list')

    def form_valid(self, form):
        form.instance.mestre = self.request.user
        return super().form_valid(form)

# View para editar campanha
class CampanhaUpdateView(LoginRequiredMixin, UpdateView):
    model = Campanha
    form_class = CampanhaForm
    template_name = 'campanhas/campanha_form.html'
    success_url = reverse_lazy('campanhas:list')

# View para detalhes da campanha (com categorias)
class CampanhaDetailView(LoginRequiredMixin, DetailView):
    model = Campanha
    template_name = 'campanhas/campanha_detail.html'
    
    def get_queryset(self):
        # Otimiza o carregamento das categorias e suas relações
        return Campanha.objects.filter(mestre=self.request.user).prefetch_related(
            Prefetch('categorias', queryset=Categoria.objects.all().prefetch_related('campos', 'entidades'))
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = self.object.categorias.all()
        return context
    
# View para criar categoria dentro de uma campanha
class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'campanhas/categoria_form.html'

    def form_valid(self, form):
        campanha = Campanha.objects.get(pk=self.kwargs['campanha_id'])
        form.instance.campanha = campanha
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('campanhas:detail', kwargs={'pk': self.kwargs['campanha_id']})
    
# View para visualizar categoria e seus campos
class CategoriaDetailView(LoginRequiredMixin, DetailView):
    model = Categoria
    template_name = 'campanhas/categoria_detail.html'
    context_object_name = 'categoria'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campanha'] = self.object.campanha
        context['campos'] = self.object.campos.all()
        context['entidades'] = self.object.entidades.all()
        return context

# View para adicionar campos a uma categoria
class CampoCreateView(LoginRequiredMixin, CreateView):
    model = CampoPersonalizado
    form_class = CampoForm
    template_name = 'campanhas/campo_form.html'

    def form_valid(self, form):
        categoria = get_object_or_404(Categoria, pk=self.kwargs['categoria_id'])
        form.instance.categoria = categoria
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = get_object_or_404(Categoria, pk=self.kwargs['categoria_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('campanhas:categoria-detail', kwargs={'pk': self.kwargs['categoria_id']})
    
class EntidadeCreateView(LoginRequiredMixin, CreateView):
    model = Entidade
    form_class = EntidadeForm
    template_name = 'campanhas/entidade_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        categoria_id = self.kwargs['categoria_id']
        kwargs['categoria'] = Categoria.objects.get(id=categoria_id)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = Categoria.objects.get(id=self.kwargs['categoria_id'])
        return context
    
    def get_success_url(self):
        return reverse_lazy('campanhas:categoria-detail', kwargs={'pk': self.kwargs['categoria_id']})
    
class EntidadeDetailView(LoginRequiredMixin, DetailView):
    model = Entidade
    template_name = 'campanhas/entidade_detail.html'
    context_object_name = 'entidade'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entidade = self.get_object()
        
        # Prepara os campos para exibição
        campos_com_valores = []
        for campo in entidade.categoria.campos.all():
            valor = entidade.get_valor_campo(campo.id)
            campos_com_valores.append({
                'nome': campo.nome,
                'tipo': campo.get_tipo_display(),
                'valor': valor
            })
        
        context['campos'] = campos_com_valores
        return context
    
# campanhas/views.py
class EntidadeListView(LoginRequiredMixin, ListView):
    model = Entidade
    template_name = 'campanhas/entidade_list.html'
    context_object_name = 'entidades'
    
    def get_queryset(self):
        categoria_id = self.kwargs['categoria_id']
        return Entidade.objects.filter(categoria_id=categoria_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = get_object_or_404(Categoria, id=self.kwargs['categoria_id'])
        return context