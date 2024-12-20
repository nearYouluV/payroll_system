from django import forms
from .models import Employee, CustomUser, PayoutRequest
from django.contrib.auth.models import Group

class PayoutRequestForm(forms.ModelForm):
    """
    Form to handle payout requests by employees.
    """
    class Meta:
        model = PayoutRequest
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1,
                'placeholder': 'Enter payout amount'
            }),
        }

class EmployeeForm(forms.Form):
    """
    Form to manage Employee creation or updates.
    """
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    position = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    salary_rate = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    is_active = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class UserRegistrationForm(forms.ModelForm):
    """
    Form to register a new user with validation for employee association.
    """
    username = forms.CharField(
        max_length=100,
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    employee_code = forms.CharField(
        max_length=10,
        required=True,
        label="Employee Code",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'employee_code', 'password', 'confirm_password')

    def clean(self):
        """
        Validate form data including password confirmation and employee code.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        employee_code = cleaned_data.get('employee_code')

        # Check password confirmation
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # Check if the username already exists
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another one.")

        # Validate employee code existence
        try:
            employee = Employee.objects.get(employee_code=employee_code)
        except Employee.DoesNotExist:
            raise forms.ValidationError("Invalid employee code.")

        # Check if the employee is already registered with another user
        if CustomUser.objects.filter(employee=employee).exists():
            raise forms.ValidationError("This employee is already registered with another user.")

        return cleaned_data

    def save(self, commit=True):
        """
        Save the user and associate with the corresponding employee. Assign groups if necessary.
        """
        # Create user instance but don't save to the database yet
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash the password

        # Associate user with the employee using the provided employee code
        employee_code = self.cleaned_data["employee_code"]
        try:
            employee = Employee.objects.get(employee_code=employee_code)
            user.employee = employee  # Link the employee to the user
        except Employee.DoesNotExist:
            raise forms.ValidationError("Invalid employee code.")

        if commit:
            user.save()

            # Assign user to the Accountant group if the employee's position matches
            if employee.position == "Accountant":
                group, created = Group.objects.get_or_create(name="Accountant")
                user.groups.add(group)

        return user
