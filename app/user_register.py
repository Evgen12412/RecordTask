from django import forms

class UserRegister(forms.Form):
    email = forms.EmailField(label="Адрес электронной почты")
    username = forms.CharField(max_length=8, label="Имя пользователя")
    password = forms.CharField(widget=forms.PasswordInput, max_length=128, label='Введите ваш пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=128, label='Подтвердите пароль')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data