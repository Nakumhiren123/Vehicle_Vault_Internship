from django import forms
from .models import Car, Review, Accessory, CarVariant


class CarForm(forms.ModelForm):

    class Meta:
        model = Car
        fields = '__all__'

        widgets = {
            'carName': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuelType': forms.TextInput(attrs={'class': 'form-control'}),
            'transmission': forms.TextInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'launchYear': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'model_3d': forms.FileInput(attrs={'class': 'form-control', 'accept': '.glb,.gltf'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = '__all__'
        widgets = {
            'accessoryName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Alloy Wheels'}),
            'accessoryType': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Exterior'}),
            'price':         forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price in ₹'}),
            'description':   forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the accessory…'}),
        }
 
class CarVariantForm(forms.ModelForm):
    class Meta:
        model = CarVariant
        fields = ['variantName', 'variantTier', 'price', 'mileage', 'transmission', 'features', 'isAvailable']
        widgets = {
            'variantName':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. LXi, VXi, ZXi+'}),
            'variantTier':  forms.Select(attrs={'class': 'form-control'}),
            'price':        forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price in ₹'}),
            'mileage':      forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'km/l (optional)'}),
            'transmission': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Manual / Automatic'}),
            'features':     forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                'placeholder': 'Sunroof, Cruise Control, LED Headlights…'}),
            'isAvailable':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
 
# Inline formset — manage multiple variants on the Car form
CarVariantFormSet = forms.inlineformset_factory(
    Car, CarVariant,
    form=CarVariantForm,
    extra=1,
    can_delete=True,
)
 