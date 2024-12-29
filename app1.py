from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import hashlib
import json
import os
from openai import OpenAI
from django.middleware.csrf import get_token
from client import AUBoutique

# Initialize the boutique class instance
boutique = AUBoutique()
client = OpenAI()

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Views
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        client_port = 8081  # Example port, adjust accordingly

        response = boutique.login_user(username, password, client_port)
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        else:
            request.session['username'] = username
            return redirect('home')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = boutique.register_user(first_name, last_name, email, username, password)
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        else:
            return redirect('login')


@method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request):
        return render(request, 'home.html', {"username": request.session.get('username')})


@method_decorator(login_required, name='dispatch')
class ProductsView(View):
    def get(self, request):
        response = boutique.list_products()
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        return render(request, 'products.html', {"products": response})


@method_decorator(login_required, name='dispatch')
class AddProductView(View):
    def get(self, request):
        return render(request, 'add_product.html')

    def post(self, request):
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.POST.get('image')
        quantity = request.POST.get('quantity')

        response = boutique.add_product(name, category, price, description, image, quantity)
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        return redirect('products')


@method_decorator(login_required, name='dispatch')
class SearchProductsView(View):
    def get(self, request):
        return render(request, 'search.html')

    def post(self, request):
        search_term = request.POST.get('search_term')
        response = boutique.search_product(search_term)
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        return render(request, 'search_results.html', {"products": response})


@method_decorator(login_required, name='dispatch')
class UserProductsView(View):
    def get(self, request):
        return render(request, 'user_products.html')

    def post(self, request):
        username = request.POST.get('username')
        response = boutique.search_user_products(username)
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        return render(request, 'user_products_results.html', {"products": response})


@method_decorator(login_required, name='dispatch')
class RateProductView(View):
    def get(self, request):
        return render(request, 'rate_product.html')

    def post(self, request):
        product_id = request.POST.get('product_id')
        rating = int(request.POST.get('rating'))

        response = boutique.rate_product(product_id, rating)
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        return redirect('products')


@method_decorator(login_required, name='dispatch')
class BuyProductView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        response = boutique.buy_product(product_id)
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        return redirect('products')


@method_decorator(login_required, name='dispatch')
class ViewCurrencyRatesView(View):
    def get(self, request):
        base_currency = 'USD'
        rates = boutique.get_currency_rates(base_currency)
        if "error" not in rates:
            return render(request, 'currency_rates.html', {"rates": rates})
        else:
            return JsonResponse({"error": "Failed to fetch currency rates"}, status=400)


@method_decorator(login_required, name='dispatch')
class ChatView(View):
    def get(self, request):
        return render(request, 'chat.html', {"username": request.session.get('username')})

    def post(self, request):
        receiver_username = request.POST.get('receiver_username')
        message = request.POST.get('message')

        response = boutique.p2p_chat(receiver_username, message)
        if "error" in response:
            return JsonResponse({"error": response["error"]}, status=400)
        return JsonResponse({"message": "Message sent successfully!"})


@method_decorator(login_required, name='dispatch')
class ChatGPTView(View):
    def get(self, request):
        return render(request, 'chatgpt.html')

    def post(self, request):
        user_message = request.POST.get('message')
        if not user_message:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        response = self.send_to_chatgpt(user_message)
        return JsonResponse({"response": response})

    def send_to_chatgpt(self, message):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return "API key not found."

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        )

        try:
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error communicating with ChatGPT API: {e}")
            return "Error retrieving response."


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    def get(self, request):
        request.session.flush()
        return redirect('login')

