from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from models_logging.admin import HistoryAdmin
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images', null=True, blank=True)

    def image_url(self):
        if self.image:
            return f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{self.image}'
        return None

    def __str__(self):
        return self.user.username

class LoggingAdminModel(HistoryAdmin):
    history_latest_first = False
    inline_models_history = '__all__' 

# Create models Notas.
class Nota(models.Model):
    TIPO_COMPRA_VENDA = (
        ('C','COMPRA'),
        ('V','VENDA'),
    )
    ativo = models.CharField(max_length=50)
    quantidade = models.IntegerField()
    preco = models.DecimalField(max_digits=10,decimal_places=2, verbose_name='Preço')
    data = models.DateField()
    tipo = models.CharField(max_length=50, choices=TIPO_COMPRA_VENDA)
    total_compra = models.DecimalField(max_digits=10,decimal_places=2, verbose_name='Total Compra', blank=True)
    identificador = models.CharField(max_length=50)
    corretagem = models.DecimalField(max_digits=10,decimal_places=2)
    emolumentos = models.DecimalField(max_digits=10,decimal_places=2, verbose_name='Emolumento B3')
    tx_liquida_CBLC = models.DecimalField(max_digits=10,decimal_places=2, verbose_name='Taxa Líquida CBLC')
    IRRF_Final = models.DecimalField(blank=True, default=0.00, max_digits=10,decimal_places=2, verbose_name='IRRF Final')
    Lucro_Day_Trade = models.DecimalField(blank=True, default=0.00, max_digits=10,decimal_places=2, verbose_name='Lucro Day Trade')
    IRRF_Day_Trade = models.DecimalField(blank=True, default=0.00, max_digits=10,decimal_places=2, verbose_name='IRRF Day Trade')
    total_custo = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2, verbose_name='Total Custo')
    corretora = models.CharField(blank=True, max_length=250)
    data_instante = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="usuário")

    def save(self, *args, **kwargs):
        self.ativo = self.ativo.upper()        
        self.total_compra = self.preco * self.quantidade
        self.total_custo = self.corretagem + self.emolumentos + self.tx_liquida_CBLC

        super(Nota, self).save(*args,**kwargs)
        
    def __str__(self):
        return self.ativo.upper()

# Create models Cotacao
class Cotacao(models.Model):
    acao = models.CharField(blank=True, max_length=255)
    ativo = models.CharField(blank=True, max_length=255, unique=True)
    fechamento_ajustado = models.CharField(blank=True, max_length=255, default=0.00)
    variacao_1 = models.CharField(blank=True, max_length=255, default=0.00)
    variacao_2 = models.CharField(blank=True, max_length=255, default=0.00)
    status_fechado_aberto = models.CharField(blank=True, max_length=255, default='Aguardando Atualizacao')
    data_instante = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.ativo

# Create models Proventos
class Proventos(models.Model):
    TIPO_PROVENTOS = (
        ('D','DIVIDENDOS'),
        ('J','JUROS COMPOSTO'),
    )
    ativo = models.CharField(max_length=250)
    tipo_provento = models.CharField(max_length=250, choices=TIPO_PROVENTOS)
    data = models.DateField()
    valor = models.DecimalField(max_digits=10,decimal_places=2)
    user = models.ForeignKey(User,  on_delete=models.PROTECT, verbose_name="Usuário")
    
    def save(self, *args, **kwargs):
        return super(Proventos, self).save(*args, **kwargs)
    def __str__(self):
        return self.ativo

# Create models Ativo
class Ativo(models.Model):
    ativo = models.CharField(max_length=250)
    quantidade = models.IntegerField(validators=[MinValueValidator(0)])
    preco_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço Total')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs )
    
    def __str__(self):
        return self.ativo

def get_absolute_url(self):
    from django.urls import reverse
    return reverse("cadastrar-nota")

class Desdobramento(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    data = models.DateField()
    a_cada = models.IntegerField()
    desdobra_se = models.IntegerField(verbose_name='Desdobra-se em')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')
    data_instante = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        return super(Desdobramento, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.ativo.ativo

class Bonificacao(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    data = models.DateField()
    a_cada = models.IntegerField()
    recebo_bonus_de = models.IntegerField()
    custo_atribuido = models.DecimalField(max_digits=10,decimal_places=2, verbose_name='Custo Atribuído')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    data_instante = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        return super(Bonificacao, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.ativo.ativo

class Grupamento(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    data = models.DateField()
    a_cada = models.IntegerField()
    agrupa_se = models.IntegerField(verbose_name='Agrupa-se em')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    data_instante = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        return super(Grupamento, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.ativo.ativo