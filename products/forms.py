from django import forms

from .models import Category, Comment


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
