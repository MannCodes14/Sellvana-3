from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse

from userauth.models import Profile
from .models import Address, CartOrder, CartOrderItems, Product, Category, ProductReview, Vendor
from django.db.models import Count, Avg
from taggit.models import Tag
from django.contrib.auth.decorators import login_required
from .forms import ProductReviewForm
from django.db.models import Count
# import render_to_string
from django.template.loader import render_to_string
#import response
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm


# Create your views here.
from django.db.models import Count, Avg
from django.shortcuts import render
from .models import Product, Category, Vendor, ProductReview, CartOrderItems

def index(request):
    # Fetch published products
    products = Product.objects.filter(product_status="published")

    # Recently Added Products (Latest 4)
    new_products = products.order_by('-date')[:4]

    # Top Selling Products (Using CartOrderItems to count orders)
    top_selling_products = Product.objects.filter(
        id__in=CartOrderItems.objects.values_list('id', flat=True)
    ).annotate(order_count=Count('id')).order_by('-order_count')[:4]

    # Trending Products (Most reviewed)
    trending_products = products.annotate(review_count=Count('reviews')).order_by('-review_count')[:4]

    # Top Rated Products (Highest average rating)
    top_rated_products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:4]

    # Fetch categories and vendors
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    print('top_selling_products : ',top_selling_products)

    context = {
        'products': products,
        'categories': categories,
        'vendors': vendors,
        'new_products': new_products,
        'top_selling_products': top_selling_products,
        'trending_products': trending_products,
        'top_rated_products': top_rated_products,
    }

    return render(request, 'core/index.html', context)


def product_list_view(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'core/product_list.html', context)


def category_list_view(request):
    # categories = Category.objects.all()
    categories = Category.objects.all()
    products = Product.objects.filter(product_status="published")

    trending_products = products.annotate(review_count=Count('reviews')).order_by('-review_count')[:4]
    print('trending_products : ',trending_products)
    context = {
        'categories': categories,
        'trending_products': trending_products
    }
    return render(request, 'core/category_list.html', context)


def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'core/category_product_list.html', context)
    

def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        'vendors': vendors
    }
    return render(request, 'core/vendor_list.html', context)


def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    context = {
        'vendor': vendor,
        'products': products
    }
    return render(request, 'core/vendor_detail.html', context)


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    p_images = product.p_images.all()
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    # Calculating Average Rating
    review = ProductReview.objects.filter(product=product).order_by('-date')
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # Calculate rating percentages
    total_reviews = review.count()
    rating_counts = ProductReview.objects.filter(product=product).values('rating').annotate(count=Count('rating'))
    rating_percentages = {i: 0 for i in range(1, 6)}
    for rating in rating_counts:
        rating_percentages[rating['rating']] = (rating['count'] / total_reviews) * 100

    # Preduct review form
    review_form = ProductReviewForm()

    # check if user is authenticated and he has already reviewed the product
    make_review = True
    if request.user.is_authenticated:
        user_review = ProductReview.objects.filter(user=request.user, product=product)
        if user_review.exists():
            make_review = False

    context = {
        'product': product,
        'p_images': p_images,
        'products': products,
        'review': review,
        'average_rating': average_rating,
        'rating_percentages': rating_percentages,
        'review_form': review_form,
        'make_review': make_review
    }
    return render(request, 'core/product_detail.html', context)


def tag_list_view(request, tag_slug):

    products = Product.objects.filter(product_status="published").order_by('-date')
    
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])
    context = {
        'products': products,
        'tag': tag
    }
    return render(request, 'core/tag.html', context)



