from django.contrib import admin
from .models import Category, Vendor, Product, Address, Whishlist, CartOrder, CartOrderItems, ProductReview, ProductImages

# Register your models here.

class ProductImagesAdmin(admin.StackedInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user', 'title', 'product_image', 'category', 'vendor','price', 'featured', 'product_status', 'pid', 'date', 'id']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']

class VendorAdmin(admin.ModelAdmin):
    list_display = ['user', 'vendor_image', 'date', 'id']

class CategoryOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'price', 'order_date', 'product_status', 'paid_status']

class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ['order', 'invoice_no', 'item', 'qty', 'price', 'total', 'image']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'review', 'date']

class WhishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']

class AddressAdmin(admin.ModelAdmin):
    list_editable = ['status', 'address']
    list_display = ['user', 'address', 'status']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Whishlist, WhishlistAdmin)
admin.site.register(CartOrder, CategoryOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
