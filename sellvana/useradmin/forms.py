from django import forms
from django.core.validators import MinValueValidator, FileExtensionValidator
from core.models import Product, Category

class AddProductForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter product title", "class": "form-control"}),
        error_messages={"required": "Please enter a product title."}
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Product Description", "class": "form-control"}),
        required=False
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={"placeholder": "Sale Price", "class": "form-control"}),
        validators=[MinValueValidator(0)]
    )
    old_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={"placeholder": "Old Price", "class": "form-control"}),
        required=False,
        validators=[MinValueValidator(0)]
    )
    type = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Type of product e.g organic cream", "class": "form-control"}),
        required=False
    )
    stock_count = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "How many are in stock?", "class": "form-control"}),
        validators=[MinValueValidator(0)]
    )
    life = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "How long would this product live?", "class": "form-control"}),
        required=False
    )
    mfd = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"placeholder": "e.g 22-11-02", "class": "form-control", "type": "date"}),
        required=True  # Ensure the field is required
    )
    tags = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Tags (comma-separated)", "class": "form-control"}),
        required=False,
        help_text="Enter tags separated by commas."
    )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'price',
            'old_price',
            'specifications',
            'type',
            'stock_count',
            'life',
            'mfd',
            'tags',
            'digital',
            'category'
        ]