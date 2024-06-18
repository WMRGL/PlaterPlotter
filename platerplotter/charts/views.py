import json
from datetime import datetime

from django.db.models import Count, Case, When, IntegerField, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View, FormView

from platerplotter.models import Sample
from .forms import DateRangeForm


# Create your views here.

class CancerRareDiseaseView(FormView):
    template_name = 'charts/cancer_rd.html'
    form_class = DateRangeForm

    def form_valid(self, form):
        start_date = form.cleaned_data['start']
        end_date = form.cleaned_data['end']
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
                When(Q(disease_area='Cancer') & Q(sample_received_datetime__range=(start_date, end_date)), then=1),
                output_field=IntegerField()
            )),
            rare_disease_count=Count(Case(
                When(Q(disease_area='Rare Disease') & Q(sample_received_datetime__range=(start_date, end_date)), then=1),
                output_field=IntegerField()
            )),
        )
        return {
            'cancer': disease_counts['cancer_count'],
            'rare_disease': disease_counts['rare_disease_count']
        }


class KpiView(View):
    def get(self, request, *args, **kwargs):
        context = {}

        today = datetime.today()
        month = today.month
        year = today.year

        glh_list = self.get_glh(year, month)
        context['all_glhs'] = glh_list

        return render(request, 'charts/kpi.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        date = request.POST['month'].split('-')

        year, month = date[0], date[1]
        context['all_glhs'] = self.get_glh(year, month)
        return render(request, 'charts/kpi.html', context)

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
