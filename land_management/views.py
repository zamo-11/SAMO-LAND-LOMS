from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import (
    LandRegistration,
    SurveyPayment,
    LandSurvey,
    TaxPayment,
    LandMapping,
    Approval
)
from .forms import (
    LandRegistrationForm,
    SurveyPaymentForm,
    LandSurveyForm,
    TaxPaymentForm,
    LandMappingForm,
    ApprovalForm,
    DirectorApprovalForm,
    SecretaryApprovalForm,
    DeputyMayorApprovalForm,
    MayorApprovalForm
)
from django.urls import reverse
from django.utils import timezone

@login_required
def dashboard(request):
    registrations = LandRegistration.objects.filter(user=request.user)
    approved_count = registrations.filter(status='approved').count()
    pending_count = registrations.filter(status='pending').count()
    rejected_count = registrations.filter(status='rejected').count()
    
    # Get all related forms for each registration
    for registration in registrations:
        registration.survey_payment = getattr(registration, 'surveypayment', None)
        registration.land_survey = getattr(registration, 'landsurvey', None)
        registration.tax_payment = getattr(registration, 'taxpayment', None)
        registration.land_mapping = getattr(registration, 'landmapping', None)
        registration.approval = getattr(registration, 'approval', None)
    
    context = {
        'registrations': registrations,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'land_management/dashboard.html', context)

@login_required
def land_registration(request, registration_id=None):
    registration = None
    if registration_id:
        registration = get_object_or_404(LandRegistration, id=registration_id, user=request.user)

    if request.method == 'POST':
        try:
            if registration: # Editing an existing registration
                form = LandRegistrationForm(request.POST, request.FILES, instance=registration)
            else: # Creating a new registration
                form = LandRegistrationForm(request.POST, request.FILES)
            
            if form.is_valid():
                registration = form.save(commit=False)
                registration.user = request.user
                registration.status = 'pending'
                registration.current_step = 'registration' # Reset to initial step if returned for correction
                registration.save()

                # If this was a returned registration, clear approval return info
                if registration_id and hasattr(registration, 'approval') and registration.approval.return_step:
                    approval_instance = registration.approval
                    approval_instance.return_step = None
                    approval_instance.rejection_reason = None
                    approval_instance.rejection_date = None
                    approval_instance.returned_by = None
                    approval_instance.save()

                messages.success(request, f'Land registration submitted successfully! Transaction Reference: {registration.transaction_reference}')
                return redirect('land_management:survey_payment', registration_id=registration.id)
            else:
                messages.error(request, 'Please correct the errors in the form.')
        except Exception as e:
            messages.error(request, f'Error saving registration: {str(e)}')
    else: # GET request
        if registration: # Pre-fill form for existing registration
            form = LandRegistrationForm(instance=registration)
        else: # Blank form for new registration
            form = LandRegistrationForm()

    return render(request, 'land_management/land_registration.html', {'form': form, 'registration': registration})

