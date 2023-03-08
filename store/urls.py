from django.urls import path
from . import views


urlpatterns = [
	path('', views.store, name = 'store'),
	path('cart/', views.cart, name = 'cart'),
	path('checkout/', views.checkout, name = 'checkout'),
	path('update_item/', views.updateItem, name = 'update_item'),
	path('process_order/', views.processOrder, name = 'process_order'),
	path('login/', views.loginPage, name = 'login'),
	path('register/', views.registerPage, name = 'register'),
	path('logout/', views.logoutPage, name = 'logout'),

	#admin begins here

	path('admin_dashboard/', views.adminDashboard, name = 'admin'),
	path('create_product/', views.createProduct, name = 'create-product'),
	path('update_product/<str:pk>', views.updateProduct, name = 'update-product'),
	path('delete_product/<str:pk>', views.deleteProduct, name = 'delete-product'),

	path('orderDetails/<str:pk>', views.orderDetails, name = 'order'),
	path('update_order/<str:pk>', views.updateOrder, name = 'update-order'),
	path('delete_order/<str:pk>', views.deleteOrder, name = 'delete-order'),

	path('customer/<str:pk>', views.customerDetails, name = 'customer-details'),
	path('customer_details/<str:pk>', views.customer, name = 'customer'),
	path('customer_update', views.customerUpdate, name = 'customer-update')
]