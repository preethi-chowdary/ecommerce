from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from .forms import CreateUserForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder


def registerPage(request):
	if request.user.is_authenticated:
		return redirect('store')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)

				return redirect('login')

		context = {'form': form}
		return render(request, 'store/register.html', context)
def loginPage(request):
	if request.user.is_authenticated:
		return redirect('store')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('store')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'store/login.html', context)
def logoutUser(request):
	logout(request)
	return redirect('login')
@receiver(post_save, sender=User, dispatch_uid='save_new_user_profile')
def save_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        customer = Customer(user=user)
        customer.save()
def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products': products, 'cartItems': cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	print(items)
	context = {'items': items, 'order': order, 'cartItems': cartItems}
	return render(request, 'store/cart.html', context)


def checkout(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items, 'order': order, 'cartItems': cartItems}
	return render(request, 'store/checkout.html', context)


def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

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

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)


def product(request, pk):
	product=get_object_or_404(Product, pk=pk)
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items, 'order': order, 'cartItems': cartItems,'product':product}
	return render(request, 'store/product.html', context)


def about_us(request):
	data = cartData(request)

	cartItems = data['cartItems']
	context = {'cartItems': cartItems}
	return render(request, 'store/about_us.html', context)


def search(request):
	query = request.GET.get('search_item')
	print(query)
	data = cartData(request)
	pk=1
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	#products = Product.objects.all()
	#print(products)
	object = Product.objects.filter(
		Q(name__icontains=query)
	)
	if len(object)!=0:
		pk=object[0].id
	else:
		pk=1
	product = get_object_or_404(Product, pk=pk)
	context = {'items': items, 'order': order, 'cartItems': cartItems, 'product': product}
	return render(request, 'store/product.html', context)