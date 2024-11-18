import uuid  # n° aleató. sem repetir
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import *
# from .models import Product, Banner
from .utils import filter_products, minimum_maximum_price, order_products, send_purchase_email, export_csv
from .api_mercadopago import create_payment


def homepage(request):
    banners = Banner.objects.filter(active=True)
    context = {"banners": banners}
    return render(request, 'homepage.html', context)


''' Outro jeito de fazer o def store ->
def store(request, nome_categoria=None):
    products = Product.objects.filter(active=True)
    if nome_categoria:
        # GET: encontra apenas 1 item como resposta, se n encontar, retorna None. 
        # Necessário try 
        # try:
            category = Category.objects.get(name=nome_categoria)
        except:
        products = products.filter(category=category)
    context = {"products": products}
    return render(request, 'store.html', context)
'''


def store(request, filter=None):
    # Dicionário para o template <queryset>
    products = Product.objects.filter(active=True)
    # Regra de filtro avançado para url categoria
    products = filter_products(products, filter)
    # Aplicar filtros do form:
    if request.method == "POST":
        # data = request.POST.dict() = dados da requisição
        data = request.POST.dict()
        products = products.filter(price__gte=data.get(
            "minimum_price"), price__lte=data.get("maximum_price"))
        if "size" in data:
            items = StockItem.objects.filter(
                product__in=products, size=data.get("size"))
            ids_products = items.values_list("product", flat=True).distinct()
            products = products.filter(id__in=ids_products)
        if "type" in data:
            products = products.filter(type__slug=data.get("type"))
        if "category" in data:
            products = products.filter(category__slug=data.get("category"))

    # Pegar diferentes tamanhos com qtd > 0, bem como tds os produtos, com product presente em products:
    items = StockItem.objects.filter(quantity__gt=0, product__in=products)
    # DISTINCT para pegar v. únicos
    sizes = items.values_list("size", flat=True).distinct()
    ids_categories = products.values_list("category", flat=True).distinct()
    categories = Category.objects.filter(id__in=ids_categories)

    # Filtrar  itens por cor
    '''ids_colors = items.values_list("color", flat=True).distinct()
    colors = Color.objects.filter(id__in=ids_colors)'''

    minimum, maximum = minimum_maximum_price(products)

    # Menor e Maior Preço (utils.py)
    order = request.GET.get("ordem", "menor-preco")
    products = order_products(products, order)

    context = {"products": products, "minimum": f"{minimum:.2f}",
               "maximum": f"{maximum:.2f}", "sizes": sizes, "categories": categories}
    return render(request, 'store.html', context)


def show_product(request, id_product, id_color=None):
    in_stock = False
    colors = {}
    sizes = {}
    selection_color = None
    if id_color:
        selection_color = Color.objects.get(id=id_color)
    product = Product.objects.get(id=id_product)

    ''' Filtrar produtos que tenham qtd maior que 0. quantity=0 (msm coisa de: quantity > 0) 
    pois segue as regras do django'''
    stock_item = StockItem.objects.filter(product=product, quantity__gt=0)
    if len(stock_item) > 0:
        in_stock = True
        # armazena item.color que tem no estoque, como 'set'. É SET {} para não pegar cores duplicadas, como ocorre com listas:
        colors = {item.color for item in stock_item}
        if id_color:
            stock_item = StockItem.objects.filter(
                product=product, quantity__gt=0, color__id=id_color)
            sizes = {item.size for item in stock_item}
        '''else:
            quantites = {}
    else:
        in_stock = False
        colors = {}
        quantities = {}'''
    context = {"product": product, "in_stock": in_stock,
               "colors": colors, "sizes": sizes, "selection_color": selection_color}
    return render(request, 'show_product.html', context)


