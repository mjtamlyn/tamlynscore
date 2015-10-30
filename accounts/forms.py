from django.contrib.auth.forms import SetPasswordForm


class RegisterForm(SetPasswordForm):
    def save(self):
        self.user.is_active = True
        return super(RegisterForm, self).save()
