from django.contrib import admin
from .models import (
    LandRegistration,
    SurveyPayment,
    LandSurvey,
    TaxPayment,
    LandMapping,
    Approval
)

@admin.register(LandRegistration)
class LandRegistrationAdmin(admin.ModelAdmin):
    list_display = ('transaction_reference', 'date_of_sale', 'buyer_full_name', 'current_step', 'status')
    list_filter = ('status', 'current_step', 'land_use_type')
    search_fields = ('transaction_reference', 'buyer_full_name', 'seller_full_name', 'land_code')
    readonly_fields = ('register_date',)

@admin.register(SurveyPayment)
class SurveyPaymentAdmin(admin.ModelAdmin):
    list_display = ('payer_name', 'payment_amount', 'payment_date', 'payment_status')
    list_filter = ('payment_status', 'payment_method')
    search_fields = ('payer_name', 'admin_name')

@admin.register(LandSurvey)
class LandSurveyAdmin(admin.ModelAdmin):
    list_display = ('survey_number', 'owner_name', 'survey_date', 'surveyor_name')
    search_fields = ('survey_number', 'owner_name', 'surveyor_name')

@admin.register(TaxPayment)
class TaxPaymentAdmin(admin.ModelAdmin):
    list_display = ('land_reference_no', 'land_owner_name', 'payment_date', 'payment_status')
    list_filter = ('payment_status',)
    search_fields = ('land_reference_no', 'land_owner_name')

@admin.register(LandMapping)
class LandMappingAdmin(admin.ModelAdmin):
    list_display = ('land_reference', 'mapping_date', 'mapped_by', 'mapping_status')
    list_filter = ('mapping_status',)
    search_fields = ('land_reference', 'mapped_by')

@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('land_registration', 'director_status', 'secretary_status', 
                   'deputy_mayor_status', 'mayor_status')
    list_filter = ('director_status', 'secretary_status', 'deputy_mayor_status', 'mayor_status')
    search_fields = ('land_registration__transaction_reference',)
