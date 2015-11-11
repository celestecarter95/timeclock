from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import FormView, ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.utils import timezone
from django.http import HttpResponseRedirect
import datetime

from .forms import PunchInForm, PunchOutForm, PunchByDateForm
from django.contrib.auth.models import User
from .models import Project, Punch

class ClockInOutView(FormView):
    success_url = reverse_lazy('timeclock:clockinout')
    def get_template_names(self):
        template_name = 'timeclock/home_clockin.html'
        records = self.request.user.punch_set.order_by('-time_in')
        if records:
            if records[0].is_clocked_in():
                template_name = 'timeclock/home_clockout.html'

        return [template_name]

    def get_form_class(self):
        records = self.request.user.punch_set.order_by('-time_in')
        if records:
            if records[0].is_clocked_in():
                return PunchOutForm

        return PunchInForm

    def get_context_data(self, **kwargs):
        context = super(ClockInOutView, self).get_context_data(**kwargs)

        objects = Punch.objects.filter(user = self.request.user).order_by('time_in')
        if objects:
            context["last_punch"] = objects[0]
        else:
            context["last_punch"] = None

        return context

    def form_valid(self, form):
        if type(form).__name__ == 'PunchInForm':
            entry = Punch()
            entry.project = form.cleaned_data['project']
            entry.user = self.request.user
            entry.save()
            #return HttpResponseRedirect(reverse('timeclock:clockinout'))

        if type(form).__name__ == 'PunchOutForm':
            entry = self.request.user.punch_set.order_by('-time_in')[0]
            entry.note = form.cleaned_data['note']
            entry.time_out = timezone.now()
            entry.save()
            #return HttpResponseRedirect(reverse('timeclock:clockinout'))

        return super(ClockInOutView, self).form_valid(form)

#class PunchByDateList(ListView):
#    model = Punch
#
#    def get_context_data(self, **kwargs):
#        context = super(PunchByDateList, self).get_context_data(**kwargs)
#        context['form'] = PunchByDateForm()
#
#class SearchByDateForm(SingleObjectMixin, FormView):
#    template_name = 'timeclock/punch_list.html'
#    form_class = PunchByDateForm
#    model = Punch
#
#    def post(self, request, *args, **kwargs):
#        self.object = self.get_object()
#        return super(SearchByDateForm, self).post(request, *args, **kwargs)
#
#    def get_success_url(self):
#        return reverse('timeclock:punchlist')
#
#    def form_valid(self, form):
#        form.cleaned_data['filter_by']
#        form.cleaned_data['state_date']
#        form.cleaned_data['end_date']
#
#        return super(SearchByDataForm, self).form_valid(self, form)
#
#class SearchForm(FormView):
#    model = Punch
#    form_class = PunchByDateForm
#    success_url = reverse_lazy('timeclock:clockinout')
#
#    def post(self, request, *args, **kwargs):
#        self.object = self.get_object()
#        return super(SearchByDateForm, self).post(request, *args, **kwargs)
#
#    def form_valid(self, form):
#        form.cleaned_data['filter_by']
#        form.cleaned_data['state_date']
#        form.cleaned_data['end_date']
#
#        return super(SearchByDataForm, self).form_valid(self, form)
#
#
#class PunchList(View):
#    template_name = 'timeclock/punch_form.html'
#
#    def get(self, request, *args, **kwargs):
#        view = PunchByDateList.as_view()
#        return view(request, *args, **kwargs)
#
#    def post(self, request, *args, **kwargs):
#        view = SearchByDateForm.as_view()
#        return view(request, *args, **kwargs)

class PunchList(ListView):
    model = Punch
    form_class = PunchByDateForm
    paginate_by = 10

    def get_queryset(self):
        #get_punches = self.request.user.punch_set.all()
        get_punches = Punch.objects.filter(user = self.request.user)

        if self.request.user.is_superuser:
            get_punches = Punch.objects.all()

        if self.request.user.is_superuser and self.request.GET.get('user'):
            get_punches = get_punches.filter(user = self.request.GET.get('user'))

        if self.request.GET.get('project'):
            get_punches = get_punches.filter(project = self.request.GET.get('project'))

        print self.request.GET.get('start_date')
        if self.request.GET.get('start_date'):
            get_punches = get_punches.filter(time_in__gte = self.request.GET.get('start_date'))

        print self.request.GET.get('end_date')
        if self.request.GET.get('end_date'):
            get_punches = get_punches.filter(time_out__lte = self.request.GET.get('end_date'))

        return get_punches.order_by('-time_in')

    def get_context_data(self, **kwargs):
        context = super(PunchList, self).get_context_data(**kwargs)

        #Add all projects to the template's context to the template's context
        context["projects"] = Project.objects.all().order_by('title')
        context["users"] = User.objects.all().order_by('first_name')

        #Get all objects for the current query
        queryset = self.get_queryset()

        total_time = datetime.timedelta(0)
        for punch in queryset:
            total_time += punch.duration()

        context["total_time"] = total_time

        return context
