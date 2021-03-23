from django import forms


def validate_not_empty(value):
    if value == '':
        raise forms.ValidationError(
            'Заполните поле',
            params={'value': value},
        )