@login_required
def survey_payment(request, registration_id):
    registration = get_object_or_404(LandRegistration, id=registration_id, user=request.user)
    
    try:
        existing_payment = SurveyPayment.objects.get(land_registration=registration)
    except SurveyPayment.DoesNotExist:
        existing_payment = None

    if request.method == 'POST':
        form = SurveyPaymentForm(request.POST, request.FILES, instance=existing_payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.land_registration = registration
            payment.payment_status = 'pending'
            payment.save()
            registration.current_step = 'survey_payment'
            registration.save()
            messages.success(request, 'Survey payment submitted successfully.')
            return redirect('land_management:land_survey', registration_id=registration.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill some fields with registration data
        initial_data = {
            'payer_name': registration.buyer_full_name,
            'admin_name': request.user.get_full_name() or request.user.username,
        }
        form = SurveyPaymentForm(instance=existing_payment, initial=initial_data)

    return render(request, 'land_management/survey_payment.html', {
        'form': form,
        'registration': registration
    })

@login_required
def land_survey(request, registration_id):
    registration = get_object_or_404(LandRegistration, id=registration_id, user=request.user)
    
    try:
        existing_survey = LandSurvey.objects.get(land_registration=registration)
    except LandSurvey.DoesNotExist:
        existing_survey = None

    if request.method == 'POST':
        form = LandSurveyForm(request.POST, request.FILES, instance=existing_survey)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.land_registration = registration
            survey.save()
            registration.current_step = 'land_survey'
            registration.save()
            messages.success(request, 'Land survey submitted successfully.')
            return redirect('land_management:tax_payment', registration_id=registration.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill some fields with registration data
        initial_data = {
            'land_code': registration.land_code,
            'owner_name': registration.buyer_full_name,
        }
        form = LandSurveyForm(instance=existing_survey, initial=initial_data)

    return render(request, 'land_management/land_survey.html', {
        'form': form,
        'registration': registration
    })

@login_required
def tax_payment(request, registration_id):
    registration = get_object_or_404(LandRegistration, id=registration_id, user=request.user)
    
    try:
        existing_payment = TaxPayment.objects.get(land_registration=registration)
    except TaxPayment.DoesNotExist:
        existing_payment = None

    if request.method == 'POST':
        form = TaxPaymentForm(request.POST, instance=existing_payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.land_registration = registration
            payment.payment_status = 'pending'
            payment.save()
            registration.current_step = 'tax_payment'
            registration.save()
            messages.success(request, f'Tax payment submitted successfully! You can now proceed to <a href="{reverse('land_management:land_mapping', args=[registration.id])}" class="alert-link">Land Mapping</a>.')
            # Stay on the same page, re-render with messages
            return render(request, 'land_management/tax_payment.html', {
                'form': form,
                'registration': registration,
            })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill some fields with registration data
        initial_data = {
            'admin_fullname': request.user.get_full_name() or request.user.username,
            'land_owner_name': registration.buyer_full_name,
            'land_reference_no': registration.transaction_reference,
            'land_price': registration.sale_price, # Assuming land price is sale price
            'tax_price': float(registration.sale_price) * 0.05, # Example: 5% of sale price as tax
        }
        form = TaxPaymentForm(instance=existing_payment, initial=initial_data)

    return render(request, 'land_management/tax_payment.html', {
        'form': form,
        'registration': registration
    })

@login_required
def land_mapping(request, registration_id):
    registration = get_object_or_404(LandRegistration, id=registration_id, user=request.user)
    
    try:
        existing_mapping = LandMapping.objects.get(land_registration=registration)
    except LandMapping.DoesNotExist:
        existing_mapping = None

    if request.method == 'POST':
        form = LandMappingForm(request.POST, request.FILES, instance=existing_mapping)
        if form.is_valid():
            mapping = form.save(commit=False)
            mapping.land_registration = registration
            mapping.mapping_status = 'pending'
            mapping.save()
            registration.current_step = 'land_mapping'
            registration.save()
            messages.success(request, f'Land mapping submitted successfully! You can now proceed to <a href="{reverse('land_management:approval_process', args=[registration.id])}" class="alert-link">Approval Process</a>.')
            # Stay on the same page, re-render with messages
            return render(request, 'land_management/land_mapping.html', {
                'form': form,
                'registration': registration,
            })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill some fields with registration data
        initial_data = {
            'land_reference': registration.transaction_reference,
            'mapped_by': request.user.get_full_name() or request.user.username,
        }
        form = LandMappingForm(instance=existing_mapping, initial=initial_data)

    return render(request, 'land_management/land_mapping.html', {
        'form': form,
        'registration': registration
    })

@login_required
def approval_process(request, registration_id):
    registration = get_object_or_404(LandRegistration, id=registration_id)
    
    try:
        approval_instance = Approval.objects.get(land_registration=registration)
    except Approval.DoesNotExist:
        approval_instance = Approval.objects.create(land_registration=registration)

    # Only check return_step if it's not a new approval
    if approval_instance.return_step and approval_instance.director_status != 'pending':
        messages.info(request, f'This registration was returned for correction at the {approval_instance.return_step} step. Reason: {approval_instance.rejection_reason}')
        # Redirect to the appropriate step
        if approval_instance.return_step == 'registration':
            return redirect('land_management:land_registration')
        elif approval_instance.return_step == 'survey_payment':
            return redirect('land_management:survey_payment', registration_id=registration.id)
        elif approval_instance.return_step == 'land_survey':
            return redirect('land_management:land_survey', registration_id=registration.id)
        elif approval_instance.return_step == 'tax_payment':
            return redirect('land_management:tax_payment', registration_id=registration.id)
        elif approval_instance.return_step == 'land_mapping':
            return redirect('land_management:land_mapping', registration_id=registration.id)

    current_level = approval_instance.current_approval_level
    form = None
    template_name = 'land_management/approval_process.html'

    # Fetch all related data for display
    survey_payment = getattr(registration, 'surveypayment', None)
    land_survey = getattr(registration, 'landsurvey', None)
    tax_payment = getattr(registration, 'taxpayment', None)
    land_mapping = getattr(registration, 'landmapping', None)

    if request.method == 'POST':
        if current_level == 'director_pending':
            form = DirectorApprovalForm(request.POST, request.FILES, instance=approval_instance)
        elif current_level == 'secretary_pending' and approval_instance.director_status == 'approved':
            form = SecretaryApprovalForm(request.POST, request.FILES, instance=approval_instance)
        elif current_level == 'deputy_mayor_pending' and approval_instance.secretary_status == 'approved':
            form = DeputyMayorApprovalForm(request.POST, request.FILES, instance=approval_instance)
        elif current_level == 'mayor_pending' and approval_instance.deputy_mayor_status == 'approved':
            form = MayorApprovalForm(request.POST, request.FILES, instance=approval_instance)

        if form and form.is_valid():
            form.save()
            
            # Handle returned status
            if form.cleaned_data.get('director_status') == 'returned' or \
               form.cleaned_data.get('secretary_status') == 'returned' or \
               form.cleaned_data.get('deputy_mayor_status') == 'returned' or \
               form.cleaned_data.get('mayor_status') == 'returned':
                
                # Set return information
                approval_instance.return_step = form.cleaned_data.get('return_step')
                approval_instance.rejection_reason = form.cleaned_data.get('rejection_reason')
                approval_instance.rejection_date = timezone.now()
                approval_instance.returned_by = request.user.get_full_name() or request.user.username
                approval_instance.save()

                # Update registration status
                registration.status = 'pending'
                registration.current_step = form.cleaned_data.get('return_step')
                registration.save()

                messages.warning(request, f'Registration has been returned for correction at the {approval_instance.return_step} step.')
                
                # Redirect to the appropriate step
                if approval_instance.return_step == 'registration':
                    return redirect('land_management:land_registration')
                elif approval_instance.return_step == 'survey_payment':
                    return redirect('land_management:survey_payment', registration_id=registration.id)
                elif approval_instance.return_step == 'land_survey':
                    return redirect('land_management:land_survey', registration_id=registration.id)
                elif approval_instance.return_step == 'tax_payment':
                    return redirect('land_management:tax_payment', registration_id=registration.id)
                elif approval_instance.return_step == 'land_mapping':
                    return redirect('land_management:land_mapping', registration_id=registration.id)

            # Handle normal approval flow
            if current_level == 'director_pending':
                if approval_instance.director_status == 'approved':
                    approval_instance.current_approval_level = 'secretary_pending'
                    messages.success(request, 'Director approval submitted. Proceed to Secretary Approval.')
                elif approval_instance.director_status == 'rejected':
                    approval_instance.current_approval_level = 'rejected'
                    registration.status = 'rejected'
                    messages.error(request, 'Director rejected the registration.')
                approval_instance.save()
                registration.save()
                return render(request, template_name, {
                    'form': form,
                    'registration': registration,
                    'approval': approval_instance,
                    'current_level': current_level,
                    'survey_payment': survey_payment,
                    'land_survey': land_survey,
                    'tax_payment': tax_payment,
                    'land_mapping': land_mapping,
                })

            elif current_level == 'secretary_pending' and approval_instance.director_status == 'approved':
                if approval_instance.secretary_status == 'approved':
                    approval_instance.current_approval_level = 'deputy_mayor_pending'
                    messages.success(request, 'Secretary approval submitted. Proceed to Deputy Mayor Approval.')
                elif approval_instance.secretary_status == 'rejected':
                    approval_instance.current_approval_level = 'rejected'
                    registration.status = 'rejected'
                    messages.error(request, 'Secretary rejected the registration.')
                approval_instance.save()
                registration.save()
                return render(request, template_name, {
                    'form': form,
                    'registration': registration,
                    'approval': approval_instance,
                    'current_level': current_level,
                    'survey_payment': survey_payment,
                    'land_survey': land_survey,
                    'tax_payment': tax_payment,
                    'land_mapping': land_mapping,
                })

            elif current_level == 'deputy_mayor_pending' and approval_instance.secretary_status == 'approved':
                if approval_instance.deputy_mayor_status == 'approved':
                    approval_instance.current_approval_level = 'mayor_pending'
                    messages.success(request, 'Deputy Mayor approval submitted. Proceed to Mayor Approval.')
                elif approval_instance.deputy_mayor_status == 'rejected':
                    approval_instance.current_approval_level = 'rejected'
                    registration.status = 'rejected'
                    messages.error(request, 'Deputy Mayor rejected the registration.')
                approval_instance.save()
                registration.save()
                return render(request, template_name, {
                    'form': form,
                    'registration': registration,
                    'approval': approval_instance,
                    'current_level': current_level,
                    'survey_payment': survey_payment,
                    'land_survey': land_survey,
                    'tax_payment': tax_payment,
                    'land_mapping': land_mapping,
                })

            elif current_level == 'mayor_pending' and approval_instance.deputy_mayor_status == 'approved':
                if approval_instance.mayor_status == 'approved':
                    approval_instance.current_approval_level = 'completed'
                    registration.status = 'approved'
                    messages.success(request, 'Mayor approval submitted. Registration approved! Certificate generated.')
                elif approval_instance.mayor_status == 'rejected':
                    approval_instance.current_approval_level = 'rejected'
                    registration.status = 'rejected'
                    messages.error(request, 'Mayor rejected the registration.')
                approval_instance.save()
                registration.save()
                if approval_instance.mayor_status == 'approved':
                    return redirect('land_management:generate_certificate', registration_id=registration.id)
                else:
                    return render(request, template_name, {
                        'form': form,
                        'registration': registration,
                        'approval': approval_instance,
                        'current_level': current_level,
                        'survey_payment': survey_payment,
                        'land_survey': land_survey,
                        'tax_payment': tax_payment,
                        'land_mapping': land_mapping,
                    })
            else:
                messages.error(request, 'An unexpected error occurred during approval state transition.')
                return render(request, template_name, {
                    'form': form,
                    'registration': registration,
                    'approval': approval_instance,
                    'current_level': current_level,
                    'survey_payment': survey_payment,
                    'land_survey': land_survey,
                    'tax_payment': tax_payment,
                    'land_mapping': land_mapping,
                })
        else:
            messages.error(request, 'Please correct the errors in the form.')
            return render(request, template_name, {
                'form': form,
                'registration': registration,
                'approval': approval_instance,
                'current_level': current_level,
                'survey_payment': survey_payment,
                'land_survey': land_survey,
                'tax_payment': tax_payment,
                'land_mapping': land_mapping,
            })
    else: # GET request
        if current_level == 'director_pending':
            form = DirectorApprovalForm(instance=approval_instance)
        elif current_level == 'secretary_pending' and approval_instance.director_status == 'approved':
            form = SecretaryApprovalForm(instance=approval_instance)
        elif current_level == 'deputy_mayor_pending' and approval_instance.secretary_status == 'approved':
            form = DeputyMayorApprovalForm(instance=approval_instance)
        elif current_level == 'mayor_pending' and approval_instance.deputy_mayor_status == 'approved':
            form = MayorApprovalForm(instance=approval_instance)
        else:
            messages.info(request, f'Approval process is at: {current_level.replace("_", " ").title()}')
            return render(request, template_name, {
                'registration': registration,
                'approval': approval_instance,
                'current_level': current_level,
                'form': None,
                'survey_payment': survey_payment,
                'land_survey': land_survey,
                'tax_payment': tax_payment,
                'land_mapping': land_mapping,
            })

    return render(request, template_name, {
        'form': form,
        'registration': registration,
        'approval': approval_instance,
        'current_level': current_level,
        'survey_payment': survey_payment,
        'land_survey': land_survey,
        'tax_payment': tax_payment,
        'land_mapping': land_mapping,
    })

@login_required
def list_survey_payments(request):
    # Get all survey payments for the current user's registrations
    survey_payments = SurveyPayment.objects.filter(land_registration__user=request.user)
    
    # Get all registrations that don't have survey payments yet
    registrations_without_payment = LandRegistration.objects.filter(
        user=request.user
    ).exclude(
        surveypayment__isnull=False
    )
    
    context = {
        'survey_payments': survey_payments,
        'registrations_without_payment': registrations_without_payment,
    }
    return render(request, 'land_management/survey_payment_list.html', context)

@login_required
def list_land_surveys(request):
    # Get all land surveys for the current user's registrations
    land_surveys = LandSurvey.objects.filter(land_registration__user=request.user)
    
    # Get all registrations that have a survey payment but no land survey yet
    registrations_without_survey = LandRegistration.objects.filter(
        user=request.user,
        surveypayment__isnull=False
    ).exclude(
        landsurvey__isnull=False
    )

    context = {
        'land_surveys': land_surveys,
        'registrations_without_survey': registrations_without_survey,
    }
    return render(request, 'land_management/land_survey_list.html', context)

@login_required
def list_tax_payments(request):
    # Get all tax payments for the current user's registrations
    tax_payments = TaxPayment.objects.filter(land_registration__user=request.user)
    
    # Get all registrations that have a land survey but no tax payment yet
    registrations_without_tax_payment = LandRegistration.objects.filter(
        user=request.user,
        landsurvey__isnull=False
    ).exclude(
        taxpayment__isnull=False
    )

    context = {
        'tax_payments': tax_payments,
        'registrations_without_tax_payment': registrations_without_tax_payment,
    }
    return render(request, 'land_management/tax_payment_list.html', context)

@login_required
def list_land_mappings(request):
    # Get all land mappings for the current user's registrations
    land_mappings = LandMapping.objects.filter(land_registration__user=request.user)
    
    # Get all registrations that have a tax payment but no land mapping yet
    registrations_without_mapping = LandRegistration.objects.filter(
        user=request.user,
        taxpayment__isnull=False
    ).exclude(
        landmapping__isnull=False
    )

    context = {
        'land_mappings': land_mappings,
        'registrations_without_mapping': registrations_without_mapping,
    }
    return render(request, 'land_management/land_mapping_list.html', context)

@login_required
def list_director_approvals(request):
    # Get registrations that are awaiting director approval (i.e., completed mapping and are pending overall)
    pending_approvals_registrations = LandRegistration.objects.filter(current_step='land_mapping', status='pending').exclude(approval__director_status__in=['approved', 'rejected'])

    # Get existing approval records that are at the director_pending level
    existing_approvals = Approval.objects.filter(current_approval_level='director_pending')

    context = {
        'pending_approvals_registrations': pending_approvals_registrations,
        'existing_approvals': existing_approvals,
    }
    return render(request, 'land_management/director_approval_list.html', context)

@login_required
def list_secretary_approvals(request):
    # Get registrations that have director approval and are awaiting secretary approval
    pending_approvals_registrations = LandRegistration.objects.filter(
        approval__director_status='approved',
        approval__current_approval_level='secretary_pending'
    ).exclude(approval__secretary_status__in=['approved', 'rejected'])

    # Get existing approval records that are at the secretary_pending level
    existing_approvals = Approval.objects.filter(current_approval_level='secretary_pending')

    context = {
        'pending_approvals_registrations': pending_approvals_registrations,
        'existing_approvals': existing_approvals,
    }
    return render(request, 'land_management/secretary_approval_list.html', context)

@login_required
def list_deputy_mayor_approvals(request):
    approvals = Approval.objects.filter(current_approval_level='deputy_mayor_pending')
    return render(request, 'land_management/deputy_mayor_approvals_list.html', {'approvals': approvals})

@login_required
def list_mayor_approvals(request):
    approvals = Approval.objects.filter(current_approval_level='mayor_pending')
    return render(request, 'land_management/mayor_approvals_list.html', {'approvals': approvals})

@login_required
def registration_detail(request, registration_id):
    registration = get_object_or_404(LandRegistration, id=registration_id, user=request.user)
    context = {
        'registration': registration,
        'survey_payment': getattr(registration, 'surveypayment', None),
        'land_survey': getattr(registration, 'landsurvey', None),
        'tax_payment': getattr(registration, 'taxpayment', None),
        'land_mapping': getattr(registration, 'landmapping', None),
        'approval': getattr(registration, 'approval', None),
    }
    return render(request, 'land_management/registration_detail.html', context)

@login_required
def certificate_list(request):
    # Get all registrations that have completed the approval process
    registrations = LandRegistration.objects.filter(
        approval__mayor_status='approved'
    ).select_related(
        'approval',
        'surveypayment',
        'landsurvey',
        'taxpayment',
        'landmapping'
    ).order_by('-approval__mayor_approval_date')

    context = {
        'registrations': registrations,
    }
    return render(request, 'land_management/certificate_list.html', context)

@login_required
def generate_certificate(request, registration_id):
    registration = get_object_or_404(LandRegistration, id=registration_id)
    
    # Check if all steps are completed and final approval is granted
    if not all([
        registration.surveypayment,
        registration.landsurvey,
        registration.taxpayment,
        registration.landmapping,
        registration.approval,
        registration.approval.mayor_status == 'approved'
    ]):
        messages.error(request, 'Cannot generate certificate: Not all steps are completed or final approval is not granted.')
        return redirect('land_management:certificate_list')
    
    context = {
        'registration': registration,
        'survey_payment': registration.surveypayment,
        'land_survey': registration.landsurvey,
        'tax_payment': registration.taxpayment,
        'land_mapping': registration.landmapping,
        'approval': registration.approval,
    }
    return render(request, 'land_management/certificate.html', context)

@login_required
def download_certificate_pdf(request, registration_id):
    registration = get_object_or_404(LandRegistration, id=registration_id)
    
    # Check if all steps are completed and final approval is granted
    if not all([
        registration.surveypayment,
        registration.landsurvey,
        registration.taxpayment,
        registration.landmapping,
        registration.approval,
        registration.approval.mayor_status == 'approved'
    ]):
        messages.error(request, 'Cannot generate certificate: Not all steps are completed or final approval is not granted.')
        return redirect('land_management:certificate_list')
    
    context = {
        'registration': registration,
        'survey_payment': registration.surveypayment,
        'land_survey': registration.landsurvey,
        'tax_payment': registration.taxpayment,
        'land_mapping': registration.landmapping,
        'approval': registration.approval,
    }
    
    # Generate PDF using WeasyPrint
    from django.template.loader import render_to_string
    from weasyprint import HTML
    from django.conf import settings
    import os
    
    # Render the template to HTML
    html_string = render_to_string('land_management/certificate.html', context)
    
    # Create PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{registration.transaction_reference}.pdf"'
    
    return response
