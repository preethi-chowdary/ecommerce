from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('register/', views.registerPage, name="register"),
	path('login/', views.loginPage, name="login"),
	path('logout/', views.logoutUser, name="logout"),

	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('product/<pk>/', views.product, name="product"),
	path('search/', views.search, name="search"),
	path('about_us/',views.about_us,name="about_us"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),

]
