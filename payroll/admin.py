from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Employee records.
    """
    list_display = (
        'first_name', 'last_name', 'position', 
        'salary_rate', 'hire_date', 'is_active'
    )  # Columns displayed in the list view
    list_filter = ('is_active', 'position')  # Filters for the sidebar
    search_fields = ('first_name', 'last_name', 'position')  # Searchable fields
    ordering = ('last_name',)  # Default ordering by last name
    actions = ['delete_selected_employees']  # Custom action for batch deletion

    def get_actions(self, request):
        """
        Include default and custom actions dynamically.
        """
        actions = super().get_actions(request)
        if 'delete_selected_employees' not in actions:
            actions['delete_selected_employees'] = (
                self.delete_selected_employees, 
                'delete_selected_employees', 
                "Delete selected employees"
            )
        return actions

    def delete_selected_employees(self, request, queryset):
        """
        Custom action to delete selected employees.
        """
        count = queryset.count()  # Count the employees to be deleted
        queryset.delete()  # Perform deletion
        self.message_user(
            request, 
            f"Successfully deleted {count} employee(s)."
        )
    delete_selected_employees.short_description = "Delete selected employees"
