from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from notifications.choices import well_ids, sample_types
from platerplotter.choices import lab_ids


class Gel1005Csv(models.Model):
    filename = models.CharField(max_length=60)
    report_generated_datetime = models.DateTimeField()

    def __str__(self):
        return self.filename

    class Meta:
        app_label = 'platerplotter'
        db_table = 'Gel1005Csv'
        verbose_name = 'Gel1005 CSV'
        verbose_name_plural = 'Gel1005 CSVs'


class Gel1004Csv(models.Model):
    gel_1005_csv = models.ForeignKey(Gel1005Csv, on_delete=models.CASCADE, null=True, blank=True)
    filename = models.CharField(max_length=60)
    plating_organisation = models.CharField(max_length=10, choices=lab_ids, default="wwm")
    report_received_datetime = models.DateTimeField()

    def __str__(self):
        return self.filename

    class Meta:
        app_label = 'platerplotter'
        db_table = 'Gel1004Csv'
        verbose_name = 'Gel1004 CSV'
        verbose_name_plural = 'Gel1004 CSVs'


class Gel1008Csv(models.Model):
    filename = models.CharField(max_length=60)
    report_generated_datetime = models.DateTimeField()
    consignment_number = models.CharField(max_length=50, null=True, blank=True)
    date_of_dispatch = models.DateTimeField(null=True, blank=True)
    consignment_collected = models.BooleanField(default=False)

    def __str__(self):
        return self.filename

    class Meta:
        app_label = 'platerplotter'
        db_table = 'Gel1008Csv'
        verbose_name = 'Gel1008 CSV'
        verbose_name_plural = 'Gel1008 CSVs'


class ReceivingRack(models.Model):
    gel_1004_csv = models.ForeignKey(Gel1004Csv, on_delete=models.CASCADE)
    receiving_rack_id = models.CharField(max_length=12)
    laboratory_id = models.CharField(max_length=3, choices=lab_ids)
    glh_sample_consignment_number = models.CharField(max_length=50)
    rack_acknowledged = models.BooleanField(default=False)
    volume_checked = models.BooleanField(default=False)
    disease_area = models.CharField(max_length=12, choices=(
        ("Cancer", "Cancer"),
        ("Rare Disease", "Rare Disease"),
        ("Mixed", "Mixed")), null=True, blank=True)
    rack_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
                                                         ("Family", "Family"), ("Cancer Germline", "Cancer Germline"),
                                                         ("Tumour", "Tumour"), ("Mixed", "Mixed")), null=True,
                                 blank=True)
    priority = models.CharField(max_length=10, choices=(("Routine", "Routine"),
                                                        ("Urgent", "Urgent"), ("Mixed", "Mixed")), null=True,
                                blank=True)

    def __str__(self):
        return self.receiving_rack_id

    def is_empty(self):
        samples = Sample.objects.filter(receiving_rack=self)
        empty = True
        for sample in samples:
            if not hasattr(sample, 'holding_rack_well'):
                empty = False
        return empty

    class Meta:
        app_label = 'platerplotter'
        db_table = 'ReceivingRack'
        verbose_name = 'Receiving rack'
        verbose_name_plural = 'Receiving racks'


class Plate(models.Model):
    gel_1008_csv = models.ForeignKey(Gel1008Csv, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='related_plate')
    plate_id = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return self.plate_id

    class Meta:
        app_label = 'platerplotter'
        db_table = 'Plate'
        verbose_name = 'Plate'
        verbose_name_plural = 'Plates'


class HoldingRack(models.Model):
    plate = models.OneToOneField(Plate, on_delete=models.CASCADE, null=True, blank=True, related_name='holding_rack')
    holding_rack_id = models.CharField(max_length=11)
    disease_area = models.CharField(max_length=12, choices=(
        ("Cancer", "Cancer"),
        ("Rare Disease", "Rare Disease"),
        ("Unassigned", "Unassigned")), default="Unassigned")
    holding_rack_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
                                                                 ("Family", "Family"),
                                                                 ("Cancer Germline", "Cancer Germline"),
                                                                 ("Tumour", "Tumour"), ("Problem", "Problem"),
                                                                 ("Unassigned", "Unassigned")), default="Unassigned")
    priority = models.CharField(max_length=10, choices=(("Routine", "Routine"),
                                                        ("Urgent", "Urgent"),
                                                        ("Unassigned", "Unassigned")), default="Unassigned")
    half_full = models.BooleanField(default=False)
    full = models.BooleanField(default=False)
    ready_to_plate = models.BooleanField(default=False)
    positions_confirmed = models.BooleanField(default=False)
    discarded = models.BooleanField(default=False)
    discarded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    checked_by = models.CharField(max_length=120, null=True, blank=True)
    discard_date = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return "Holding Rack ID: " + self.holding_rack_id

    class Meta:
        app_label = 'platerplotter'
        db_table = 'HoldingRack'
        verbose_name = 'Holding rack'
        verbose_name_plural = 'Holding racks'


