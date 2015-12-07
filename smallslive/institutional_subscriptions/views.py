from django.views.generic.list import ListView
from .models import Institution


class InstitutionsListView(ListView):
    model = Institution
    template_name = "institutional_subscriptions/institution_list.html"
    context_object_name = "institutions"
    paginate_by = 30

institution_list = InstitutionsListView.as_view()
