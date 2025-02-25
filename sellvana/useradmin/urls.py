from django.urls import path
from .views import predict_product_details  # Ensure this import is correct
from useradmin import views

app_name = "useradmin"  # Namespace for URLs

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("products/", views.products, name="products"),
    path("add_product/", views.add_product, name="add_product"),
    path("edit_product/<pid>/", views.edit_product, name="edit_product"),
    path("delete_product/<pid>/", views.delete_product, name="delete_product"),
    path("predict-product-details/", predict_product_details, name="predict_product_details"),
]
