from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.safestring import mark_safe
from userauth.models import User
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

STATUS_CHOICES = (
    ('process', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
)

STATUS = (
    ('draft', 'Draft'),
    ('disabled', 'Disabled'),
    ('in_review', 'In Review'),
    ('rejected', 'Rejected'),
    ('published', 'Published'),
)

RATING =(
    ('1', '⭐☆☆☆☆'),
    ('2', '⭐⭐☆☆☆'),
    ('3', '⭐⭐⭐☆☆'),
    ('4', '⭐⭐⭐⭐☆'),
    ('5', '⭐⭐⭐⭐⭐'),
    
)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True,length = 10, max_length=20, prefix = 'cat', alphabet = 'abcdefgh12345')
    title = models.CharField(max_length=100, default='Category')
    image = models.ImageField(upload_to='media/category', null=True, blank=True, default='category.jpg')

    class meta:
        verbose_name_plural = 'Categories'

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title
    

class Tags(models.Model):
    pass


class Vendor(models.Model):
    vid = ShortUUIDField(unique=True,length = 10, max_length=20, prefix = 'ven', alphabet = 'abcdefgh12345')
    title = models.CharField(max_length=100, default='Vendor')

    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True, default='vendor.jpg')
    description = RichTextUploadingField(null=True, blank=True, default='I am amazing vendor')
    # description = models.TextField(null=True, blank=True, default='I am amazing vendor')

    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    cover_image = models.ImageField(upload_to=user_directory_path, null=True, blank=True, default='vendor.jpg')

    address = models.TextField(max_length=100, default='123 virar west')
    contact = models.CharField(max_length=100, default='1234567890')
    chat_resp_time = models.CharField(max_length=100, default='100')
    shipping_on_time = models.CharField(max_length=100, default='100')
    authentic_rating = models.CharField(max_length=100, default='100')
    days_return = models.CharField(max_length=100, default='100')
    warranty_period = models.CharField(max_length=100, default='100')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class meta:
        verbose_name_plural = 'Vendors'

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title
    

class Product(models.Model):
    pid = ShortUUIDField(unique=True,length = 10, max_length=20, prefix = 'pro', alphabet = 'abcdefgh12345')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='vendor')

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='category')
    title = models.CharField(max_length=100, default='Product')
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True, default='product.jpg')

    description = RichTextUploadingField(null=True, blank=True, default='This is a product')    

    price = models.DecimalField(max_digits=999999999, decimal_places=2, default=1.99)
    old_price = models.DecimalField(max_digits=999999999, decimal_places=2, default=2.99)

    specifications = RichTextUploadingField(null=True, blank=True)

    life = models.CharField(max_length=100, default='1 year', null=True, blank=True)
    mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    stock_count = models.IntegerField(default=100, null=True, blank=True)
    type = models.CharField(max_length=100, default='Organic', null=True, blank=True)
    # tag = models.ForeignKey(Tags,on_delete=models.SET_NULL ,blank=True, null=True)

    product_status = models.CharField(choices = STATUS, max_length=10,default="in_review")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=True)

    sku = ShortUUIDField(unique=True,length = 4, max_length=10, prefix = 'sku', alphabet = '1234567890')

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null = True, blank=True)

    tags = TaggableManager(blank=True)

    class meta:
        verbose_name_plural = 'products'

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_percentage(self):
        return (self.old_price - self.price) * 100 / self.old_price

class ProductImages(models.Model):
    product = models.ForeignKey(Product, related_name='p_images' ,on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to="product-images", null=True, blank=True, default='product.jpg')
    date = models.DateTimeField(auto_now_add=True)

    class meta:
        verbose_name_plural = 'product Images'


####################### cart, order, orderitem, address ############################
####################### cart, order, orderitem, address ############################
####################### cart, order, orderitem, address ############################
####################### cart, order, orderitem, address ############################


class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=999999999, decimal_places=2, default=1.99)
    product_status = models.CharField(choices = STATUS_CHOICES, max_length=30, default='processing')
    paid_status = models.BooleanField(default=False)

    order_date = models.DateTimeField(auto_now_add=True)

    class meta:
        verbose_name_plural = 'Cart Order'

    def __str__(self):
        return self.user.username

    class meta:
        verbose_name_plural = 'Cart Order'

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=999999999, decimal_places=2, default=1.99)
    total = models.DecimalField(max_digits=999999999, decimal_places=2, default=1.99)

    class meta:
        verbose_name_plural = 'Cart Order Items'

    def order_image(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))



####################### Product review, Whishlist, Address ###########################
# ######################## Product review, Whishlist, Address ########################
# ########################## Product review, Whishlist, Address ######################
# ####################### Product review, Whishlist, Address #########################


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)    
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    rating = models.CharField(max_length= 1, choices = RATING, default= None)
    review = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class meta:
        verbose_name_plural = 'Product Reviews'

    def __str__(self):
        return self.product.title

class Whishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class meta:
        verbose_name_plural = 'Whishlist'

    def __str__(self):
        return self.product.title


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.TextField(max_length=100, null=True)
    city = models.CharField(max_length=100, default='Virar', null=True, blank=True)
    state = models.CharField(max_length=100, default='Maharashtra', null=True, blank=True)
    country = models.CharField(max_length=100, default='India', null=True, blank=True)
    pincode = models.CharField(max_length=100, default='401303', null=True, blank=True)
    phone = models.CharField(max_length=100, default='1234567890', null=True, blank=True)
    email = models.EmailField(max_length=100, default='email@gmail.com', null=True, blank=True)

    status = models.BooleanField(default=False)


