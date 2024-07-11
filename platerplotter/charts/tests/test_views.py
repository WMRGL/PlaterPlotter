import json
from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from charts import views
from platerplotter.models import Sample, ReceivingRack, Gel1004Csv, Gel1005Csv


def retrieve_samples_by_date(start_date, end_date):
    samples = Sample.objects.filter(sample_received_datetime__range=(start_date, end_date))
    return samples

class Chart(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testing12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        gel_1005_csv = Gel1005Csv.objects.create(filename='test1005.csv',
                                                 report_generated_datetime=datetime.now(pytz.timezone('UTC')))
        gel_1004_csv = Gel1004Csv.objects.create(filename='test1004.csv', gel_1005_csv=gel_1005_csv,
                                                 plating_organisation='wwm',
                                                 report_received_datetime=datetime.now(pytz.timezone('UTC')))
        self.gel_1004_pk = gel_1004_csv.pk
        receiving_rack = ReceivingRack.objects.create(gel_1004_csv=gel_1004_csv,
                                                      receiving_rack_id='SA12345678', laboratory_id='now',
                                                      glh_sample_consignment_number='abc-1234-12-12-12-1',
                                                      rack_acknowledged=False, disease_area='Rare Disease',
                                                      rack_type='Proband', priority='Routine')
        Sample.objects.create(receiving_rack=receiving_rack,
                              receiving_rack_well='A01', participant_id='p12345678901',
                              group_id='r12345678901', priority='Routine',
                              disease_area='Rare Disease', sample_type='Proband',
                              clin_sample_type='dna_saliva', laboratory_sample_id='1234567890',
                              uid='1234567890',
                              laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                              tissue_type='Normal or Germline sample', sample_received=True,
                              sample_received_datetime=timezone.now())
        Sample.objects.create(receiving_rack=receiving_rack,
                              receiving_rack_well='C01', participant_id='p12345678908',
                              group_id='r12345678908', priority='Routine',
                              disease_area='Cancer', sample_type='Tumour',
                              clin_sample_type='dna_saliva', laboratory_sample_id='1234567897',
                              uid='1234567897',
                              laboratory_sample_volume=10, is_proband=True, is_repeat='New',
                              tissue_type='Normal or Germline sample', sample_received=True,
                              sample_received_datetime=timezone.now())
        self.cancer_rd = views.CancerRareDiseaseView()
        self.weekly_total = views.WeekTotalView()
        self.monthly_total = views.MonthTotalView()
        self.glhs = ["yne", "now", "eme", "lnn", "lns", "wwm", "sow"]
        self.sample_type = ["Proband", "Family", "Tumour", "Cancer Germline"]
        self.today = datetime.today()
        self.month = self.today.month
        self.year = self.today.year
        self.monthly_expected_result = {}
        for glh in self.glhs:
            self.monthly_expected_result[glh] = Sample.objects.filter(
                receiving_rack__gel_1004_csv__report_received_datetime__year=self.year,
                receiving_rack__gel_1004_csv__report_received_datetime__month=self.month,
                receiving_rack__laboratory_id=glh
            ).count()
        self.monthly_kpi_expected_result = []
        samples = Sample.objects.filter(
            receiving_rack__gel_1004_csv__report_received_datetime__year=self.year,
            receiving_rack__gel_1004_csv__report_received_datetime__month=self.month
        ).order_by("receiving_rack__gel_1004_csv__report_received_datetime")
        for glh in self.glhs:
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
            self.monthly_kpi_expected_result.append({
                'glh': glh,
                'data': {
                    'rd_proband': rd_proband,
                    'rd_family': rd_family,
                    'cancer_germline': cancer_germline,
                    'cancer_tumour': cancer_tumour,
                    'troubleshooting_ongoing': troubleshooting_ongoing,
                    'troubleshooting_discards': troubleshooting_discards,
                    'troubleshooting_returns': troubleshooting_returns,
                },
            })

    def test_chart_cancer_rd(self):
        response = self.client.get(reverse('charts:cancer_rd'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'charts/cancer_rd.html')
        self.assertEqual(response.context['cancer'], 1)
        self.assertEqual(response.context['rare_disease'], 1)

    def test_cancer_rd_filtered_disease_counts(self):
        start_date = self.today.date()
        end_date = self.today.date()

        start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()),
                                             timezone.get_current_timezone())
        end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()),
                                           timezone.get_current_timezone())

        response = self.client.post(reverse('charts:cancer_rd'), {
            'range_calendar': f'{start_date} to {end_date}'
        })

        expected_cancer_count = Sample.objects.filter(
            Q(disease_area='Cancer') & Q(sample_received_datetime__range=(start_datetime, end_datetime))
        ).count()
        expected_rare_disease_count = Sample.objects.filter(
            Q(disease_area='Rare Disease') & Q(sample_received_datetime__range=(start_datetime, end_datetime))
        ).count()

        print(f"Expected Cancer Count: {expected_cancer_count}")
        print(f"Expected Rare Disease Count: {expected_rare_disease_count}")

        print(f"Response Cancer Count: {response.context['cancer']}")
        print(f"Response Rare Disease Count: {response.context['rare_disease']}")

        self.assertEqual(response.context['cancer'], expected_cancer_count)
        self.assertEqual(response.context['rare_disease'], expected_rare_disease_count)

    def test_chart_weekly_kpi(self):
        response = self.client.get(reverse('charts:week_total'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'charts/week_total.html')

    def test_weekly_total(self):
        expected_result = {}
        for sample_type in self.sample_type:
            expected_result[sample_type] = Sample.objects.filter(sample_type=sample_type,
                                                                 receiving_rack__laboratory_id='now'
                                                                 ).count()

        monday, friday = self.weekly_total.get_current_week_monday()
        result = self.weekly_total.week_total(monday, friday)

        self.assertEqual(result[1]['data']['rd_proband'], expected_result['Proband'])
        self.assertEqual(result[1]['data']['rd_family'], expected_result['Family'])
        self.assertEqual(result[1]['data']['cancer_germline'], expected_result['Cancer Germline'])
        self.assertEqual(result[1]['data']['cancer_tumour'], expected_result['Tumour'])

    def test_weekly_total_filtered(self):
        now = datetime.today()
        monday = now - timedelta(days=now.weekday())
        iso_week = monday.strftime('%G-W%V')

        response = self.client.post(reverse('charts:week_total'), {'week': iso_week})

        self.assertEqual(response.status_code, 200)
        self.assertIn('week_total', response.context)
        week_total = response.context['week_total']
        self.assertIsInstance(week_total, list)
        self.assertEqual(week_total[1]['data']['rd_proband'], 1)
        self.assertEqual(week_total[1]['data']['rd_family'], 0)
        self.assertEqual(week_total[1]['data']['cancer_germline'], 0)
        self.assertEqual(week_total[1]['data']['cancer_tumour'], 1)

        for glh_data in week_total:
            self.assertIn('glh', glh_data)
            self.assertIn('data', glh_data)
            data = glh_data['data']
            self.assertIn('rd_proband', data)
            self.assertIn('rd_family', data)
            self.assertIn('cancer_germline', data)
            self.assertIn('cancer_tumour', data)
            self.assertIsInstance(data['rd_proband'], int)
            self.assertIsInstance(data['rd_family'], int)
            self.assertIsInstance(data['cancer_germline'], int)
            self.assertIsInstance(data['cancer_tumour'], int)

    def test_chart_monthly_total(self):
        response = self.client.get(reverse('charts:month_total'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'charts/monthly_total.html')

    def test_monthly_total(self):
        response = self.client.get(reverse('charts:month_total'))
        result = self.monthly_total.get_total(self.year, self.month)
        for glh in range(len(self.glhs)):
            self.assertEqual(result[glh]['total'], self.monthly_expected_result[self.glhs[glh]])
            self.assertEqual(response.context['month_total'][glh]['total'],
                             self.monthly_expected_result[self.glhs[glh]])

    def test_monthly_total_filtered(self):
        response = self.client.post(reverse('charts:month_total'), {'month': f'{self.year}-{self.month}'})
        month_total = response.context['month_total']

        self.assertEqual(response.status_code, 200)
        self.assertIn('month_total', response.context)
        self.assertIsInstance(month_total, list)

        for glh in range(len(self.glhs)):
            self.assertEqual(response.context['month_total'][glh]['total'],
                             self.monthly_expected_result[self.glhs[glh]])

        for glh_data in month_total:
            self.assertIn('glh', glh_data)
            self.assertIn('total', glh_data)
            self.assertIsInstance(glh_data['total'], int)

    def test_monthly_kpi(self):
        response = self.client.get(reverse('charts:kpi'))
        all_glhs_json = response.context['all_glhs']
        all_glhs = json.loads(all_glhs_json)

        for glh in range(len(self.glhs)):
            self.assertEqual(all_glhs[glh]['glh'], self.monthly_kpi_expected_result[glh]['glh'])
            self.assertEqual(all_glhs[glh]['data']['rd_proband'],
                             self.monthly_kpi_expected_result[glh]['data']['rd_proband'])
            self.assertEqual(all_glhs[glh]['data']['rd_family'],
                             self.monthly_kpi_expected_result[glh]['data']['rd_family'])
            self.assertEqual(all_glhs[glh]['data']['cancer_germline'],
                             self.monthly_kpi_expected_result[glh]['data']['cancer_germline'])
            self.assertEqual(all_glhs[glh]['data']['cancer_tumour'],
                             self.monthly_kpi_expected_result[glh]['data']['cancer_tumour'])
            self.assertEqual(all_glhs[glh]['data']['troubleshooting_ongoing'],
                             self.monthly_kpi_expected_result[glh]['data']['troubleshooting_ongoing'])
            self.assertEqual(all_glhs[glh]['data']['troubleshooting_discards'],
                             self.monthly_kpi_expected_result[glh]['data']['troubleshooting_discards'])
            self.assertEqual(all_glhs[glh]['data']['troubleshooting_returns'],
                             self.monthly_kpi_expected_result[glh]['data']['troubleshooting_returns'])

    def test_monthly_kpi_filtered(self):
        response = self.client.post(reverse('charts:kpi'), {'month': f'{self.year}-{self.month}'})
        all_glhs_json = response.context['all_glhs']
        all_glhs = json.loads(all_glhs_json)

        for glh in range(len(self.glhs)):
            self.assertEqual(all_glhs[glh]['glh'], self.monthly_kpi_expected_result[glh]['glh'])
            self.assertEqual(all_glhs[glh]['data']['rd_proband'],
                             self.monthly_kpi_expected_result[glh]['data']['rd_proband'])
            self.assertEqual(all_glhs[glh]['data']['rd_family'],
                             self.monthly_kpi_expected_result[glh]['data']['rd_family'])
            self.assertEqual(all_glhs[glh]['data']['cancer_germline'],
                             self.monthly_kpi_expected_result[glh]['data']['cancer_germline'])
            self.assertEqual(all_glhs[glh]['data']['cancer_tumour'],
                             self.monthly_kpi_expected_result[glh]['data']['cancer_tumour'])
            self.assertEqual(all_glhs[glh]['data']['troubleshooting_ongoing'],
                             self.monthly_kpi_expected_result[glh]['data']['troubleshooting_ongoing'])
            self.assertEqual(all_glhs[glh]['data']['troubleshooting_discards'],
                             self.monthly_kpi_expected_result[glh]['data']['troubleshooting_discards'])
            self.assertEqual(all_glhs[glh]['data']['troubleshooting_returns'],
                             self.monthly_kpi_expected_result[glh]['data']['troubleshooting_returns'])

    def test_chart_monthly_kpi(self):
        response = self.client.get(reverse('charts:month_total'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'charts/monthly_total.html')
