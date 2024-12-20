from django.contrib.auth.models import Group

def is_accountant_or_superuser(request):
    if not request.user.is_authenticated:
        return {'is_accountant': False, 'is_superuser': False}
    return {
        'is_accountant': request.user.groups.filter(name='Accountant').exists(),
        'is_superuser': request.user.is_superuser,
    }