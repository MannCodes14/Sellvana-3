from .models import Product, Category, Address, Vendor
from django.db.models import Count, Min, Max

def default(request):

    # thes will be available in all templates
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    min_max_price = Product.objects.aggregate(Min('price'), Max('price'))

    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None
        
        
    context = {
        'categories': categories,
        'address': address,
        'vendors': vendors,
        'min_max_price': min_max_price
    }
    return context