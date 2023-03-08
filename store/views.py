from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from .forms import CreateUserForm, CustomerForm, ProductForm, OrderForm
from django.contrib import messages
from .filters import OrderFilter
from .decorators import allowed_user, admin_only

# Create your views here.


def registerPage(request):
	if request.user.is_authenticated:
		return redirect('store')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				user = form.save()
				username = form.cleaned_data.get('username')
				email = form.cleaned_data.get('email')

				group = Group.objects.get(name='customer')
				user.groups.add(group)
				Customer.objects.create(
					user=user,
					email=email
					)

				messages.success(request, 'Account was created for' + ' ' + username )
				return redirect('login')
		context ={'form': form}
		return render(request, 'store/register.html', context)


def loginPage(request):
	if request.user.is_authenticated:
		return redirect('store')
	else:	
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				if user.is_staff:
					return redirect('admin')
				else: 
					return redirect('store')
			else:
				messages.info(request, "Username or password is incorrect")	
		context ={}
		return render(request, 'store/login.html', context)


def logoutPage(request):
	logout(request)
	return redirect('store')




def store(request):

	data = cartData(request)
	cartItems = data['cartItems']

	products = Product.objects.all().order_by('-id')
	context = {'products': products, 'cartItems': cartItems}
	return render(request, 'store/store.html', context)


def cart(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items, 'order': order, 'cartItems': cartItems}
	return render(request, 'store/cart.html', context)


def checkout(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items, 'order': order, 'cartItems': cartItems}
	return render(request, 'store/checkout.html', context,)		


def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)
	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()
	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		

	else:
		customer, order = guestOrder(request, data)
		
	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == float(order.get_cart_total):
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
			customer = customer,
			order = order,
			address = data['shipping']['address'],
			city = data['shipping']['city'],
			state = data['shipping']['state'],
			zipcode = data['shipping']['zipcode'],
			)

	return JsonResponse('Payment submitted', safe=False)


@login_required(login_url='login')
def customer(request, pk):
	data = cartData(request)
	cartItems = data['cartItems']


	customer = Customer.objects.get(id=pk)
	orders = customer.order_set.filter(complete=True).order_by('-date_ordered')
	order_count = orders.count()
	myFilter = OrderFilter(request.GET, queryset=orders)
	orders = myFilter.qs
	context = {'customer': customer, 'orders': orders, 'order_count': order_count,
	 'myFilter': myFilter, 'cartItems': cartItems}
	return render(request, 'store-manage/customer.html', context)


@login_required(login_url='login')
def customerUpdate(request):
	data = cartData(request)
	cartItems = data['cartItems']

	customer = request.user.customer
	form = CustomerForm(instance=customer)
	if request.method == 'POST':
		form = CustomerForm(request.POST, instance=customer)
		if form.is_valid():
			form.save()
			return redirect('customer', pk=customer.id)	

	context = {'form': form, 'cartItems': cartItems}
	return render(request, 'store/customer_form.html', context)



#ADMIN

@login_required(login_url='login')
@admin_only
def adminDashboard(request):
	orders = Order.objects.filter(complete=True).order_by('-date_ordered')
	customers = Customer.objects.all()
	products = Product.objects.all().order_by('-id')
	total_products = Product.objects.count()
	total_customers = customers.count()
	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	delivering = orders.filter(status='Out for delivery').count()
	pending = orders.filter(status='Pending').count()

	context = {'orders': orders, 'customers': customers,
	'total_orders': total_orders, 'total_customers': total_customers,
	'delivered': delivered, 'pending':pending, 'delivering':delivering,
	'products': products, 'total_products': total_products
	}
	return render(request, 'store-manage/dashboard.html', context)


@login_required(login_url='login')
@admin_only
def createProduct(request):
	form = ProductForm()
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('admin')
	context = {'form':form}
	return render(request, 'store-manage/product_form.html', context)


@login_required(login_url='login')
@admin_only
def updateProduct(request, pk):
	product = Product.objects.get(id=pk)
	form = ProductForm(instance=product)
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES, instance=product)
		if form.is_valid():
			form.save()
			return redirect('admin')
	context={'form':form}
	return render(request, 'store-manage/product_form.html', context)


@login_required(login_url='login')
@admin_only
def deleteProduct(request, pk):
	product = Product.objects.get(id=pk)
	if request.method == 'POST':
		product.delete()
		return redirect('admin')
	context = {'product':product}
	return render(request, 'store-manage/delete_product.html', context)


@login_required(login_url='login')
def orderDetails(request, pk):
	order = Order.objects.get(id=pk)
	shipping = ShippingAddress.objects.get(order=order)
	orderitem = order.orderitem_set.all()
	context = {'order':order, 'shipping':shipping, 'orderitem':orderitem}
	return render(request, 'store-manage/order_details.html', context)


@login_required(login_url='login')
@admin_only
def updateOrder(request, pk):
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)
	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('admin')


	context = {'form':form}
	return render(request, 'store-manage/product_form.html', context)


@login_required(login_url='login')
@admin_only
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == 'POST':
		order.delete()
		return redirect('admin')
	context = {'order':order}
	return render(request, 'store-manage/delete_order.html', context)


@login_required(login_url='login')
@admin_only
def customerDetails(request, pk):
	customer = Customer.objects.get(id=pk)
	orders = customer.order_set.filter(complete=True).order_by('-date_ordered')
	order_count = orders.count()
	myFilter = OrderFilter(request.GET, queryset=orders)
	orders = myFilter.qs
	context = {'customer': customer, 'orders': orders, 'order_count': order_count, 'myFilter': myFilter}
	return render(request, 'store-manage/customer_details.html', context)





