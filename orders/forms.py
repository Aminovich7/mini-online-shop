from django import forms


class CheckoutForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label="Miqdor")
    address = forms.CharField(
        label="Yetkazib berish manzili",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Buyurtma yetkaziladigan manzilni kiriting",
            }
        )
    )
    promo_code = forms.CharField(
        required=False,
        max_length=50,
        label="Promo-kod",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ixtiyoriy promo-kod",
            }
        ),
    )
