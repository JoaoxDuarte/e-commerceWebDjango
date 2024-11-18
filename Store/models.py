import re
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


'''session_id, pois o cliente pode add itens msm sem estar logado'''


class Customer(models.Model):
    name = models.CharField(max_length=60, null=True,
                            blank=True, verbose_name=_('Nome'))
    user = models.OneToOneField(User, null=True, blank=True,
                                on_delete=models.CASCADE, verbose_name=_('Usuário'))  # Exclui o Customer se o User for excluído
    session_id = models.CharField(
        max_length=60, null=True, blank=True, verbose_name=_('ID da Sessão'))
    email = models.CharField(max_length=60, null=True, blank=True, validators=[
                             EmailValidator(message='Coloque um endereço válido.')])
    phone = models.CharField(
        max_length=15, null=True, blank=True, verbose_name=_('Telefone'),
        validators=[
            RegexValidator(
                regex=r'^(?:\+55\s)?(?:\(\d{2}\)\s|\d{2}\s)?(?:\d{4,5}-\d{4}|\d{4,5}\s\d{4}|\d{10,11}|\d{2}\s\d{8,9})$',
                message='Número de telefone inválido. Por favor, use um dos formatos permitidos: +55 (XX) XXXX-XXXX, +55 (XX) XXXXX-XXXX, (XX) XXXX-XXXX, (XX) XXXXX-XXXX, XX XXXX-XXXX, XX XXXXX-XXXX, XX XXXXXXXXXX ou XX XXXXXXXXX'
            ),
        ],
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"Email: {self.email} - Cliente: {self.name}"


class Category(models.Model):
    name = models.CharField(max_length=60, null=True,
                            blank=True, verbose_name=_('Nome'))
    slug = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return str(self.name)


class Type(models.Model):  # Tipos (camisa, camiseta, bermuda, calça)
    name = models.CharField(max_length=60, null=True,
                            blank=True, verbose_name=_('Nome'))
    slug = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        verbose_name = "Tipo"
        verbose_name_plural = "Tipos"

    def __str__(self):
        return str(self.name)


# PRODUTO
class Product(models.Model):
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Categoria'))
    type = models.ForeignKey(
        Type, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Tipo'))
    img = models.ImageField(null=True, blank=True, verbose_name=_('Imagem'))
    name = models.CharField(max_length=60, null=True,
                            blank=True, verbose_name=_('Nome'))
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_('Preço'))
    active = models.BooleanField(default=True, verbose_name=_('Ativo'))

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return f"Nome: {self.name}, Categoria: {self.category}, Tipo: {self.type}, Preço: {self.price}"

    def total_sales(self):
        # OrderItem <- stock_item <- product A.54
        items = OrderItem.objects.filter(
            order__finished=True, stock_item__product=self.id)
        # pegando item.quantity e somando todo mundo
        total = sum([item.quantity for item in items])
        return total


def validate_hex_color(value):
    if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
        raise ValidationError(
            'O código hexadecimal da cor deve estar no formato #RRGGBB')
    if len(value) != 7:
        raise ValidationError(
            'O código hexadecimal da cor deve ter exatamente 6 dígitos')


class Color(models.Model):
    name = models.CharField(max_length=60, null=True,
                            blank=True, verbose_name=_('Nome'))
    code = models.CharField(max_length=7, null=True,
                            blank=True, verbose_name=_('Código'), validators=[validate_hex_color])

    class Meta:
        verbose_name = "Cor"
        verbose_name_plural = "Cores"

    def __str__(self):
        return str(self.name)


class StockItem(models.Model):
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Produto'))
    color = models.ForeignKey(Color, null=True,
                              blank=True, on_delete=models.SET_NULL, verbose_name=_('Cor'))
    size = models.CharField(max_length=60, null=True,
                            blank=True, verbose_name=_('Tamanho'))
    # Produto sem nenhum item no estoque
    quantity = models.IntegerField(default=0, verbose_name=_('Quantidade'))

    class Meta:
        verbose_name = "Item em Estoque"
        verbose_name_plural = "Itens em Estoque"

# Para mostra os itens com o nome e ñ como objects durante a seleção
    def __str__(self):
        return f"{self.product.name}, Tamanho: {self.size}, Cor: {self.color.name}"


class Address(models.Model):
    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Cliente'))
    number = models.IntegerField(default=0, verbose_name=_('Número'))
    street = models.CharField(
        max_length=300, null=True, blank=True, verbose_name=_('Rua'))
    complement = models.CharField(
        max_length=60, blank=True, null=True, verbose_name=_('Complemento'))
    city = models.CharField(max_length=60, blank=True,
                            null=True, verbose_name=_('Cidade'))
    state = models.CharField(max_length=60, blank=True,
                             null=True, verbose_name=_('Estado'))
    postal_code = models.CharField(max_length=10, verbose_name=_('CEP'),
                                   validators=[
                                       RegexValidator(
                                           regex=r'^\d{5}-\d{3}$|^\d{8}$',
                                           message=_(
                                               'CEP inválido. Por favor, use o formato: XXXXX-XXX ou XXXXXXXX'),
                                       ),
    ]
    )

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.customer} - {self.street} - {self.city}-{self.state} - {self.postal_code}"


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Cliente'))
    address = models.ForeignKey(Address, null=True, blank=True,
                                on_delete=models.SET_NULL, verbose_name=_('Endereço'))
    finished = models.BooleanField(default=False, verbose_name=_('Finalizado'))
    transaction_code = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_('Código de Transação'))
    completion_date = models.DateTimeField(
        null=True, blank=True, verbose_name=_('Data de Conclusão'))

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Cliente: {self.customer.email} - id_pedido: {self.id} - Finalizado {self.finished}"

    @property
    def total_quantity(self):
        order_items = OrderItem.objects.filter(order__id=self.id)
        # Vai criar uma lista para cd item dentro da lista order_items e vai pegar o item.quantity
        quantity = sum([item.quantity for item in order_items])
        return quantity

    # TORAL PRICE
    @property
    def total_price(self):
        order_items = OrderItem.objects.filter(order__id=self.id)
        price = sum([item.total_price for item in order_items])
        return price

    @property
    def items(self):
        order_items = OrderItem.objects.filter(order__id=self.id)
        return order_items


class OrderItem(models.Model):
    stock_item = models.ForeignKey(
        StockItem, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Item em Estoque'))
    order = models.ForeignKey(Order,
                              null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Pedido'))
    quantity = models.IntegerField(default=0, verbose_name=_('Quantidade'))

    class Meta:
        verbose_name = "Item Pedido"
        verbose_name_plural = "Itens Pedidos"

    def __str__(self):
        return f"ID pedido: {self.order.id} - Produto: {self.stock_item.product.name}, {self.stock_item.size}, {self.stock_item.color.name} "

    # CALCULAR PREÇO TOTAL. Property para usar como um campo do elemento e não uma função
    @property
    def total_price(self):  # StockItem tem o produto e o Product tem o preço (price)
        return self.quantity * self.stock_item.product.price


class Banner(models.Model):
    img = models.ImageField(null=True, blank=True, verbose_name=_('Imagem'))
    link = models.CharField(max_length=400, null=True, blank=True)
    active = models.BooleanField(default=False, verbose_name=_('Ativo'))

# para mostrar se o banner está ativo durante a seleção
    def __str__(self):
        return f"{self.link} - Ativo: {self.active}"


class Payment(models.Model):
    order = order = models.ForeignKey(Order,
                                      null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Pedido'))
    payment_id = models.CharField(max_length=400, null=True, blank=True)
    approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
