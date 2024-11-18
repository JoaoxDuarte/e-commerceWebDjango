# Disponibilizar para tds em settings, TEMPLATES ('Store.new_context.cart')
# new_context pode pesar dependendo do há contido nele
from .models import Order, OrderItem, Customer, Category, Type


# TODO: Verifica se o user está associado:
def cart(request):
    cart_product_quantity = 0
    customer = None

    if request.user.is_authenticated:
        # Verifica se o usuário tem um perfil 'customer' associado
        customer = getattr(request.user, 'customer', None)
    else:
        if request.COOKIES.get("session_id"):
            session_id = request.COOKIES.get("session_id")
            customer, created = Customer.objects.get_or_create(
                session_id=session_id)
        else:
            # Retorna 0 (zero) se não houver session_id
            return {"cart_product_quantity": cart_product_quantity}

    # Se não houver customer, retorna 0 (zero) ou trata de forma adequada
    if customer is None:
        return {"cart_product_quantity": cart_product_quantity}

    # get_or_create = entrega o pedido e se foi criado ou não
    order, created = Order.objects.get_or_create(
        customer=customer, finished=False)  # pedidos do usuário
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        cart_product_quantity += item.quantity
    return {"cart_product_quantity": cart_product_quantity}

# cart_product_quantity para mostrar o n° de itens no carrinho


# Para barra de pesquisa e para fazer um FOR em navbar.html
def category_types(request):
    navigation_categories = Category.objects.all()
    navigation_types = Type.objects.all()
    return {"navigation_categories": navigation_categories, "navigation_types": navigation_types}

def is_staff_member(request):
    staff = False
    if request.user.is_authenticated:
        if request.user.groups.filter(name="Equipe").exists():
            staff = True
    return {"staff": staff}