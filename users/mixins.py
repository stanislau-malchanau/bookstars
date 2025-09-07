from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(LoginRequiredMixin):
    """
    Миксин для проверки роли пользователя в CBV.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.role not in self.allowed_roles:
            raise PermissionDenied("У вас нет прав для доступа к этой странице.")
        
        return super().dispatch(request, *args, **kwargs)