def ajax_add_review(request, pid):

    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user = user, 
        product = product,
        review = request.POST.get('review'),
        rating = request.POST.get('rating'),
    )

    context = {
        'user' : user.username,
        'review': request.POST['review'],
        'rating' : request.POST['rating'],

    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    return JsonResponse(
        {
            'bool' : True,
            'context' : context,
            'average_reviews' : average_reviews
        }
    )


from django.db.models import Q

def search_view(request):
    query = request.GET.get('q', '').strip()  # Get the search query from the request
    tags = request.GET.getlist('tags', [])  # Get the list of tags if any
    categories = request.GET.getlist('category[]', [])
    vendors = request.GET.getlist('vendor[]', [])
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Create a base query for title, description, and tags using Q
    search_query = Q()

    # Split the query into individual words and create search conditions for each word
    for word in query.split():
        search_query |= Q(title__icontains=word) | Q(description__icontains=word)

    # If tags are passed, add them to the query
    for tag in tags:
        search_query |= Q(tags__name__icontains=tag)

    # Filter products based on the search query
    products = Product.objects.filter(search_query, product_status="published")

    # Apply category filter if any
    if categories:
        products = products.filter(category__id__in=categories)

    # Apply vendor filter if any
    if vendors:
        products = products.filter(vendor__id__in=vendors)

    # Apply price filter if min and max prices are specified
    # if min_price and max_price:
    #     products = products.filter(price__gte=min_price, price__lte=max_price)

    # Order by most recent
    products = products.order_by('-date').distinct()

    context = {
        'products': products,
        'query': query,
        'tags': tags,
        'categories': categories,
        'vendors': vendors,
        'min_price': min_price,
        'max_price': max_price
    }

    return render(request, 'core/search.html', context)


def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Create a base query for published products
    products = Product.objects.filter(product_status="published").distinct()

    # Apply price filter if min and max prices are specified
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # Filter by categories if any
    if categories:
        products = products.filter(category__id__in=categories)

    # Filter by vendors if any
    if vendors:
        products = products.filter(vendor__id__in=vendors)

    # Order by most recent
    products = products.order_by('-date').distinct()

    # Render the filtered products to a template
    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})



def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty']) 
            cart_product.update(cart_data)
            request.session['cart_data_obj'] = cart_product
            print(request.session['cart_data_obj'])
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
            print(request.session['cart_data_obj'])
    else:
        request.session['cart_data_obj'] = cart_product
        print(request.session['cart_data_obj'])

    return JsonResponse({"data" : request.session['cart_data_obj'], 'totalCartItems' : len(request.session['cart_data_obj'])})


# New View for AI-Based Product Prediction and Tag Generation
from .ai_model import predict_image, generate_tags  # Assuming your AI functions are in ai_model.py
from django.db.models import Q

from django.core.files.storage import default_storage
def predict_product_view(request):
    if request.method == 'POST' and request.FILES['image']:
        # Save the uploaded image
        file = request.FILES['image']
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.path(file_name)

        # Predict the product using the AI model
        predicted_class = predict_image(file_url)
        if "Prediction error" in predicted_class:
            return JsonResponse({'error': predicted_class}, status=400)

        # Generate tags using Google Gemini
        tags = generate_tags(predicted_class)
        if "Error generating tags" in tags:
            return JsonResponse({'error': tags}, status=400)

        # Filter products based on the generated tags
        query = Q()
        for tag in tags.split('\n'):
            query |= Q(title__icontains=tag) | Q(description__icontains=tag) | Q(tags__name__in=[tag])
        products = Product.objects.filter(query).distinct()

        # Render the filtered products to a template
        data = render_to_string("core/async/product-list.html", {"products": products})
        return JsonResponse({
            'data': data,
            'predicted_class': predicted_class,
            'tags': tags.split('\n')
        })

    return render(request, 'core/predict_product.html')



# cart view
def cart_view(request):
    cart_total_amount = 0

    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            # Validate price before conversion
            price = item.get('price', '0')  # Default to '0' if price is missing or empty
            if price.strip():  # Check if price is not an empty string
                try:
                    cart_total_amount += int(item['qty']) * float(price)
                except ValueError:
                    # Handle invalid price (e.g., log the error or skip the item)
                    print(f"Invalid price for product {p_id}: {price}")
            else:
                # Handle empty price (e.g., log the error or skip the item)
                print(f"Empty price for product {p_id}")

        return render(request, "core/cart.html", {
            "cart_data": request.session['cart_data_obj'],
            'totalCartItems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount
        })

    else:
        messages.warning(request, "Your cart is empty")
        return redirect('core:index')


