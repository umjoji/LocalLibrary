import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from catalog.models import BookInstance

# Create your forms here.

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text='Enter a date between now and 4 weeks (default 3)')

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # check if date is not in past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # check if date in allowed range
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data

class RenewBookModelForm(ModelForm):

    def clean_due_back(self):
        data = self.cleaned_data['due_back']

        # check if date in past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # check if renewal in allowed range
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('New renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user