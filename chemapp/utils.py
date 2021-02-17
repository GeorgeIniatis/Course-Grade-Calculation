from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Permission


def user_edit_perm_check(func):
    def wrapper(self, *args, **kwargs):
        # access a from TestSample
        #if self.request.user.has_perm('can_edit_course_')
        perm = kwargs['course_name_slug']
        if self.user.has_perm("chemapp.can_edit_course"+perm.upper()):
            return func(self, *args, **kwargs)
        else:
            messages.error(self,"You do not have permission to edit "+perm)
            return redirect('chemapp:courses')
    return wrapper





def permission_required_context(perm, exceptionContext, login_url=None, raise_exception=False):
    def check_perms(user):
        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm
        # First check if the user has the permission (even anon users)
        if user.has_perms(perms):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied(exceptionContext)
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url)
