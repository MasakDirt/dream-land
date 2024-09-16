from django import forms

from dream.models import Dream, Commentary


class DreamSearchForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by title",
                "class": "form-control"
            }
        )
    )


class DreamFilterForm(forms.Form):
    filter = forms.ChoiceField(
        choices=[
            ["-date_recorded", "newest"],
            ["date_recorded", "oldest"],
            ["likes", "popular"],
            ["dislikes", "unpopular"],
        ]
    )


class CommentaryForm(forms.ModelForm):
    content = forms.CharField(widget=forms.TextInput(
        attrs={
            "placeholder": "Write comment here! . . .",
            "class": "form-control form-control border-0 shadow-none px-0",

        }), required=True, label="")

    class Meta:
        model = Commentary
        fields = ("content",)


class DreamForm(forms.ModelForm):
    class Meta:
        model = Dream
        fields = ("title", "description", "symbols", "emotions")

    def __init__(self, *args, **kwargs):
        super(DreamForm, self).__init__(*args, **kwargs)
        self.fields["symbols"].required = False
        self.fields["emotions"].required = False
