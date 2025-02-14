from django.urls import include, path
from core.views import make_address_default, order_detail_view, dashboard_view, payment_completed_view, payment_failed_view, checkout_view, update_cart, delete_item_from_cart, cart_view, predict_product_view, add_to_cart, search_view, ajax_add_review, filter_product, index, category_list_view, product_list_view, category_product_list_view, vendor_list_view, vendor_detail_view, product_detail_view, tag_list_view

app_name = "core"

urlpatterns = [
    # homepage
    path("", index, name="index"),
    path("product/", product_list_view, name="product-list"),
    path("product/<pid>", product_detail_view, name="product-detail"),
    

    # category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),

    # vendor
    path("vendor/", vendor_list_view, name="vendor-list"),
    path("vendor/<vid>/", vendor_detail_view, name="vendor-detail"),

    # tags
    path("products/tag/<slug:tag_slug>/", tag_list_view, name="tag"),


    # ajax review form
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),

    # search url
    path("search/", search_view, name="search"),

    # filter products
    path("filter-products", filter_product, name="filter-product"),

    #Add to cart
    path("add_to_cart", add_to_cart, name="add-to-cart"),

    # Cart List Url
    path("cart/", cart_view, name="cart"),

    # Delete Cart Item
    path("delete-from-cart", delete_item_from_cart, name="cadelete-from-cartrt"),

    # Update Cart Item
    path("update-cart", update_cart, name="update-cart"),

    # Checkout
    path("checkout", checkout_view, name="checkout"),

    # Payment Complete
    path('payment-completed/', payment_completed_view, name='payment-completed'),

    # Payment Failed
    path('payment-failed/', payment_failed_view, name='payment-failed'),


    path('dashboard/', dashboard_view, name='dashboard'),


    path('dashboard/order/<int:id>', order_detail_view, name='order-detail'),


    # make default address
    path("make-default-address", make_address_default, name="make-default-address"),

    # predict product
    path('predict_product/', predict_product_view, name='predict_product'),

    # paypal
    path('paypal', include('paypal.standard.ipn.urls')),

]
