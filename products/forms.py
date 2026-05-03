from django import forms
from django.forms import formset_factory, inlineformset_factory

from .models import Category, Comment, Product, ProductImage


class ProductFilterForm(forms.Form):
    query = forms.CharField(required=False, label="Qidiruv")
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="Barcha kategoriyalar",
        label="Kategoriya",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["query"].widget.attrs.update(
            {
                "placeholder": "Mahsulot, kategoriya yoki kalit so'zni qidiring",
            }
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Mahsulot haqida savol bering yoki fikringizni yozing",
                }
            )
        }
        labels = {
            "body": "Fikringiz",
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "description", "price", "category", "address", "phone_number", "discount_percent"]
        labels = {
            "title": "Mahsulot nomi",
            "description": "Tavsif",
            "price": "Narxi ($)",
            "category": "Kategoriya",
            "address": "Manzil",
            "phone_number": "Telefon raqami",
            "discount_percent": "Chegirma %",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Mahsulot nomini kiriting"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Mahsulot tavsifini kiriting"}),
            "price": forms.NumberInput(attrs={"placeholder": "Narxni kiriting", "step": "0.01"}),
            "category": forms.Select(),
            "address": forms.TextInput(attrs={"placeholder": "Manzilni kiriting"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+998 XX XXX XX XX"}),
            "discount_percent": forms.NumberInput(attrs={"placeholder": "0", "min": "0", "max": "100", "step": "0.01"}),
        }


class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(
        label="Rasm",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'multiple': False,
        })
    )

    class Meta:
        model = ProductImage
        fields = ["image"]
        labels = {
            "image": "Rasm",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget.attrs.update({
            "accept": "image/*",
        })


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True,
)
