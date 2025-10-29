from django import forms

from .models import Profile


class UserAndProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=120, label='First Name')
    last_name = forms.CharField(max_length=120, label='Last Name')
    email = forms.EmailField(label='Email')

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'agreement_accepted', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile
