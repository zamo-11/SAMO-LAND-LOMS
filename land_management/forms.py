from django import forms
from .models import (
    LandRegistration,
    SurveyPayment,
    LandSurvey,
    TaxPayment,
    LandMapping,
    Approval
)

class LandRegistrationForm(forms.ModelForm):
    class Meta:
        model = LandRegistration
        exclude = ['user', 'status', 'rejection_comment', 'current_step', 'transaction_reference']
        widgets = {
            # Seller Information
            'seller_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'seller_national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'seller_birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'seller_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'seller_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            
            # Buyer Information
            'buyer_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'buyer_national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'buyer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'buyer_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            
            # Land Information
            'land_code': forms.TextInput(attrs={'class': 'form-control'}),
            'land_size': forms.Select(attrs={'class': 'form-control'}),
            'size_unit': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('sqm', 'Square Meters'),
                ('hectares', 'Hectares'),
                ('acres', 'Acres'),
            ]),
            'land_use_type': forms.Select(attrs={'class': 'form-control'}),
            'land_zone': forms.TextInput(attrs={'class': 'form-control'}),
            'land_district': forms.TextInput(attrs={'class': 'form-control'}),
            'land_region': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Transaction Details
            'date_of_sale': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'title_deed_number': forms.TextInput(attrs={'class': 'form-control'}),
            'title_deed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sale_deed_number': forms.TextInput(attrs={'class': 'form-control'}),
            'sale_deed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Transaction Participants
            'notary_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guarantor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'witness1_name': forms.TextInput(attrs={'class': 'form-control'}),
            'witness2_name': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Documents
            'documents': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom choices for land size
        self.fields['land_size'].choices = [
            ('6x12', '6x12'),
            ('9x12', '9x12'),
            ('custom', 'Custom'),
        ]

class SurveyPaymentForm(forms.ModelForm):
    class Meta:
        model = SurveyPayment
        exclude = ['land_registration', 'payment_status', 'date_created']
        widgets = {
            'admin_name': forms.TextInput(attrs={'class': 'form-control'}),
            'payer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_amount': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_receipt': forms.FileInput(attrs={'class': 'form-control'}),
        }

