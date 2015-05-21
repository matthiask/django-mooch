from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy

from flock.models import Donation


class DonationAmountForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ('amount',)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        if self.project.default_amount:
            kwargs.setdefault('initial', {}).setdefault(
                'amount', self.project.default_amount)

        super().__init__(*args, **kwargs)

        available_rewards = self.project.available_rewards()
        if available_rewards:
            self.fields['reward'] = forms.ModelChoiceField(
                queryset=self.project.rewards.all(),
                label=_('Reward'),
                widget=forms.RadioSelect,
                initial='',
                required=False,
            )
            self.fields['reward'].choices = [
                ('', _('Participating is enough, thank you')),
            ] + [
                (r.id, str(r))
                for r in available_rewards
            ]

    def clean(self):
        data = super().clean()
        amount = data.get('amount')
        reward = data.get('reward')
        if amount and reward:
            if amount < reward.donation_amount:
                raise forms.ValidationError(_(
                    'The selected reward requires a minimal donation'
                    ' of %(amount)s.'
                ) % {'amount': reward.donation_amount})

            if reward.available_times is not None:
                if reward.donations.count() >= reward.available_times:
                    raise forms.ValidationError(_(
                        'This reward is not available anymore. Sorry!'
                    ))

        return data

    def save(self):
        donation = super().save(commit=False)
        donation.project = self.project
        donation.selected_reward = self.cleaned_data.get('reward')
        donation.save()
        return donation


class DonationDetailsForm(forms.ModelForm):
    remember_my_name = forms.BooleanField(
        label=ugettext_lazy('Remember my name'),
        required=False,
        initial=True,
    )

    class Meta:
        model = Donation
        fields = ('full_name', 'email', 'postal_address')