# URL Configuration
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('home/', HomeView.as_view(), name='home'),
    path('products/', ProductsView.as_view(), name='products'),
    path('add-product/', AddProductView.as_view(), name='add_product'),
    path('search-products/', SearchProductsView.as_view(), name='search_products'),
    path('user-products/', UserProductsView.as_view(), name='user_products'),
    path('rate-product/', RateProductView.as_view(), name='rate_product'),
    path('buy-product/', BuyProductView.as_view(), name='buy_product'),
    path('currency-rates/', ViewCurrencyRatesView.as_view(), name='currency_rates'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('chatgpt/', ChatGPTView.as_view(), name='chatgpt'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

# Templates (minimal examples)
# login.html
"""
<form method="post">{% csrf_token %}
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <button type="submit">Login</button>
</form>
"""

# register.html
"""
<form method="post">{% csrf_token %}
    First Name: <input type="text" name="first_name"><br>
    Last Name: <input type="text" name="last_name"><br>
    Email: <input type="email" name="email"><br>
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <button type="submit">Register</button>
</form>
"""

# home.html
"""
<h1>Welcome {{ username }}</h1>
<a href="/products/">View Products</a><br>
<a href="/add-product/">Add Product</a><br>
<a href="/search-products/">Search Products</a><br>
<a href="/user-products/">View User's Products</a><br>
<a href="/rate-product/">Rate a Product</a><br>
<a href="/currency-rates/">View Currency Rates</a><br>
<a href="/chat/">Chat</a><br>
<a href="/chatgpt/">Chat with ChatGPT</a><br>
<a href="/logout/">Logout</a>
"""

# products.html
"""
<h1>Products</h1>
<ul>
    {% for product in products %}
        <li>{{ product.name }} - {{ product.price }} USD</li>
    {% endfor %}
</ul>
<a href="/home/">Back to Home</a>
"""

# add_product.html
"""
<form method="post">{% csrf_token %}
    Name: <input type="text" name="name"><br>
    Category: <input type="text" name="category"><br>
    Price: <input type="number" name="price"><br>
    Description: <textarea name="description"></textarea><br>
    Image URL: <input type="url" name="image"><br>
    Quantity: <input type="number" name="quantity"><br>
    <button type="submit">Add Product</button>
</form>
<a href="/home/">Back to Home</a>
"""

# search.html
"""
<form method="post">{% csrf_token %}
    Search Term: <input type="text" name="search_term"><br>
    <button type="submit">Search</button>
</form>
<a href="/home/">Back to Home</a>
"""

# search_results.html
"""
<h1>Search Results</h1>
<ul>
    {% for product in products %}
        <li>{{ product.name }} - {{ product.price }} USD</li>
    {% endfor %}
</ul>
<a href="/search-products/">Back to Search</a>
"""

# user_products.html
"""
<form method="post">{% csrf_token %}
    Username: <input type="text" name="username"><br>
    <button type="submit">Search</button>
</form>
<a href="/home/">Back to Home</a>
"""

# user_products_results.html
"""
<h1>User's Products</h1>
<ul>
    {% for product in products %}
        <li>{{ product.name }} - {{ product.price }} USD</li>
    {% endfor %}
</ul>
<a href="/user-products/">Back to Search</a>
"""

# rate_product.html
"""
<form method="post">{% csrf_token %}
    Product ID: <input type="text" name="product_id"><br>
    Rating: <input type="number" name="rating" min="1" max="5"><br>
    <button type="submit">Submit Rating</button>
</form>
<a href="/products/">Back to Products</a>
"""

# currency_rates.html
"""
<h1>Currency Rates</h1>
<ul>
    {% for currency, rate in rates.items() %}
        <li>{{ currency }}: {{ rate }}</li>
    {% endfor %}
</ul>
<a href="/home/">Back to Home</a>
"""

# chat.html
"""
<h1>Chat</h1>
<form method="post">{% csrf_token %}
    To: <input type="text" name="receiver_username"><br>
    Message: <input type="text" name="message"><br>
    <button type="submit">Send</button>
</form>
<a href="/home/">Back to Home</a>
"""

# chatgpt.html
"""
<h1>Chat with ChatGPT</h1>
<form method="post">{% csrf_token %}
    Your Message: <input type="text" name="message"><br>
    <button type="submit">Send</button>
</form>
"""
