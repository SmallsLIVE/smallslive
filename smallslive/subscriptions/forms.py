import floppyforms as forms
from django.conf import settings


class PlanForm(forms.Form):
    def __init__(self, *args, **kwargs):
        selected_plan_type = kwargs.pop('selected_plan_type')
        super(PlanForm, self).__init__(*args, **kwargs)
        if selected_plan_type == 'basic' or selected_plan_type == 'supporter':
            monthly_plan = settings.SUBSCRIPTION_PLANS[selected_plan_type]['monthly']
            plans = [(monthly_plan.get('stripe_plan_id'), monthly_plan)]
        else:
            yearly_plan = settings.SUBSCRIPTION_PLANS[selected_plan_type]['yearly']
            plans = [(yearly_plan.get('stripe_plan_id'), yearly_plan)]
        self.fields['plan'] = forms.ChoiceField(choices=plans)


class ReactivateSubscriptionForm(forms.Form):
    pass
