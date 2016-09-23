from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy

from flock.models import Donation


class DonationAmountForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Donation
        fields = ('amount',)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        request = kwargs.pop('request')

        kwargs.setdefault('label_suffix', '')

        available_rewards = self.project.available_rewards
        initial = kwargs.setdefault('initial', {})

        try:
            selected_reward = [
                reward for reward in available_rewards
                if str(reward.pk) == request.GET.get('selected')
            ][0]
        except IndexError:
            if self.project.default_amount:
                initial.setdefault('amount', self.project.default_amount)
        else:
            initial.setdefault('reward', selected_reward.pk)
            initial.setdefault('amount', selected_reward.donation_amount)

        super(DonationAmountForm, self).__init__(*args, **kwargs)

        if self.project.available_rewards:
            self.fields['reward'] = forms.ModelChoiceField(
                queryset=self.project.rewards.all(),
                label=_('Reward'),
                widget=forms.RadioSelect,
                initial='',
                required=self.project.is_reward_required,
            )

            choices = []
            if not self.project.is_reward_required:
                choices.append(
                    ('', _('Participating is enough, thank you')),
                )
            choices.extend(
                (r.id, str(r))
                for r in self.project.available_rewards
            )
            self.fields['reward'].choices = choices

    def clean(self):
        data = super(DonationAmountForm, self).clean()
        amount = data.get('amount')
        reward = data.get('reward')
        if amount and reward:
            if amount < reward.donation_amount:
                raise forms.ValidationError(_(
                    'The selected reward requires a minimal donation'
                    ' of %(amount)s.'
                ) % {'amount': reward.donation_amount})

            if reward.available_times is not None:
                if reward not in self.project.available_rewards:
                    raise forms.ValidationError(_(
                        'This reward is not available anymore. Sorry!'
                    ))

        return data

    def save(self):
        donation = super(DonationAmountForm, self).save(commit=False)
        donation.project = self.project
        donation.selected_reward = self.cleaned_data.get('reward')
        donation.save()
        return donation


class DonationDetailsForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    remember_my_name = forms.BooleanField(
        label=ugettext_lazy('Remember my name'),
        required=False,
        initial=True,
    )

    class Meta:
        model = Donation
        fields = ('full_name', 'email', 'postal_address')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(DonationDetailsForm, self).__init__(*args, **kwargs)
