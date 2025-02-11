from django import forms
from stripe import Review
from core.models import ProductReview

class ProductReviewForm(forms.ModelForm):
  
    review = forms.CharField(widget = forms.Textarea(attrs={"placeholder" : "Write your review here"}))

    class Meta:
        model = ProductReview
        fields = ['review' , 'rating']


