import os
import mercadopago
from dotenv import load_dotenv

# ATENÇÃO #
# Chave e token no .env
# TODO: mudar credenciais de TESTE  # pylint: disable=fixme
load_dotenv()
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
TOKEN = os.getenv('TOKEN')


def create_payment(order_items, link):
    # Configurar credenciais
    sdk = mercadopago.SDK(TOKEN)

    items = []
    for item in order_items:
        quantity = int(item.quantity)
        product_name = item.stock_item.product.name
        unit_price = float(item.stock_item.product.price)
        # add dicionário
        items.append({
            "title": product_name,
            "quantity": quantity,
            "unit_price": unit_price,
        })
    # total price/valor total
    preference_data = {
        "items": items,
        "auto_return": "all",
        "back_urls": {
            "success": link,
            "pending": link,
            "failure": link,
        }
    }
    preference_response = sdk.preference().create(preference_data)
    payment_link = preference_response["response"]["init_point"]
    payment_id = preference_response["response"]["id"]
    return payment_link, payment_id