class Sample(models.Model):
    uid = models.CharField(max_length=100, unique=True)
    receiving_rack = models.ForeignKey(ReceivingRack, on_delete=models.CASCADE)
    receiving_rack_well = models.CharField(max_length=3, choices=well_ids)
    participant_id = models.CharField(max_length=20)
    group_id = models.CharField(max_length=20)
    priority = models.CharField(max_length=7, choices=(("Routine", "Routine"),
                                                       ("Urgent", "Urgent")), default="Routine")
    disease_area = models.CharField(max_length=12, choices=(
        ("Cancer", "Cancer"),
        ("Rare Disease", "Rare Disease")))
    sample_type = models.CharField(max_length=15, choices=(("Proband", "Proband"),
                                                           ("Family", "Family"), ("Cancer Germline", "Cancer Germline"),
                                                           ("Tumour", "Tumour"), ("Unassigned", "Unassigned")),
                                   default="Unassigned")
    clin_sample_type = models.CharField(max_length=44, choices=sample_types)
    laboratory_sample_id = models.CharField(max_length=10)
    laboratory_sample_volume = models.IntegerField()
    is_proband = models.BooleanField()
    is_repeat = models.CharField(max_length=50, choices=(("New", "New"),
                                                         ("Retrospective", "Retrospective"),
                                                         ("Repeat New", "Repeat New"),
                                                         ("Repeat Retrospective", "Repeat Retrospective")),
                                 default="New")
    tissue_type = models.CharField(max_length=50, choices=(("Normal or Germline sample", "Normal or Germline sample"),
                                                           ("Liquid tumour sample", "Liquid tumour sample"),
                                                           ("Solid tumour sample", "Solid tumour sample"),
                                                           ("Abnormal tissue sample", "Abnormal tissue sample"),
                                                           ("Omics sample", "Omics sample")))
    sample_delivery_mode = models.CharField(max_length=50, blank=True, default="Standard",
                                            choices=(("Tumour First", "Tumour First"),
                                                     ("Germline Late", "Germline Late"), ("Family Only", "Family Only"),
                                                     ("Standard", "Standard")))
    sample_received = models.BooleanField(default=False)
    sample_matched = models.BooleanField(default=False)
    sample_received_datetime = models.DateTimeField(null=True)
    norm_biorep_sample_vol = models.FloatField(null=True, blank=True)
    norm_biorep_conc = models.FloatField(null=True, blank=True)
    issue_identified = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    issue_outcome = models.CharField(max_length=64, choices=(("Not resolved", "Not resolved"),
                                                             ("Ready for plating", "Ready for plating"),
                                                             ("Sample returned to extracting GLH",
                                                              "Sample returned to extracting GLH"),
                                                             ("Sample destroyed", "Sample destroyed")), blank=True,
                                     null=True)
    bypass_plating_rules = models.BooleanField(default=False)

    def __str__(self):
        return self.laboratory_sample_id

    def get_absolute_url(self):
        return reverse('ready:sample_comment', kwargs={'pk': self.pk})

    class Meta:
        app_label = 'platerplotter'
        db_table = 'Sample'
        verbose_name = 'Sample'
        verbose_name_plural = 'Samples'


class HoldingRackWell(models.Model):
    holding_rack = models.ForeignKey(HoldingRack, on_delete=models.CASCADE, related_name='wells')
    well_id = models.CharField(max_length=3, choices=well_ids)
    buffer_added = models.BooleanField(default=False)
    sample = models.OneToOneField(Sample, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='holding_rack_well')

    def __str__(self):
        return self.holding_rack.holding_rack_id + ' ' + self.well_id

    class Meta:
        app_label = 'platerplotter'
        db_table = 'HoldingRackWell'
        verbose_name = 'Holding rack well'
        verbose_name_plural = 'Holding rack wells'


class RackScanner(models.Model):
    filename = models.CharField(max_length=60)
    scanned_id = models.CharField(max_length=13)
    date_modified = models.DateTimeField()
    acknowledged = models.BooleanField(default=False)

    class Meta:
        unique_together = (('filename', 'scanned_id', 'date_modified'),)
        app_label = 'platerplotter'
        db_table = 'RackScanner'
        verbose_name = 'Rack scanner'
        verbose_name_plural = 'Rack scanners'

    def __str__(self):
        return self.filename + ' ' + str(self.date_modified)


class RackScannerSample(models.Model):
    rack_scanner = models.ForeignKey(RackScanner, on_delete=models.CASCADE)
    sample_id = models.CharField(max_length=10)
    position = models.CharField(max_length=3, choices=well_ids)
    matched = models.BooleanField(default=False)

    class Meta:
        unique_together = (('rack_scanner', 'sample_id', 'position'))
        app_label = 'platerplotter'
        db_table = 'RackScannerSample'
        verbose_name = 'Rack scanner sample'
        verbose_name_plural = 'Rack scanner samples'

    def __str__(self):
        return self.rack_scanner.scanned_id + ': ' + self.sample_id
