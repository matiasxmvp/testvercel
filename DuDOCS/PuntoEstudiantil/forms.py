from django import forms
from Core.models import TNE

class TNEForm(forms.ModelForm):

    class Meta:
        model = TNE
        fields=[
            'rut',
            'nombre',
            'apellido',
            'estado',
            'email',
            'codigo',
            'condicion',
        ]