class LandSurveyForm(forms.ModelForm):
    class Meta:
        model = LandSurvey
        exclude = ['land_registration', 'date_created']
        widgets = {
            'survey_number': forms.TextInput(attrs={'class': 'form-control'}),
            'parcel_number': forms.TextInput(attrs={'class': 'form-control'}),
            'land_code': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'survey_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'surveyor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'survey_location': forms.TextInput(attrs={'class': 'form-control'}),
            'coordinates': forms.TextInput(attrs={'class': 'form-control'}),
            'survey_documents': forms.FileInput(attrs={'class': 'form-control'}),
            'land_direction': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TaxPaymentForm(forms.ModelForm):
    class Meta:
        model = TaxPayment
        exclude = ['land_registration', 'payment_status', 'date_created']
        widgets = {
            'admin_fullname': forms.TextInput(attrs={'class': 'form-control'}),
            'land_owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'land_reference_no': forms.TextInput(attrs={'class': 'form-control'}),
            'land_price': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'tax_price': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class LandMappingForm(forms.ModelForm):
    class Meta:
        model = LandMapping
        exclude = ['land_registration', 'mapping_status']
        widgets = {
            'mapping_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = [
            'director_full_name', 'director_title', 'director_email', 'director_signature', 'director_status', 'director_comment',
            'secretary_full_name', 'secretary_title', 'secretary_email', 'secretary_signature', 'secretary_status', 'secretary_comment',
            'deputy_mayor_full_name', 'deputy_mayor_title', 'deputy_mayor_email', 'deputy_mayor_signature', 'deputy_mayor_status', 'deputy_mayor_comment',
            'mayor_full_name', 'mayor_title', 'mayor_email', 'mayor_signature', 'mayor_status', 'mayor_comment',
        ]
        widgets = {
            'director_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'director_title': forms.TextInput(attrs={'class': 'form-control'}),
            'director_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'director_signature': forms.FileInput(attrs={'class': 'form-control'}),
            'director_status': forms.Select(attrs={'class': 'form-control'}),
            'director_comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),

            'secretary_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'secretary_title': forms.TextInput(attrs={'class': 'form-control'}),
            'secretary_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'secretary_signature': forms.FileInput(attrs={'class': 'form-control'}),
            'secretary_status': forms.Select(attrs={'class': 'form-control'}),
            'secretary_comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),

            'deputy_mayor_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'deputy_mayor_title': forms.TextInput(attrs={'class': 'form-control'}),
            'deputy_mayor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'deputy_mayor_signature': forms.FileInput(attrs={'class': 'form-control'}),
            'deputy_mayor_status': forms.Select(attrs={'class': 'form-control'}),
            'deputy_mayor_comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),

            'mayor_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mayor_title': forms.TextInput(attrs={'class': 'form-control'}),
            'mayor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mayor_signature': forms.FileInput(attrs={'class': 'form-control'}),
            'mayor_status': forms.Select(attrs={'class': 'form-control'}),
            'mayor_comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class DirectorApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = ['director_full_name', 'director_title', 'director_email', 'director_signature', 'director_status', 'director_comment', 'return_step', 'rejection_reason']
        widgets = {
            'director_comment': forms.Textarea(attrs={'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
            'return_step': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['return_step'].required = False
        self.fields['rejection_reason'].required = False

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('director_status')
        return_step = cleaned_data.get('return_step')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status == 'returned':
            if not return_step:
                raise forms.ValidationError('Please select which step to return to.')
            if not rejection_reason:
                raise forms.ValidationError('Please provide a reason for returning the registration.')

        return cleaned_data

class SecretaryApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = ['secretary_full_name', 'secretary_title', 'secretary_email', 'secretary_signature', 'secretary_status', 'secretary_comment', 'return_step', 'rejection_reason']
        widgets = {
            'secretary_comment': forms.Textarea(attrs={'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
            'return_step': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['return_step'].required = False
        self.fields['rejection_reason'].required = False

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('secretary_status')
        return_step = cleaned_data.get('return_step')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status == 'returned':
            if not return_step:
                raise forms.ValidationError('Please select which step to return to.')
            if not rejection_reason:
                raise forms.ValidationError('Please provide a reason for returning the registration.')

        return cleaned_data

class DeputyMayorApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = ['deputy_mayor_full_name', 'deputy_mayor_title', 'deputy_mayor_email', 'deputy_mayor_signature', 'deputy_mayor_status', 'deputy_mayor_comment', 'return_step', 'rejection_reason']
        widgets = {
            'deputy_mayor_comment': forms.Textarea(attrs={'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
            'return_step': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['return_step'].required = False
        self.fields['rejection_reason'].required = False

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('deputy_mayor_status')
        return_step = cleaned_data.get('return_step')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status == 'returned':
            if not return_step:
                raise forms.ValidationError('Please select which step to return to.')
            if not rejection_reason:
                raise forms.ValidationError('Please provide a reason for returning the registration.')

        return cleaned_data

class MayorApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = ['mayor_full_name', 'mayor_title', 'mayor_email', 'mayor_signature', 'mayor_status', 'mayor_comment', 'return_step', 'rejection_reason']
        widgets = {
            'mayor_comment': forms.Textarea(attrs={'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
            'return_step': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['return_step'].required = False
        self.fields['rejection_reason'].required = False

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('mayor_status')
        return_step = cleaned_data.get('return_step')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status == 'returned':
            if not return_step:
                raise forms.ValidationError('Please select which step to return to.')
            if not rejection_reason:
                raise forms.ValidationError('Please provide a reason for returning the registration.')

        return cleaned_data 