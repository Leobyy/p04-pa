from django import forms
from .models import Campanha, Categoria, CampoPersonalizado, Entidade

class CampanhaForm(forms.ModelForm):
    class Meta:
        model = Campanha
        fields = ['nome', 'prologo']
        widgets = {
            'prologo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome da Campanha',
            'prologo': 'Prólogo/Introdução'
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class CampoForm(forms.ModelForm):
    class Meta:
        model = CampoPersonalizado
        fields = ['nome', 'tipo', 'obrigatorio']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'obrigatorio': 'Campo obrigatório?'
        }

class EntidadeForm(forms.ModelForm):
    class Meta:
        model = Entidade
        fields = ['nome']
    
    def __init__(self, *args, **kwargs):
        self.categoria = kwargs.pop('categoria', None)
        super().__init__(*args, **kwargs)
        
        if self.categoria:
            # Adiciona campos dinâmicos baseados na categoria
            campos = CampoPersonalizado.objects.filter(categoria=self.categoria)
            for campo in campos:
                field_name = f'campo_{campo.id}'
                if campo.tipo == 'texto':
                    self.fields[field_name] = forms.CharField(
                        label=campo.nome,
                        required=campo.obrigatorio
                    )
                elif campo.tipo == 'numero':
                    self.fields[field_name] = forms.IntegerField(
                        label=campo.nome,
                        required=campo.obrigatorio
                    )
                elif campo.tipo == 'checkbox':
                    self.fields[field_name] = forms.BooleanField(
                        label=campo.nome,
                        required=campo.obrigatorio
                    )
                elif campo.tipo == 'textarea':
                    self.fields[field_name] = forms.CharField(
                        label=campo.nome,
                        required=campo.obrigatorio,
                        widget=forms.Textarea
                    )
    
    def save(self, commit=True):
        entidade = super().save(commit=False)
        entidade.categoria = self.categoria
        
        # Coleta valores dos campos dinâmicos
        valores = {}
        for key, value in self.cleaned_data.items():
            if key.startswith('campo_'):
                campo_id = key.split('_')[1]
                valores[campo_id] = value
        
        entidade.valores_campos = valores
        
        if commit:
            entidade.save()
        return entidade