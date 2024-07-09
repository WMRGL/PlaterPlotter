from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from charts import views
from platerplotter.models import Sample, ReceivingRack, Gel1004Csv, Gel1005Csv


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

    def test_chart_cancer_rd(self):
        response = self.client.get(reverse('charts:cancer_rd'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'charts/cancer_rd.html')

    def test_cancer_rd_total(self):
        expected_result = {'cancer': 1, 'rare_disease': 1}
        self.assertEqual(self.cancer_rd.get_total_disease_counts(), expected_result)

    def test_cancer_rd_filtered_disease_counts(self):
        start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

        expected_cancer_count = Sample.objects.filter(
            Q(disease_area='Cancer') & Q(sample_received_datetime__range=(start_date, end_date))
        ).count()
        expected_rare_disease_count = Sample.objects.filter(
            Q(disease_area='Rare Disease') & Q(sample_received_datetime__range=(start_date, end_date))
        ).count()

        result = self.cancer_rd.get_filtered_disease_counts(start_date, end_date)

        self.assertEqual(result['cancer'], expected_cancer_count)
        self.assertEqual(result['rare_disease'], expected_rare_disease_count)

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
        now = datetime.now()
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
        today = datetime.today()
        month = today.month
        year = today.year
        expected_result = {}
        for glh in self.glhs:
            expected_result[glh] = Sample.objects.filter(
                receiving_rack__gel_1004_csv__report_received_datetime__year=year,
                receiving_rack__gel_1004_csv__report_received_datetime__month=month,
                receiving_rack__laboratory_id=glh
            ).count()

        result = self.monthly_total.get_total(year, month)
        # print result
        # for glh in self.glhs:
        #     self.assertEqual(result[glh]['total'], expected_result[glh])

    def test_get_glh(self):
        today = datetime.today()
        month = today.month
        year = today.year
        expected_result = {}
        for glh in self.glhs:
            expected_result[glh] = Sample.objects.filter(
                receiving_rack__gel_1004_csv__report_received_datetime__year=year,
                receiving_rack__gel_1004_csv__report_received_datetime__month=month,
                receiving_rack__laboratory_id=glh
            ).count()

        result = views.MonthlyKpiView().get_glh(year, month)
        # print result
        # for glh in self.glhs:
        #     self.assertEqual(result[glh]['total'], expected_result[glh])
        # self.assertEqual(expected_result, self.glhs)

    def test_chart_monthly_kpi(self):
        response = self.client.get(reverse('charts:month_total'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'charts/monthly_total.html')
