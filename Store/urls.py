from django.urls import path
from django.contrib.auth import views
from .views import *


urlpatterns = [
    path('', homepage, name='homepage'),
    path('loja/', store, name='store'),

    # valor dinâmico para urls. Views ->  nome_categoria=None
    path('loja/<str:filter>/', store, name='store'),
    path('produto/<int:id_product>/', show_product, name='show_product'),
    path('produto/<int:id_product>/<int:id_color>/',
         show_product, name='show_product'),

    path('carrinho/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('adicionarcarrinho/<int:id_product>/', add_cart, name='add_cart'),
    path('removercarrinho/<int:id_product>/', remove_cart, name='remove_cart'),
    path('adicionarendereco/', add_address, name='add_address'),
    path('finalizarpedido/<int:order_id>/', finalize_order, name='finalize_order'),
    path('finalizarpagamento/', finalize_payment, name='finalize_payment'),
    path('pedidoaprovado/<int:order_id>/', approve_order, name='approve_order'),

    path('minhaconta/', account, name='account'),
    path('meuspedidos/', my_orders, name='my_orders'),
    path('login/', sign_in, name='sign_in'),
    path('criarconta/', create_account, name='create_account'),
    path('fazerlogout/', logout_session, name='logout_session'),

    path('gerenciarloja/', manage_store, name='manage_store'),
    path('exportarrelatorio/<str:report>/', export_report, name='export_report'),
   

    path("password_change/", views.PasswordChangeView.as_view(),
         name="password_change"),
    path("password_change/done/", views.PasswordChangeDoneView.as_view(),
         name="password_change_done"),

    path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", views.PasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("reset/done/", views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),
]
