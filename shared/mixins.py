from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import AccessMixin


class AuthRequiredMessageMixin(AccessMixin):
    permission_denied_message = "Bu amalni bajarish uchun tizimga kiring."

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        messages.info(self.request, self.get_permission_denied_message())
        redirect_target = (
            self.request.POST.get("next")
            or self.request.GET.get("next")
            or self.request.META.get("HTTP_REFERER")
            or self.request.get_full_path()
        )
        return redirect_to_login(
            redirect_target,
            self.get_login_url(),
            self.get_redirect_field_name(),
        )
