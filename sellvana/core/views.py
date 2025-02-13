from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Product, Category, ProductReview, Vendor
from django.db.models import Count, Avg
from taggit.models import Tag
from django.contrib.auth.decorators import login_required
from .forms import ProductReviewForm
from django.db.models import Count
# import render_to_string
from django.template.loader import render_to_string
#import response
from django.http import JsonResponse

# Create your views here.
def index(request):
    # products = Product.objects.all().order_by('-date')
    products = Product.objects.filter(product_status="published", featured=True)
    print(products)
    context = {
        'products': products
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
    context = {
        'categories': categories
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





# cart list view
def cart_view(request):
    cart_total_amount = 0

    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html",{"cart_data" : request.session['cart_data_obj'], 'totalCartItems' : len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})

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


def checkout_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/checkout.html",{"cart_data" : request.session['cart_data_obj'], 'totalCartItems' : len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
