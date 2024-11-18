import csv
from django.db.models import Max, Min
from django.core.mail import send_mail
from django.http import HttpResponse



def filter_products(products, filter):
    if filter:
        if "-" in filter:
            category, type = filter.split("-")
            products = products.filter(
                type__slug=type, category__slug=category)
        else:
            # (nomedocampo__parâmetro)
            products = products.filter(category__slug=filter)

    return products


def minimum_maximum_price(products):
    minimum = 0
    maximum = 0
    if len(products) > 0:
        # campo price do 'model' Product
        maximum = list(products.aggregate(Max("price")).values())[0]
        # maximum = round(maximum, 2)

        minimum = list(products.aggregate(Min("price")).values())[0]
        # minimum = round(minimum, 2)
        # minimum = products.aggregate(Min('price'))['price__min']
    return minimum, maximum

def order_products(products, order):
    if order == "menor-preco":
        products = products.order_by("price")
    elif order == "maior-preco":
        products = products.order_by("-price")
        
    # Ordenar - Mais Vendidos
    # Se não tiver nenhum produto vendido, dá erro
    elif order == "mais-vendidos":
        product_list = []
        for product in products:
            product_list.append((product.total_sales(), product))
            
        # Para não dar ERRO de ter dois ou + produtos com a msm qtd de vendas
        # A referência vai ser o primeiro item da tupla para ordenar, e não o segundo  
        product_list = sorted(product_list, reverse=True, key=lambda x: x[0])
        '''Mesma coisa de: 
                        def key_order(x):
                            return x[0]'''
        product = [item[1] for item in product_list]
            # print(product.name, product.total_sales())
    return products


def send_purchase_email(order):
    email = order.customer.email
    subject = f"Pedido Aprovado: {order.id}"
    body = f"""Parabéns! Seu pedido foi aprovado.
    ID do pedido: {order.id}
    Quantidade de produtos: {order.total_quantity}
    Valor total: {order.total_price}"""
    sender = "testcodedevsandbox@gmail.com"
    send_mail(subject, body, sender, [email])

def export_csv(info):
    columns = info.model._meta.fields
    columns_names = [column.name for column in columns]

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = "attachment; filename=export.csv"

    # Inclui o indicador BOM para suportar UTF-8 em leitores como Excel
    response.write("\ufeff")
    
    csv_writer = csv.writer(response, delimiter=";")
    csv_writer.writerow(columns_names)

    # Linhas do CSV
    for row in info.values_list():
        csv_writer.writerow(row)
    
    return response