from braces.views import StaffuserRequiredMixin
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, FormView, ListView, UpdateView

from users.models import SmallsUser
from artist_registration.views import ArtistAccountActivateView
from .forms import InstitutionAddForm, InstitutionMembersInviteForm
from .models import Institution


class InstitutionsListView(StaffuserRequiredMixin, ListView):
    model = Institution
    template_name = "institutional_subscriptions/institution_list.html"
    context_object_name = "institutions"
    paginate_by = 30

    def get_queryset(self):
        qs = super(InstitutionsListView, self).get_queryset()
        if self.request.GET.get('q'):
            qs = qs.filter(name__icontains=self.request.GET.get('q'))
        return qs

institution_list = InstitutionsListView.as_view()


class InstitutionMembersList(StaffuserRequiredMixin, ListView):
    template_name = "institutional_subscriptions/members_list.html"
    context_object_name = "members"
    paginate_by = 50

    def get_queryset(self):
        institution = get_object_or_404(Institution, pk=self.kwargs.get('pk'))
        qs = SmallsUser.objects.filter(institution=institution)
        search_query = self.request.GET.get('q')
        if search_query:
            qs = qs.filter(Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) |
                           Q(email__icontains=search_query))
        return qs

    def get_context_data(self, **kwargs):
        context = super(InstitutionMembersList, self).get_context_data(**kwargs)
        self.institution = get_object_or_404(Institution, pk=self.kwargs.get('pk'))
        context['institution'] = self.institution
        return context

institution_members = InstitutionMembersList.as_view()


class InstitutionAddView(StaffuserRequiredMixin, CreateView):
    model = Institution
    template_name = "institutional_subscriptions/institution_add.html"
    success_url = reverse_lazy('institution_list')
    form_class = InstitutionAddForm

institution_add = InstitutionAddView.as_view()


class InstitutionAddView(StaffuserRequiredMixin, UpdateView):
    model = Institution
    template_name = "institutional_subscriptions/institution_add.html"
    success_url = reverse_lazy('institution_list')
    form_class = InstitutionAddForm

institution_edit = InstitutionAddView.as_view()


@staff_member_required
@require_POST
def institution_member_delete(request, institution_id, member_id):
    user = get_object_or_404(SmallsUser, pk=member_id)
    user.institution = None
    user.save()
    return redirect('institution_members', pk=institution_id)


@staff_member_required
@require_POST
def institution_delete(request, institution_id):
    institution = get_object_or_404(Institution, pk=institution_id)
    institution.members.update(institution=None)
    institution.delete()
    return redirect('institution_list')


class InstitutionInviteMembersView(StaffuserRequiredMixin, FormView):
    form_class = InstitutionMembersInviteForm
    template_name = 'institutional_subscriptions/institution_invite_members.html'

    def form_valid(self, form):
        form.invite_members(self.request)
        return super(InstitutionInviteMembersView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(InstitutionInviteMembersView, self).get_form_kwargs()
        self.institution = get_object_or_404(Institution, pk=self.kwargs.get('pk'))
        kwargs['institution'] = self.institution
        return kwargs

    def get_success_url(self):
        return reverse_lazy('institution_members', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(InstitutionInviteMembersView, self).get_context_data(**kwargs)
        context['institution'] = self.institution
        return context

institution_invite_members = InstitutionInviteMembersView.as_view()


class InstitutionMemberActivateView(ArtistAccountActivateView):
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(InstitutionMemberActivateView, self).get_context_data(**kwargs)
        context['institution_signup'] = True
        return context

institution_member_activate = InstitutionMemberActivateView.as_view()
