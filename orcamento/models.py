from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=(('1', 'Receita'), ('2', 'Despesa')))

    def __str__(self):
        return self.nome


class Subcategoria(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Lancamento(models.Model):
    descricao = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')
    create_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.descricao
