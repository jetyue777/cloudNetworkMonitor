from django import forms


class configure_form(forms.Form):
    external_ip = forms.CharField(max_length=20, required=True)
    user_name = forms.CharField(max_length=50, required=True)
