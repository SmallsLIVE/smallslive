from braces.views import StaffuserRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView

from users.models import SmallsUser
from .forms import InstitutionAddForm
from .models import Institution


class InstitutionsListView(StaffuserRequiredMixin, ListView):
    model = Institution
    template_name = "institutional_subscriptions/institution_list.html"
    context_object_name = "institutions"
    paginate_by = 30

institution_list = InstitutionsListView.as_view()


class InstitutionMembersList(StaffuserRequiredMixin, ListView):
    template_name = "institutional_subscriptions/members_list.html"
    context_object_name = "members"
    paginate_by = 50

    def get_queryset(self):
        institution = get_object_or_404(Institution, pk=self.kwargs.get('pk'))
        return SmallsUser.objects.filter(institution=institution)

institution_members = InstitutionMembersList.as_view()


class InstitutionAddView(StaffuserRequiredMixin, CreateView):
    model = Institution
    template_name = "institutional_subscriptions/institution_add.html"
    success_url = reverse_lazy('institutions')
    form_class = InstitutionAddForm

institution_add = InstitutionAddView.as_view()