def add_cart(request, id_product):
    if request.method == "POST" and id_product:
        data = request.POST.dict()
        size = data.get("size")
        id_color = data.get("color")
        if not size:
            return redirect('store')

        # Pegar o cliente
        response = redirect('cart')
        if request.user.is_authenticated:
            customer, created = Customer.objects.get_or_create(
                user=request.user)
            # customer = request.user.customer
        else:
            # Só armazena session_id se não tiver um
            if request.COOKIES.get('session_id'):
                session_id = request.COOKIES.get("session_id")
            else:
                session_id = str(uuid.uuid4())
                # Para o cookie do navegador. Durar 1 dia
                response.set_cookie(
                    key="session_id", value=session_id, max_age=60*60*24*30)
            customer, created = Customer.objects.get_or_create(
                session_id=session_id)

         # Obter ou criar o pedido em aberto para o cliente
        order, created = Order.objects.get_or_create(
            customer=customer, finished=False)

        # Tenta buscar o item em estoque com o produto, tamanho e cor
        try:
            stock_item = StockItem.objects.get(
                product__id=id_product, size=size, color__id=id_color)
        except StockItem.DoesNotExist:
            return redirect('store')

        # Criar o Pedido ou pegar o pedido aberto
        order_item, created = OrderItem.objects.get_or_create(
            stock_item=stock_item, order=order)
        # Editando e salvando o elemento
        order_item.quantity += 1
        order_item.save()
        return response
    else:
        return redirect('store')


def remove_cart(request, id_product):
    if request.method == "POST" and id_product:
        data = request.POST.dict()
        size = data.get("size")
        id_color = data.get("color")
        # Se ñ tiver tamanho, redireciona
        if not size:
            return redirect('store')
        # Pegar o cliente
        if request.user.is_authenticated:
            customer = request.user.customer
        else:
            if request.COOKIES.get("session_id"):
                session_id = request.COOKIES.get("session_id")
                customer, created = Customer.objects.get_or_create(
                    session_id=session_id)
            else:
                return redirect('store')
        order, created = Order.objects.get_or_create(
            customer=customer, finished=False)
        stock_item = StockItem.objects.get(product__id=id_product, size=size,
                                           color__id=id_color)
        # Criar o Pedido ou pegar o pedido aberto
        order_item, created = OrderItem.objects.get_or_create(
            stock_item=stock_item, order=order)
        # Editando e salvando o elemento
        order_item.quantity -= 1
        order_item.save()

        # Para não ficar com o carrinho NEGATIVO:
        if order_item.quantity <= 0:
            order_item.delete()
        return redirect('cart')
    else:
        return redirect('store')


