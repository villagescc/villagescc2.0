from decimal import Decimal as D
from django import forms
from django.utils.translation import ugettext_lazy as _
from relate.models import Endorsement
from ripple import PRECISION, SCALE
import ripple.api as ripple
from feed.models import FeedItem
from general.forms import AmountInput, ReceiverInput, ReceiverPayInput, ToggleSwitch

ROUTED = 'routed'
DIRECT = 'direct'


class EndorseForm(forms.ModelForm):
    MESSAGES = {
        'over_weight': _("Please ensure this number is below %d.")
    }

    weight = forms.IntegerField(label="Credit Limit (Measured in 'Village Hours'.)",
                                required=True, min_value=0,
                                widget=forms.NumberInput(attrs={}))

    referral = forms.BooleanField(label="Refer This Person's Services to Friends? (Only refer a person if you have actually worked with them)",
                                  required=False,
                                  widget=forms.CheckboxInput())

    class Meta:
        model = Endorsement
        exclude = ('endorser', 'recipient', 'updated')

    def __init__(self, *args, **kwargs):
        self.endorser = kwargs.pop('endorser', None)
        self.recipient = kwargs.pop('recipient', None)
        super(EndorseForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget = (forms.Textarea(attrs={}))
        self.fields['text'].label = 'Testimonial (This is a public statement)'

    @property
    def max_weight(self):
        if not self.endorser.endorsement_limited:
            return None
        max_weight = self.endorser.endorsements_remaining
        if self.instance.id:
            max_weight += self.instance.weight
        return max_weight

    # def clean_weight(self):
    #     weight = self.cleaned_data['weight']
    #     if self.endorser.endorsement_limited and weight > self.max_weight:
    #         raise forms.ValidationError(
    #             self.MESSAGES['over_weight'] % self.max_weight)
    #     return weight

    def save(self):
        endorsement = super(EndorseForm, self).save(commit=False)
        if not self.instance.id:
            endorsement.endorser = self.endorser
            endorsement.recipient = self.recipient
        endorsement.save()
        return endorsement


class AcknowledgementForm(forms.Form):
    # ripple = forms.ChoiceField(
    #     label=_("Send"),
    #     widget=forms.RadioSelect(attrs={'style': 'float: left;'}),
    #     choices=((ROUTED, _(" Trusted payment")),
    #              (DIRECT, _(" Direct payment"))),
    #     initial=ROUTED)
    amount = forms.DecimalField(
        label=_("Hours"),
        max_digits=PRECISION, decimal_places=SCALE,
        min_value=D('0.' + '0' * (SCALE - 1) + '1'),
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    memo = forms.CharField(
        label=_("Testimonial"),
        required=False,
        widget=forms.Textarea(attrs={'style': 'width: 570px; height: 215px;'}))

    ERRORS = {
        'max_ripple': _("This is higher than the maximum possible routed "
                        "payment amount."),
    }

    def __init__(self, *args, **kwargs):
        self.max_ripple = kwargs.pop('max_ripple', None)
        super(AcknowledgementForm, self).__init__(*args, **kwargs)
        if self.max_ripple == 0:
            del self.fields['ripple']

    def clean(self):
        data = self.cleaned_data
        # Enforce max_ripple amount.
        if data.get('ripple') == ROUTED and 'amount' in data:
            if data['amount'] > self.max_ripple:
                self._errors['amount'] = self.error_class(
                    [self.ERRORS['max_ripple']])
        return data

    def send_acknowledgement(self, payer, recipient):
        data = self.cleaned_data
        routed = data.get('ripple') == ROUTED
        obj = ripple.pay(
            payer, recipient, data['amount'], data['memo'], routed=routed)
        # Create feed item
        FeedItem.create_feed_items(
            sender=ripple.RipplePayment, instance=obj, created=True)
        return obj


class BlankTrust(forms.ModelForm):
    MESSAGES = {
        'over_weight': _("Please ensure this number is below %d.")
    }

    recipient_name = forms.CharField(label='Choose the trust receiver', required=True,
                                     widget=ReceiverInput(attrs={'class': 'typeahead', 'style': 'max-width: 100%'}, ))

    weight = forms.IntegerField(label="Credit Limit", required=True,
                                min_value=0, widget=AmountInput())

    text = forms.CharField(label='Testimonial', required=False,
                           widget=forms.Textarea())

    referral = forms.BooleanField(label="", required=False,
                                  widget=ToggleSwitch(attrs={
                                      'label_text': "Refer This Person's Services to Friends?",
                                      'help_text': "(Only refer a person if you have actually worked with them)",
                                  }))

    class Meta:
        model = Endorsement
        fields = ['recipient_name', 'weight', 'text']
        exclude = ('endorser', 'recipient', 'updated')

    def __init__(self, *args, **kwargs):
        self.endorser = kwargs.pop('endorser', None)
        self.recipient = kwargs.pop('recipient', None)
        super(BlankTrust, self).__init__(*args, **kwargs)

    @property
    def max_weight(self):
        if not self.endorser.endorsement_limited:
            return None
        max_weight = self.endorser.endorsements_remaining
        if self.instance.id:
            max_weight += self.instance.weight
        return max_weight

    def save(self):
        endorsement = super(BlankTrust, self).save(commit=False)
        if not self.instance.id:
            endorsement.endorser = self.endorser
            endorsement.recipient = self.recipient
        endorsement.save()
        return endorsement


class BlankPaymentForm(forms.Form):
    recipient = forms.CharField(label='Choose the payment receiver', required=True,
                                widget=ReceiverPayInput(attrs={'class': 'typeahead', 'style': 'max-width: 100%'}))

    amount = forms.DecimalField(
        label=_("Hours"),
        max_digits=PRECISION, decimal_places=SCALE,
        min_value=D('0.' + '0' * (SCALE - 1) + '1'),
        widget=AmountInput())

    memo = forms.CharField(required=False,
                           widget=forms.Textarea(attrs={'style': 'max-width: 100%; height: 100px;'}))

    def __init__(self, *args, **kwargs):
        self.payer = kwargs.pop('payer', None)
        self.recipient = kwargs.pop('recipient', None)
        self.max_amount = kwargs.pop('max_amount', None)
        super(BlankPaymentForm, self).__init__(*args, **kwargs)

        self.fields['recipient'].widget.attrs['profile'] = self.payer
        self.fields['recipient'].widget.attrs['max_amount'] = self.max_amount

    def clean(self):
        cleaned_data = super(BlankPaymentForm, self).clean()

        if self.payer == self.recipient:
            raise forms.ValidationError(
                "You can't send a payment to yourself."
            )

        amount = cleaned_data.get("amount")
        if amount:
            cleaned_data['routed'] = self.max_amount >= cleaned_data['amount']
            if not cleaned_data['routed']:
                raise forms.ValidationError(
                    "The payment through the trust network is refused. "
                    "Contact the recipient and ask them to raise your credit limit."
                )

        return cleaned_data

    def send_payment(self):
        data = self.cleaned_data
        obj = ripple.pay(
            self.payer, self.recipient, float(data['amount']), data['memo'], routed=data['routed']
        )
        # Create feed item
        FeedItem.create_feed_items(sender=ripple.RipplePayment, instance=obj, created=True)
        return obj
