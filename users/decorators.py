from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Декоратор для проверки роли пользователя.
    allowed_roles - список допустимых ролей.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("У вас нет прав для доступа к этой странице.")
        return _wrapped_view
    return decorator