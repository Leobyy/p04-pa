from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Campanha, Categoria, CampoPersonalizado, Entidade
from .forms import CampanhaForm, CategoriaForm, CampoForm, EntidadeForm
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponse
import csv
import json

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

class CampanhaUpdateView(LoginRequiredMixin, UpdateView):
    model = Campanha
    form_class = CampanhaForm
    template_name = 'campanhas/campanha_form.html'
    success_url = reverse_lazy('campanhas:list')

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

class CampanhaDeleteView(LoginRequiredMixin, DeleteView):
    model = Campanha
    template_name ='campanhas/confirm_delete.html'
    success_url = reverse_lazy('campanhas:list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "Campanha deletada com sucesso!")
        return JsonResponse({'success': True})
    
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

class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'campanhas/confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('campanhas:detail', kwargs={'pk': self.object.campanha.pk})

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
    
class CampoDeleteView(LoginRequiredMixin, DeleteView):
    model = CampoPersonalizado
    template_name = 'campanhas/confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('campanhas:categoria-detail', kwargs={'pk': self.object.categoria.pk})
    
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
    
class EntidadeDeleteView(LoginRequiredMixin, DeleteView):
    model = Entidade
    template_name = 'campanhas/confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('campanhas:categoria-detail', kwargs={'pk': self.object.categoria.pk})


def exportar_campanha_csv(request, pk):
    campanha = Campanha.objects.prefetch_related(
        Prefetch(
            'categorias',
            queryset=Categoria.objects.prefetch_related(
                'campos',
                Prefetch(
                    'entidades',
                    queryset=Entidade.objects.all().order_by('nome')
                )
            )
        )
    ).get(pk=pk)
    
    # Cria a resposta HTTP com o cabeçalho de arquivo CSV
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="campanha_{campanha.nome}.csv"'},
    )
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Tipo', 'ID', 'Nome', 'Descrição', 'Relacionamentos', 'Campos Adicionais'])
    
    # Exporta a campanha
    writer.writerow([
        'CAMPANHA',
        campanha.id,
        campanha.nome,
        campanha.prologo or '',
        f'Mestre: {campanha.mestre.username}',
        f'Data Criação: {campanha.data_criacao.strftime("%d/%m/%Y %H:%M")}'
    ])
    
    # Exporta categorias
    for categoria in campanha.categorias.all():
        writer.writerow([
            'CATEGORIA',
            categoria.id,
            categoria.nome,
            categoria.descricao or '',
            f'Campanha: {campanha.nome}',
            ''
        ])
        
        # Exporta campos personalizados da categoria
        for campo in categoria.campos.all():
            writer.writerow([
                'CAMPO PERSONALIZADO',
                campo.id,
                campo.nome,
                '',
                f'Categoria: {categoria.nome}',
                f'Tipo: {campo.get_tipo_display()}, Obrigatório: {"Sim" if campo.obrigatorio else "Não"}'
            ])
        
        # Exporta entidades da categoria
        for entidade in categoria.entidades.all():
            # Formata campos personalizados
            campos_formatados = []
            for campo_id, valor in entidade.valores_campos.items():
                try:
                    campo = CampoPersonalizado.objects.get(id=int(campo_id))
                    campos_formatados.append(f"{campo.nome}: {valor}")
                except (ValueError, CampoPersonalizado.DoesNotExist):
                    campos_formatados.append(f"Campo ID {campo_id}: {valor}")
            
            writer.writerow([
                'ENTIDADE',
                entidade.id,
                entidade.nome,
                '',
                f'Categoria: {categoria.nome}',
                ' | '.join(campos_formatados)
            ])
    
    return response