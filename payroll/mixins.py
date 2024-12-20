from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

class AccountantRequiredMixin(LoginRequiredMixin):
    """
    Custom mixin to restrict access to views for users who are not in the 'Accountant' group.
    Inherits from LoginRequiredMixin to ensure user authentication.
    """

    def dispatch(self, request, *args, **kwargs):
        # Check if the user belongs to the 'Accountant' group
        if not request.user.groups.filter(name='Accountant').exists():
            messages.error(request, "You are not authorized to view this page.")
            return redirect('profile')  # Redirect to the profile page if unauthorized

        return super().dispatch(request, *args, **kwargs)
