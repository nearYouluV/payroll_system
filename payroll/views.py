from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .models import Employee, PayoutRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegistrationForm, EmployeeForm, PayoutRequestForm
from django.contrib.auth.decorators import login_required
from .mixins import AccountantRequiredMixin
from .context_processors import is_accountant_or_superuser
from django.db.models import Sum
from django.core.exceptions import ValidationError

class HomeView(TemplateView):
    template_name = 'payroll/home.html'

class ProcessPayout(AccountantRequiredMixin, LoginRequiredMixin, DetailView):
    model = PayoutRequest
    template_name = 'payroll/payout_request_detail.html'
    context_object_name = 'request'

    def post(self, request, *args, **kwargs):
        # Retrieve the payout request object
        payout_request = self.get_object()

        try:
            payout_request.process_request()  # Calls the custom processing method on the request
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'payroll/error.html', {'error_message': str(e)})

        return redirect('payout_request_list')

class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'payroll/registration.html'
    success_url = reverse_lazy('profile')  # Redirects to the user profile page after successful registration

    def form_valid(self, form):
        user = form.save()  # Save the new user
        login(self.request, user)  # Log in the user immediately
        messages.success(self.request, "Registration successful!")
        return redirect(self.success_url)

class UserLoginView(LoginView):
    template_name = 'payroll/login.html'  # Login page template
    redirect_authenticated_user = True  # Redirect already logged-in users to their profile or dashboard

class EmployeeCreateView(FormView):
    template_name = 'payroll/employee_form.html'
    form_class = EmployeeForm
    success_url = reverse_lazy('employee_list')

    def form_valid(self, form):
        # Create a new employee instance
        Employee.objects.create(
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            position=form.cleaned_data['position'],
            salary_rate=form.cleaned_data['salary_rate'],
            hire_date=form.cleaned_data['hire_date'],
            is_active=form.cleaned_data['is_active'],
        )
        return super().form_valid(form)

# Employee profile page
class EmployeeProfileView(LoginRequiredMixin, DetailView, FormView):
    model = Employee
    template_name = 'payroll/employee_profile.html'
    context_object_name = 'employee'
    form_class = PayoutRequestForm

    def get_object(self, queryset=None):
        # Fetch the employee object for the logged-in user
        self.object = self.request.user.employee
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        context['total_pending_amount'] = (
            PayoutRequest.objects.filter(employee=employee, status='Pending')
            .aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        )
        context['form'] = self.get_form()  # Include the form in the context
        return context

    def form_valid(self, form):
        employee = self.get_object()
        amount = form.cleaned_data['amount']
        if amount > employee.available_earnings:
            form.add_error('amount', 'Requested amount exceeds available earnings.')
            return self.form_invalid(form)

        PayoutRequest.objects.create(
            employee=employee,
            amount=amount,
            status='Pending'
        )
        return HttpResponseRedirect(reverse_lazy('profile'))

    def form_invalid(self, form):
        # Pass the form with errors back to the context
        context = self.get_context_data(form=form)
        context['form'] = form
        return self.render_to_response(context)

# Page to view all employees (for accountants only)
class EmployeeListView(AccountantRequiredMixin, ListView):
    model = Employee
    template_name = 'payroll/employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        return Employee.objects.all().order_by('-salary_rate')

# Employee details page (for accountants only)
class EmployeeDetailView(AccountantRequiredMixin, DetailView):
    model = Employee
    template_name = 'payroll/employee_detail.html'
    context_object_name = 'employee'

# Page to view all payout requests (for accountants only)
class PayoutRequestListView(AccountantRequiredMixin, ListView):
    model = PayoutRequest
    template_name = 'payroll/payout_request_list.html'
    context_object_name = 'payout_requests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(is_accountant_or_superuser(self.request))  # Add the accountant and superuser check
        return context

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'requested_at')  # Default sorting field
        order = self.request.GET.get('order', 'asc')  # Default sorting order

        queryset = PayoutRequest.objects.filter(status="Pending")

        if sort_by == 'amount':
            if order == 'asc':
                queryset = queryset.order_by('amount')
            else:
                queryset = queryset.order_by('-amount')
        elif sort_by == 'requested_at':
            if order == 'asc':
                queryset = queryset.order_by('requested_at')
            else:
                queryset = queryset.order_by('-requested_at')

        return queryset

# Create a new payout request (for employees only)
class PayoutRequestCreateView(LoginRequiredMixin, CreateView):
    model = PayoutRequest
    fields = ['amount']
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        employee = self.request.user.employee
        requested_amount = form.cleaned_data['amount']
        if requested_amount > employee.available_earnings:
            messages.error(self.request, f"Requested amount exceeds available earnings (${employee.available_earnings:.2f}).")
            return self.form_invalid(form)
        form.instance.employee = self.request.user.employee
        return super().form_valid(form)

# Payout request detail view
class PayoutRequestDetailView(AccountantRequiredMixin, DetailView):
    model = PayoutRequest
    template_name = 'payroll/payout_request_detail.html'
    context_object_name = 'payout_request'

# View for payout history
class PayoutHistoryListView(LoginRequiredMixin, ListView):
    model = PayoutRequest
    template_name = 'payroll/payout_history_list.html'
    context_object_name = 'payout_history'

    def get_queryset(self):
        user = self.request.user
        order = self.request.GET.get('order', 'asc')

        sort_by = self.request.GET.get('sort_by', 'requested_at')

        if user.groups.filter(name='Accountant').exists():
            queryset = PayoutRequest.objects.filter(status="Processed")
        elif hasattr(user, 'employee'):
            queryset = PayoutRequest.objects.filter(employee=user.employee, status='Processed')
        else:
            raise Http404("You do not have an associated employee record.")

        if sort_by == 'amount':
            if order == 'asc':
                queryset = queryset.order_by('amount')
            else:
                queryset = queryset.order_by('-amount')
        elif sort_by == 'requested_at':
            if order == 'asc':
                queryset = queryset.order_by('requested_at')
            else:
                queryset = queryset.order_by('-requested_at')

        return queryset