def cart(request):
    # User deve estar longado
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        if request.COOKIES.get("session_id"):
            session_id = request.COOKIES.get("session_id")
            customer, created = Customer.objects.get_or_create(
                session_id=session_id)
        else:
            context = {"existing_customer": False,
                       "order_items": None, "order": None}
            return render(request, 'cart.html', context)

    order, created = Order.objects.get_or_create(
        customer=customer, finished=False)
    order_items = OrderItem.objects.filter(order=order)
    '''for item in order_items:
        print(item.total_price)'''
    context = {"order_items": order_items,
               "order": order, "existing_customer": True}
    return render(request, 'cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        if request.COOKIES.get("session_id"):
            session_id = request.COOKIES.get("session_id")
            customer, created = Customer.objects.get_or_create(
                session_id=session_id)
        else:
            return redirect('store')

    order, created = Order.objects.get_or_create(
        customer=customer, finished=False)
    addresses = Address.objects.filter(customer=customer)
    context = {"order": order, "addresses": addresses, "error": None}
    return render(request, 'checkout.html', context)

# Para finalizar o pedido é preciso: Endereço e Email


def finalize_order(request, order_id):
    if request.method == "POST":
        error = None
        data = request.POST.dict()

        # Para Não Burlar o Sistema (ex: HTML)
        # Verificar se "total" (do form) é igual ao "order_id" (do banco de dados)
        total = data.get("total")
        total = float(total.replace(",", "."))
        order = Order.objects.get(id=order_id)

        # float pois em Models ele é um Decimal
        if total != float(order.total_price):
            error = "nonexistent_price"

        # Verifica endereço
        if not "address" in data:
            error = "nonexistent_address"
        else:
            address_id = data.get("address")
            address = Address.objects.get(id=address_id)
            order.address = address

        # Verifica email
        if not request.user.is_authenticated:
            email = data.get("email")
            try:
                validate_email(email)
            except ValidationError:
                error = "nonexistent_email"
            # Busca o cliente pelo email
            if not error:
                # devolve como resposta uma lista de clientes
                customers = Customer.objects.filter(email=email)
                # Se a lista não for vazia -> muda o cliente do pedido caso ele já exista -> associa com primeiro cliente encontrado
                if customers:
                    order.customer = customers[0]

                # Se nenhum cliente for encontrado, um novo cliente é criado ou atualizado
                else:
                    order.customer.email = email
                    order.customer.save()
        # Data/hora atual no formato EPOCH
        transaction_code = f"{order.id}-{datetime.now().timestamp()}"
        order.transaction_code = transaction_code

        order.save()

        if error:
            # O cliente aqui é o order.customer
            addresses = Address.objects.filter(customer=order.customer)
            context = {"error": error, "order": order, "addresses": addresses}
            return render(request, 'checkout.html', context)
        else:
            # Pagamento do usuário (User - API)
            # Pega todos os itens do pedido:
            order_items = OrderItem.objects.filter(order=order)
            # reverse: pega ele pega o nome da url e dá um link relativo
            # build_absolute_uri: é o domínio e dps junto os 2
            link = request.build_absolute_uri(reverse("finalize_payment"))
            payment_link, payment_id = create_payment(order_items, link)
            payment = Payment.objects.create(
                payment_id=payment_id, order=order)
            payment.save()
            return redirect(payment_link)
    else:
        return redirect("store")


def finalize_payment(request):
    data = request.GET.dict()
    status = data.get("status")
    payment_id = data.get("preference_id")
    if status == "approved":
        payment = Payment.objects.get(payment_id=payment_id)
        payment.approved = True
        # Pedido associado ao cliente
        order = payment.order
        order.finished = True
        order.completion_date = datetime.now()
        order.save()
        payment.save()

        send_purchase_email(order)

        if request.user.is_authenticated:
            return redirect("my_orders")
        else:
            return redirect("order_approved", order.id)
    # Caso o pedido NÃO seja Aprovado:
    else:
        return redirect("checkout")


def approve_order(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {"order": order}
    return render(request, "order_approved.html", context)


def add_address(request):
    if request.method == "POST":
        # tratar o envio do form
        if request.user.is_authenticated:
            customer = request.user.customer  # está com o login feito
        else:
            if request.COOKIES.get("session_id"):
                session_id = request.COOKIES.get("session_id")
                customer, created = Customer.objects.get_or_create(
                    session_id=session_id)
            else:
                return redirect('store')
        data = request.POST.dict()
    # user vai inserir o endereço que quiser. Ñ vamos bloquear
    # number=int(data.get("number")) para vir como TEXTO
        address = Address.objects.create(customer=customer, street=data.get("street"),
                                         number=data.get("number"), state=data.get("state"), city=data.get("city"),
                                         complement=data.get("complement"), postal_code=data.get("postal_code"))
        return redirect('checkout')

    else:
        context = {}
        return render(request, 'add_address.html', context)


@login_required
def account(request):
    changed = False
    error = None

    if request.method == "POST":
        data = request.POST.dict()
        if "current_password" in data:
            # Esta modificando a senha
            current_password = data.get("current_password")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")
            if new_password == confirm_password:
                # verifica se current_password ta certa (63):
                user = authenticate(
                    request, username=request.user.email, password=current_password)
                # senha correta:
                if user:
                    user.set_password(new_password)
                    user.save()
                    changed = True
                else:
                    # Account.html
                    error = "incorrect_passwords"

            else:
                error = "different_passwords"

        elif "email" in data:
            # Esta modificando dados pessoais
            email = data.get("email")
            phone = data.get("phone")
            name = data.get("name")

            # EMAIL
            if email != request.user.email:
                users = User.objects.filter(email=email)
                if len(users) > 0:
                    error = "existing_email"

            if not error:
                customer = request.user.customer
                customer.email = email
                request.user.email = email
                request.user.username = email
                customer.name = name
                customer.phone = phone
                customer.save()
                request.user.save()
                changed = True
        else:
            error = "filling"
    context = {"error": error, "changed": changed}
    return render(request, 'user/account.html', context)


@login_required
def my_orders(request):
    customer = request.user.customer
    orders = Order.objects.filter(
        finished=True, customer=customer).order_by("-completion_date")
    context = {"orders": orders}
    return render(request, 'user/my_orders.html', context)


# TODO: Lembrar // Django usa o username como auth // Cliente é criado ao criar conta
def sign_in(request):
    error = False
    if request.user.is_authenticated:
        return redirect('store')
    elif request.method == "POST":
        data = request.POST.dict()
        if "email" in data and "password" in data:
            email = data.get("email")
            password = data.get("password")
            user = authenticate(request, username=email, password=password)

            if user:
                # Faz login
                login(request, user)
                return redirect('store')
            else:
                error = True

        else:
            error = True

    context = {"error": error}
    return render(request, 'user/login.html', context)


def create_account(request):
    error = None
    if request.user.is_authenticated:
        return redirect('store')
    if request.method == "POST":
        data = request.POST.dict()
        # Formas de verificar:
        # if "email" in data and "password" in data and "password_confirm" in data:
        # if "email" != "" and "password" != "" and "confirm_password" != "":
        # TODO: função all()
        if all(key in data and data[key] != "" for key in ["email", "password", "confirm_password"]):
            email = data.get("email")
            password = data.get("password")
            password_confirm = data.get("password_confirm")
            try:
                validate_email(email)
            except ValidationError:
                error = "invalid_email"
            if password == password_confirm:
                # cria conta // username=email, email=email
                user, created = User.objects.get_or_create(
                    username=email, email=email)
                if not created:
                    error = "existing_user"
                else:
                    user.set_password(password)
                    user.save()

                    # FAZ LOGIN DO USER:
                    user = authenticate(
                        request, username=email, password=password)
                    login(request, user)

                    # CRIA CLIENTE
                    # Verificar se existe session_id nos cookies
                    if request.COOKIES.get("session_id"):
                        session_id = request.COOKIES.get("session_id")
                        customer, created = Customer.objects.get_or_create(
                            session_id=session_id)
                    else:
                        customer, created = Customer.objects.get_or_create(
                            email=email)
                    customer.user = user
                    customer.email = email
                    customer.save()
                    return redirect('store')
            else:
                error = "different_passwords"

        else:
            error = "filling"
    context = {"error": error}
    return render(request, 'user/create_account.html', context)


@login_required
def logout_session(request):
    logout(request)
    return redirect('store')


@login_required
def manage_store(request):
    if request.user.groups.filter(name="Equipe").exists():
        # Tabela Order
        completed_orders = Order.objects.filter(finished=True)

        order_quantity = len(completed_orders)
        revenue = sum(order.total_price for order in completed_orders)
        product_quantity = sum(
            order.total_quantity for order in completed_orders)

        context = {"order_quantity": order_quantity, "revenue": revenue,
                   "product_quantity": product_quantity}
        return render(request, 'internal/manage_store.html', context)
    else:
        redirect('store')

@login_required
def export_report(request, report):
    if request.user.groups.filter(name="Equipe").exists():
        if report == "order":
            info = Order.objects.filter(finished=True)
        elif report == "customer":
            info = Customer.objects.all()
        elif report == "address":
            info = Address.objects.all()
        else:
            return redirect('manage_store')
        
        return export_csv(info)
    else:
        return redirect('manage_store')
