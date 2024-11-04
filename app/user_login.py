from django import forms

class UserLogIn(forms.Form):
    email = forms.EmailField(label="Адрес электронной почты")
    password = forms.CharField(widget=forms.PasswordInput, max_length=128, label='Введите ваш пароль')

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data