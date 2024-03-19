from django import forms
from django.forms import inlineformset_factory
from .models import FacturaManual, ItemsFacturaManual

class FacturaManualForm(forms.ModelForm):
    class Meta:
        model = FacturaManual
        fields = '__all__'

class ItemsFacturaManualForm(forms.ModelForm):
    class Meta:
        model = ItemsFacturaManual
        fields = '__all__'

ItemsFacturaManualFormSet = inlineformset_factory(
    parent_model=FacturaManual,
    model=ItemsFacturaManual,
    fields='__all__',
    extra=1,
    can_delete=True
)
