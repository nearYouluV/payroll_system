from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('profile/', EmployeeProfileView.as_view(), name='profile'),
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/create/', EmployeeCreateView.as_view(), name='employee_create'),
    path('payout-requests/', PayoutRequestListView.as_view(), name='payout_request_list'),
    path('payout-request/<int:pk>/', PayoutRequestDetailView.as_view(), name='payout_request_detail'),
    path('payout-request/create/', PayoutRequestCreateView.as_view(), name='payout_request_create'),
    path('payout-history/', PayoutHistoryListView.as_view(), name='payout_history_list'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('payout-request/<int:pk>/process/',  ProcessPayout.as_view(), name='process_payout_request'),
]