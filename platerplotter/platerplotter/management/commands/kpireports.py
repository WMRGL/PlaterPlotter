from django.core.management.base import BaseCommand, CommandError
from platerplotter.models import Sample
from platerplotter.config.load_config import LoadConfig
import csv
import datetime

class Command(BaseCommand):
	help = 'Produces KPI reports'

	def has_gel1008(self,sample):
		has_gel1008 = False
		try:
			has_gel1008 = (sample.holding_rack_well.holding_rack.plate.gel_1008_csv is not None)
		except:
			pass
		return has_gel1008

	def handle(self, *args, **options):
		###########################################################################################################################################
		# for when a specific date range is needed - will need to be modified as required
		# samples = Sample.objects.filter(receiving_rack__gel_1004_csv__report_received_datetime__range=["2020-11-09", "2020-12-01"]).order_by("receiving_rack__gel_1004_csv__report_received_datetime")
		# file_name_start = '20201109-20201130-'
		###########################################################################################################################################
		# normal query will be all cases received the previous month
		dt = datetime.datetime.today()
		month = dt.month
		year = dt.year
		if month == 1:
			month = 12
			year = year - 1
		else:
			month = month - 1
		samples = Sample.objects.filter(receiving_rack__gel_1004_csv__report_received_datetime__year=year,
			receiving_rack__gel_1004_csv__report_received_datetime__month=month).order_by("receiving_rack__gel_1004_csv__report_received_datetime")
		if len(str(month)) == 1:
			month = "0" + str(month)
		file_name_start = str(year) + str(month) + '-'
		###########################################################################################################################################
		directory = LoadConfig().load()['kpi_path']
		with open(directory + file_name_start + 'KPI-TAT.csv', 'w', newline='') as csvfile:
			csv_writer = csv.writer(csvfile, delimiter=',')
			csv_writer.writerow(['SAMPLE','RECEIVED','GEL1005_GENERATED', 'TIME_TO_ACKNOWLEDGE', '24HR_TARGET_MET', 
				'SAMPLE_DISPATCHED', 'DAYS_FROM_RECEIVE_TO_DISPATCH', 'COMMENTS'])
			for sample in samples:
				sample_id = sample.laboratory_sample_id
				received = sample.sample_received_datetime
				if sample.receiving_rack.gel_1004_csv.gel_1005_csv:
					gel1005_generated = sample.receiving_rack.gel_1004_csv.gel_1005_csv.report_generated_datetime
				else:
					gel1005_generated = None
				if gel1005_generated and received:
					difference = gel1005_generated - received
					difference = difference - datetime.timedelta(microseconds=difference.microseconds)
				else:
					difference = None
				if difference:
					if datetime.timedelta(hours=24) > difference:
						target_met = True
					else:
						target_met = False
				else:
					difference_from_now = datetime.datetime.now(datetime.timezone.utc) - received
					if datetime.timedelta(hours=24) < difference_from_now:
						target_met = False
					else:
						target_met = None
				if self.has_gel1008(sample):
					dispatch_date = sample.holding_rack_well.holding_rack.plate.gel_1008_csv.date_of_dispatch
				else:
					dispatch_date = None
				if dispatch_date:
					days_to_dispatch = dispatch_date.date() - received.date()
					days_to_dispatch = days_to_dispatch.days
				else:
					days_to_dispatch = None
				if gel1005_generated:
					gel1005_generated = gel1005_generated.strftime("%d/%m/%y %H:%M:%S")
				if dispatch_date:
					dispatch_date = dispatch_date.strftime("%d/%m/%y")
				comment = sample.comment
				csv_writer.writerow([sample_id, received.strftime("%d/%m/%y %H:%M:%S"), gel1005_generated, 
					difference, target_met, dispatch_date, days_to_dispatch, comment])
		
		with open(directory + file_name_start + 'KPI-Sample-Breakdown.csv', 'w', newline='') as csvfile:
			glhs = ["yne", "now", "eme", "lnn", "lns", "wwm", "sow"]
			csv_writer = csv.writer(csvfile, delimiter=',')
			csv_writer.writerow(['GLH','RD_PROBAND','RD_FAMILY', 'CANCER_GERMLINE', 'CANCER_TUMOUR', 'TROUBLESHOOTING_ONGOING', 
				'TROUBLESHOOTING_DISCARDS', 'TROUBLESHOOTING_RETURNS', 'TOTALS'])
			for glh in glhs:
				rd_proband = samples.filter(sample_type="Proband", receiving_rack__laboratory_id=glh).count()
				rd_family = samples.filter(sample_type="Family", receiving_rack__laboratory_id=glh).count()
				cancer_germline = samples.filter(sample_type="Cancer Germline", receiving_rack__laboratory_id=glh).count()
				cancer_tumour = samples.filter(sample_type="Tumour", receiving_rack__laboratory_id=glh).count()
				troubleshooting_ongoing = samples.filter(issue_outcome="Not resolved", receiving_rack__laboratory_id=glh).count()
				troubleshooting_discards = samples.filter(issue_outcome="Sample destroyed", receiving_rack__laboratory_id=glh).count()
				troubleshooting_returns = samples.filter(issue_outcome="Sample returned to extracting GLH", receiving_rack__laboratory_id=glh).count()
				total = samples.filter(receiving_rack__laboratory_id=glh).count()
				csv_writer.writerow([glh.upper(), rd_proband, rd_family, cancer_germline, cancer_tumour, troubleshooting_ongoing, 
					troubleshooting_discards, troubleshooting_returns, total])
			rd_proband = samples.filter(sample_type="Proband").count()
			rd_family = samples.filter(sample_type="Family").count()
			cancer_germline = samples.filter(sample_type="Cancer Germline").count()
			cancer_tumour = samples.filter(sample_type="Tumour").count()
			troubleshooting_ongoing = samples.filter(issue_outcome="Not resolved").count()
			troubleshooting_discards = samples.filter(issue_outcome="Sample destroyed").count()
			troubleshooting_returns = samples.filter(issue_outcome="Sample returned to extracting GLH").count()
			total = samples.all().count()
			csv_writer.writerow(['TOTALS', rd_proband, rd_family, cancer_germline, cancer_tumour, troubleshooting_ongoing, 
					troubleshooting_discards, troubleshooting_returns, total])

		print("Reports generated in", directory)

