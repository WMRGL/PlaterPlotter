import json
from datetime import datetime, timedelta

from django.db.models import Count, Case, When, IntegerField, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from platerplotter.models import Sample
from . import forms


class CancerRareDiseaseView(LoginRequiredMixin, FormView):
    template_name = 'charts/cancer_rd.html'
    form_class = forms.DateRangeForm

    def form_valid(self, form):
        date_range = form.cleaned_data['range_calendar'].split(' to ')
        start_date = datetime.strptime(date_range[0], '%Y-%m-%d').date()
        end_date = datetime.strptime(date_range[1], '%Y-%m-%d').date()
        context = self.get_filtered_disease_counts(start_date, end_date)
        return self.render_to_response(self.get_context_data(**context))

    def get(self, request, *args, **kwargs):
        context = self.get_total_disease_counts()
        return self.render_to_response(self.get_context_data(**context))

    def get_total_disease_counts(self):
        # Returns total counts for each disease area.
        disease_counts = Sample.objects.aggregate(
            cancer_count=Count(Case(When(disease_area='Cancer', then=1), output_field=IntegerField())),
            rare_disease_count=Count(Case(When(disease_area='Rare Disease', then=1), output_field=IntegerField()))
        )
        return {
            'cancer': disease_counts['cancer_count'],
            'rare_disease': disease_counts['rare_disease_count']
        }

    def get_filtered_disease_counts(self, start_date, end_date):
        # Returns counts for each disease area within the specified date range.
        disease_counts = Sample.objects.aggregate(
            cancer_count=Count(Case(
                When(Q(disease_area='Cancer') & Q(sample_received_datetime__date__range=(start_date, end_date)),
                     then=1),
                output_field=IntegerField()
            )),
            rare_disease_count=Count(Case(
                When(Q(disease_area='Rare Disease') & Q(sample_received_datetime__date__range=(start_date, end_date)),
                     then=1),
                output_field=IntegerField()
            )),
        )
        return {
            'cancer': disease_counts['cancer_count'],
            'rare_disease': disease_counts['rare_disease_count']
        }


class MonthlyKpiView(LoginRequiredMixin, FormView):
    form_class = forms.MonthForm
    template_name = 'charts/monthly_kpi.html'
    context = {}

    def get(self, request, *args, **kwargs):
        today = datetime.today()
        month = today.month
        year = today.year

        glh_list = self.get_glh(year, month)
        self.context['all_glhs'] = glh_list
        self.context['form'] = self.get_form()
        return self.render_to_response(self.get_context_data(**self.context))

    def form_valid(self, form):
        date = form.cleaned_data['month']
        month = date.month
        year = date.year
        glh_list = self.get_glh(year, month)
        self.context['all_glhs'] = glh_list
        self.context['form'] = form

        return self.render_to_response(self.get_context_data(**self.context))

    def get_glh(self, year, month):
        glhs_list = []

        samples = Sample.objects.filter(
            receiving_rack__gel_1004_csv__report_received_datetime__year=year,
            receiving_rack__gel_1004_csv__report_received_datetime__month=month
        ).order_by("receiving_rack__gel_1004_csv__report_received_datetime")

        glhs = ["yne", "now", "eme", "lnn", "lns", "wwm", "sow"]
        for glh in glhs:
            rd_proband = samples.filter(sample_type="Proband", receiving_rack__laboratory_id=glh).count()
            rd_family = samples.filter(sample_type="Family", receiving_rack__laboratory_id=glh).count()
            cancer_germline = samples.filter(sample_type="Cancer Germline", receiving_rack__laboratory_id=glh).count()
            cancer_tumour = samples.filter(sample_type="Tumour", receiving_rack__laboratory_id=glh).count()
            troubleshooting_ongoing = samples.filter(issue_outcome="Not resolved",
                                                     receiving_rack__laboratory_id=glh).count()
            troubleshooting_discards = samples.filter(issue_outcome="Sample destroyed",
                                                      receiving_rack__laboratory_id=glh).count()
            troubleshooting_returns = samples.filter(issue_outcome="Sample returned to extracting GLH",
                                                     receiving_rack__laboratory_id=glh).count()
            total = samples.filter(receiving_rack__laboratory_id=glh).count()

            glhs_list.append({
                'glh': glh,
                'data': {
                    'rd_proband': rd_proband,
                    'rd_family': rd_family,
                    'cancer_germline': cancer_germline,
                    'cancer_tumour': cancer_tumour,
                    'troubleshooting_ongoing': troubleshooting_ongoing,
                    'troubleshooting_discards': troubleshooting_discards,
                    'troubleshooting_returns': troubleshooting_returns,
                    'total': total
                },
            })

        return json.dumps(glhs_list)