def delete_item_from_cart(request):
    product_id = str(request.GET['id'])

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del cart_data[product_id]  # Delete the product from the cart
            request.session['cart_data_obj'] = cart_data  # Update the session

    # Calculate the total cart amount
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for pid, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    # Render the updated cart template
    context = {
        "cart_data": request.session.get('cart_data_obj', {}),
        'totalCartItems': len(request.session.get('cart_data_obj')),
        'cart_total_amount': cart_total_amount,
    }
    data = render_to_string("core/async/cart-list.html", context)

    return JsonResponse({"data": data, 'totalCartItems': len(request.session.get('cart_data_obj'))})



def update_cart(request):
    product_id = str(request.GET.get('id'))
    new_quantity = int(request.GET.get('qty', 1))  # Default to 1 if quantity is not provided

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[product_id]['qty'] = new_quantity
            request.session['cart_data_obj'] = cart_data

    # Calculate the total cart amount
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    # Render the updated cart list
    context = {
        "cart_data": request.session.get('cart_data_obj', {}),
        "cart_total_amount": cart_total_amount,
    }
    cart_html = render_to_string("core/async/cart-list.html", context)

    return JsonResponse({
        "data": cart_html,
        "totalcartitems": len(request.session.get('cart_data_obj', {})),
        "cart_total_amount": cart_total_amount,
    })





@login_required
def checkout_view(request):
    # Check if cart_data_obj exists in the session
    if 'cart_data_obj' not in request.session or not request.session['cart_data_obj']:
        messages.warning(request, "Your cart is empty. Please add items to your cart before proceeding to checkout.")
        return redirect('core:cart')  # Redirect to the cart page or another appropriate page

    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': "200",  # Assuming a default amount, should be calculated
        'item_name': 'Fresh Pear',  # Should be dynamic
        'invoice': 'INV-2',  # Should be unique and dynamic
        'currency_code': 'USD',
        'notify_url': f'http://{host}{reverse("core:paypal-ipn")}',
        'return_url': f'http://{host}{reverse("core:payment-completed")}',
        'cancel_return': f'http://{host}{reverse("core:payment-failed")}',
    }

    # Form to render the Paypal button
    payment_button_form = PayPalPaymentsForm(initial=paypal_dict)

    print("Host is ", request.get_host())

    cart_total_amount = 0  # Initialize to 0
    for oid, item in request.session['cart_data_obj'].items():
        cart_total_amount += int(item['qty']) * float(item['price'])

    return render(request, 'core/checkout.html', {
        'cart_data': request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount,
        'payment_button_form': payment_button_form
    })


@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')    



@login_required
def payment_completed_view(request):
    cart_total_amount = 0  # Initialize to 0!
    for product_id, item in request.session['cart_data_obj'].items():
        cart_total_amount += int(item['qty']) * float(item['price'])  # Corrected calculation

    order = CartOrder.objects.create(
        user=request.user,
        price=cart_total_amount,
        paid_status=True
    )
    for product_id, item in request.session['cart_data_obj'].items():
        CartOrderItems.objects.create(
        order=order,
        invoice_no='INVOICE_NO-' + str(order.id),  # Example: INVOICE_NO-5
        item=item['title'], 
        image=item['image'], 
        qty=item['qty'], 
        price=item['price'], 
        total=float(item['qty']) * float(item['price'])  # Corrected the total calculation
    )

    context = request.POST  # Assuming you need this data
    return render(request, 'core/payment-completed.html', {
        'cart_data': request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount  # Pass the calculated total
    })




@login_required
def dashboard_view(request):
    orders = CartOrder.objects.filter(user=request.user)
    address = Address.objects.filter(user=request.user)

    # Fetch the user's profile or create one if it doesn't exist
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(user=request.user)

    # Handle POST request to save a new address
    if request.method == "POST":
        address = request.POST.get("address")
        phone = request.POST.get("phone")

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            phone=phone
        )

        messages.success(request, "Address Saved")
        return redirect("core:dashboard")

    # Prepare context for the template
    context = {
        'user_profile': user_profile,
        'orders': orders,
        'address': address,
    }

    return render(request, 'core/dashboard.html', context)

# Order Detail View
def order_detail_view(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItems.objects.filter(order=order)

    context = {
        "order_items": order_items,
    }
    return render(request, 'core/order-detail.html', context)


def make_address_default(request):
    id = request.GET['id']

    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)

    return JsonResponse({"boolean": True})  # Corrected dictionary syntax

