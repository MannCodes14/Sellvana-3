from django.shortcuts import render, redirect
from core.models import CartOrder, Product, Category
from django.db.models import Sum
from userauth.models import User
from useradmin.forms import AddProductForm

import datetime

def dashboard(request):
    revenue = CartOrder.objects.aggregate(price=Sum("price"))
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")
    latest_orders = CartOrder.objects.all()

    this_month = datetime.datetime.now().month

    monthly_revenue = CartOrder.objects.filter(order_date__month=this_month).aggregate(price=Sum("price"))

    context = {
        "revenue": revenue,
        "total_orders_count": total_orders_count,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "monthly_revenue": monthly_revenue,
    }

    return render(request, "useradmin/dashboard.html", context)



def products(request):
    all_products = Product.objects.all().order_by("-id")
    all_categories = Category.objects.all()

    context = {
        "all_products": all_products,
        "all_categories": all_categories,
    }

    return render(request, "useradmin/products.html", context)


def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            return redirect("useradmin:dashboard")  # Redirect properly
        else:
            print(form.errors)  # Debugging: Print errors in console
    else:
        form = AddProductForm()

    context = {
        "form": form
    }

    return render(request, 'useradmin/add_product.html', context)



def edit_product(request, pid):
    product = Product.objects.get(pid=pid)
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            return redirect("useradmin:edit_product", product.pid)  # Redirect properly
    else:
        form = AddProductForm(instance=product)

    context = {
        "form": form,
        'product': product
    }

    return render(request, "useradmin/edit_product.html", context)

def delete_product(request, pid):
    product = Product.objects.get(pid=pid)
    product.delete()
    return redirect("useradmin:products")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from core.models import Category
from .ml_utils import predict_image, generate_tags, match_category_gemini, generate_description_gemini  # Import function for Gemini API

import re

import re
from django.utils.text import slugify

@csrf_exempt
def predict_product_details(request):
    if request.method == "POST" and request.FILES.get("image"):
        try:
            # Get the uploaded image
            image_file = request.FILES["image"]

            # Predict the class using MobileNetV3
            predicted_class = predict_image(image_file)
            if "error" in predicted_class.lower():
                return JsonResponse({"success": False, "error": predicted_class})

            # Generate tags using Google Gemini and extract properly
            tags_str = generate_tags(predicted_class)
            
            # Remove numbers and extra spaces from tags and convert to a list
            tags_list = re.sub(r'\d+\.\s*', '', tags_str).split()  # Remove numbers and dots, then split into list
            tags_list_main = []
            for tag in tags_list:
                tags_list_main.append(slugify(tag))
            # Generate a description
            description = generate_description_gemini(predicted_class, tags_str)

            # Fetch all available categories
            all_categories = list(Category.objects.values_list("title", flat=True))

            # Use Gemini to determine the best category
            best_match = match_category_gemini(predicted_class, all_categories)

            # Fetch category object if found
            category = Category.objects.filter(title=best_match).first() if best_match and best_match != "No matching category" else None

            return JsonResponse({
                "success": True,
                "title": predicted_class,
                "category": category.id if category else "",
                "description": description,
                "tags": tags_list_main,  # Return tags as a list
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Invalid request."})