class MonthTotalView(LoginRequiredMixin, FormView):
    form_class = forms.MonthForm
    template_name = 'charts/monthly_total.html'
    context = {}

    def form_valid(self, form):
        date = form.cleaned_data['month']
        month = date.month
        year = date.year
        self.context['month_total'] = self.get_total(year, month)
        return self.render_to_response(self.get_context_data(**self.context))

    def get(self, request, *args, **kwargs):
        today = datetime.today()
        month = today.month
        year = today.year
        self.context['month_total'] = self.get_total(year, month)
        return self.render_to_response(self.get_context_data(**self.context))

    def get_total(self, year, month):
        glhs_list = []
        samples = Sample.objects.filter(
            receiving_rack__gel_1004_csv__report_received_datetime__year=year,
            receiving_rack__gel_1004_csv__report_received_datetime__month=month
        ).order_by("receiving_rack__gel_1004_csv__report_received_datetime")
        glhs = ["yne", "now", "eme", "lnn", "lns", "wwm", "sow"]
        for glh in glhs:
            total = samples.filter(receiving_rack__laboratory_id=glh).count()
            glhs_list.append({
                'glh': glh,
                'total': total
            })
        return glhs_list


class WeekTotalView(LoginRequiredMixin, FormView):
    template_name = 'charts/week_total.html'
    form_class = forms.WeekForm
    context = {}

    def form_valid(self, form):
        monday = form.cleaned_data['week']
        friday = monday + timedelta(days=4)
        self.context['week_total'] = self.week_total(monday, friday)

        return self.render_to_response(self.get_context_data(**self.context))

    def get(self, request, *args, **kwargs):
        monday_date, friday_date = self.get_current_week_monday()
        result = self.week_total(monday_date, friday_date)

        self.context['week_total'] = result
        self.context['form'] = self.get_form()
        return self.render_to_response(self.get_context_data(**self.context))

    def get_current_week_monday(self):
        today = datetime.today()
        monday = today - timedelta(days=today.weekday())
        friday = monday + timedelta(days=4)
        return monday.date(), friday.date()

    def week_total(self, start, end):
        glhs = ["yne", "now", "eme", "lnn", "lns", "wwm", "sow"]
        glhs_list = []
        samples = Sample.objects.filter(sample_received_datetime__range=(start, end))
        for glh in glhs:
            rd_proband = samples.filter(sample_type="Proband", receiving_rack__laboratory_id=glh).count()
            rd_family = samples.filter(sample_type="Family", receiving_rack__laboratory_id=glh).count()
            cancer_germline = samples.filter(sample_type="Cancer Germline", receiving_rack__laboratory_id=glh).count()
            cancer_tumour = samples.filter(sample_type="Tumour", receiving_rack__laboratory_id=glh).count()

            glhs_list.append(
                {'glh': glh,
                 'data': {
                     'rd_proband': rd_proband,
                     'rd_family': rd_family,
                     'cancer_germline': cancer_germline,
                     'cancer_tumour': cancer_tumour}
                 }
            )
        return glhs_list

