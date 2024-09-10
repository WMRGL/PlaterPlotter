# Generated by Django 3.2.23 on 2024-01-18 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gel1004Csv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=60)),
                ('plating_organisation', models.CharField(choices=[('yne', 'yne'), ('now', 'now'), ('eme', 'eme'), ('lnn', 'lnn'), ('lns', 'lns'), ('wwm', 'wwm'), ('sow', 'sow')], default='wwm', max_length=10)),
                ('report_received_datetime', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Gel1004 CSV',
                'verbose_name_plural': 'Gel1004 CSVs',
                'db_table': 'Gel1004Csv',
            },
        ),
        migrations.CreateModel(
            name='Gel1005Csv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=60)),
                ('report_generated_datetime', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Gel1005 CSV',
                'verbose_name_plural': 'Gel1005 CSVs',
                'db_table': 'Gel1005Csv',
            },
        ),
        migrations.CreateModel(
            name='Gel1008Csv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=60)),
                ('report_generated_datetime', models.DateTimeField()),
                ('consignment_number', models.CharField(blank=True, max_length=50, null=True)),
                ('date_of_dispatch', models.DateTimeField(blank=True, null=True)),
                ('consignment_collected', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Gel1008 CSV',
                'verbose_name_plural': 'Gel1008 CSVs',
                'db_table': 'Gel1008Csv',
            },
        ),
        migrations.CreateModel(
            name='HoldingRack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('holding_rack_id', models.CharField(max_length=11)),
                ('disease_area', models.CharField(choices=[('Cancer', 'Cancer'), ('Rare Disease', 'Rare Disease'), ('Unassigned', 'Unassigned')], default='Unassigned', max_length=12)),
                ('holding_rack_type', models.CharField(choices=[('Proband', 'Proband'), ('Family', 'Family'), ('Cancer Germline', 'Cancer Germline'), ('Tumour', 'Tumour'), ('Problem', 'Problem'), ('Unassigned', 'Unassigned')], default='Unassigned', max_length=15)),
                ('priority', models.CharField(choices=[('Routine', 'Routine'), ('Urgent', 'Urgent'), ('Unassigned', 'Unassigned')], default='Unassigned', max_length=10)),
                ('half_full', models.BooleanField(default=False)),
                ('full', models.BooleanField(default=False)),
                ('ready_to_plate', models.BooleanField(default=False)),
                ('positions_confirmed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Holding rack',
                'verbose_name_plural': 'Holding racks',
                'db_table': 'HoldingRack',
            },
        ),
        migrations.CreateModel(
            name='RackScanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=60)),
                ('scanned_id', models.CharField(max_length=13)),
                ('date_modified', models.DateTimeField()),
                ('acknowledged', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Rack scanner',
                'verbose_name_plural': 'Rack scanners',
                'db_table': 'RackScanner',
                'unique_together': {('filename', 'scanned_id', 'date_modified')},
            },
        ),
        migrations.CreateModel(
            name='ReceivingRack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiving_rack_id', models.CharField(max_length=12)),
                ('laboratory_id', models.CharField(choices=[('yne', 'yne'), ('now', 'now'), ('eme', 'eme'), ('lnn', 'lnn'), ('lns', 'lns'), ('wwm', 'wwm'), ('sow', 'sow')], max_length=3)),
                ('glh_sample_consignment_number', models.CharField(max_length=50)),
                ('rack_acknowledged', models.BooleanField(default=False)),
                ('volume_checked', models.BooleanField(default=False)),
                ('disease_area', models.CharField(blank=True, choices=[('Cancer', 'Cancer'), ('Rare Disease', 'Rare Disease'), ('Mixed', 'Mixed')], max_length=12, null=True)),
                ('rack_type', models.CharField(blank=True, choices=[('Proband', 'Proband'), ('Family', 'Family'), ('Cancer Germline', 'Cancer Germline'), ('Tumour', 'Tumour'), ('Mixed', 'Mixed')], max_length=15, null=True)),
                ('priority', models.CharField(blank=True, choices=[('Routine', 'Routine'), ('Urgent', 'Urgent'), ('Mixed', 'Mixed')], max_length=10, null=True)),
                ('gel_1004_csv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platerplotter.gel1004csv')),
            ],
            options={
                'verbose_name': 'Receiving rack',
                'verbose_name_plural': 'Receiving racks',
                'db_table': 'ReceivingRack',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=100, unique=True)),
                ('receiving_rack_well', models.CharField(choices=[('A01', 'A01'), ('A02', 'A02'), ('A03', 'A03'), ('A04', 'A04'), ('A05', 'A05'), ('A06', 'A06'), ('A07', 'A07'), ('A08', 'A08'), ('A09', 'A09'), ('A10', 'A10'), ('A11', 'A11'), ('A12', 'A12'), ('B01', 'B01'), ('B02', 'B02'), ('B03', 'B03'), ('B04', 'B04'), ('B05', 'B05'), ('B06', 'B06'), ('B07', 'B07'), ('B08', 'B08'), ('B09', 'B09'), ('B10', 'B10'), ('B11', 'B11'), ('B12', 'B12'), ('C01', 'C01'), ('C02', 'C02'), ('C03', 'C03'), ('C04', 'C04'), ('C05', 'C05'), ('C06', 'C06'), ('C07', 'C07'), ('C08', 'C08'), ('C09', 'C09'), ('C10', 'C10'), ('C11', 'C11'), ('C12', 'C12'), ('D01', 'D01'), ('D02', 'D02'), ('D03', 'D03'), ('D04', 'D04'), ('D05', 'D05'), ('D06', 'D06'), ('D07', 'D07'), ('D08', 'D08'), ('D09', 'D09'), ('D10', 'D10'), ('D11', 'D11'), ('D12', 'D12'), ('E01', 'E01'), ('E02', 'E02'), ('E03', 'E03'), ('E04', 'E04'), ('E05', 'E05'), ('E06', 'E06'), ('E07', 'E07'), ('E08', 'E08'), ('E09', 'E09'), ('E10', 'E10'), ('E11', 'E11'), ('E12', 'E12'), ('F01', 'F01'), ('F02', 'F02'), ('F03', 'F03'), ('F04', 'F04'), ('F05', 'F05'), ('F06', 'F06'), ('F07', 'F07'), ('F08', 'F08'), ('F09', 'F09'), ('F10', 'F10'), ('F11', 'F11'), ('F12', 'F12'), ('G01', 'G01'), ('G02', 'G02'), ('G03', 'G03'), ('G04', 'G04'), ('G05', 'G05'), ('G06', 'G06'), ('G07', 'G07'), ('G08', 'G08'), ('G09', 'G09'), ('G10', 'G10'), ('G11', 'G11'), ('G12', 'G12'), ('H01', 'H01'), ('H02', 'H02'), ('H03', 'H03'), ('H04', 'H04'), ('H05', 'H05'), ('H06', 'H06'), ('H07', 'H07'), ('H08', 'H08'), ('H09', 'H09'), ('H10', 'H10'), ('H11', 'H11'), ('H12', 'H12')], max_length=3)),
                ('participant_id', models.CharField(max_length=20)),
                ('group_id', models.CharField(max_length=20)),
                ('priority', models.CharField(choices=[('Routine', 'Routine'), ('Urgent', 'Urgent')], default='Routine', max_length=7)),
                ('disease_area', models.CharField(choices=[('Cancer', 'Cancer'), ('Rare Disease', 'Rare Disease')], max_length=12)),
                ('sample_type', models.CharField(choices=[('Proband', 'Proband'), ('Family', 'Family'), ('Cancer Germline', 'Cancer Germline'), ('Tumour', 'Tumour'), ('Unassigned', 'Unassigned')], default='Unassigned', max_length=15)),
                ('clin_sample_type', models.CharField(choices=[('dna_blood_germline', 'dna_blood_germline'), ('dna_saliva', 'dna_saliva'), ('dna_fibroblast', 'dna_fibroblast'), ('dna_ff_germline', 'dna_ff_germline'), ('dna_ffpe_tumour', 'dna_ffpe_tumour'), ('dna_ff_tumour', 'dna_ff_tumour'), ('dna_blood_tumour', 'dna_blood_tumour'), ('dna_bone_marrow_aspirate_tumour_sorted_cells', 'dna_bone_marrow_aspirate_tumour_sorted_cells'), ('dna_bone_marrow_aspirate_tumour_cells', 'dna_bone_marrow_aspirate_tumour_cells'), ('tumour_tissue_ffpe', 'tumour_tissue_ffpe'), ('lysate_ffpe', 'lysate_ffpe'), ('lysate_ff', 'lysate_ff'), ('lysed_tumour_cells', 'lysed_tumour_cells'), ('buffy_coat', 'buffy_coat'), ('streck_plasma', 'streck_plasma'), ('edta_plasma', 'edta_plasma'), ('lihep_plasma', 'lihep_plasma'), ('serum', 'serum'), ('rna_blood', 'rna_blood'), ('tumour_tissue_ff', 'tumour_tissue_ff'), ('bone_marrow_rna_gtc', 'bone_marrow_rna_gtc'), ('blood_rna_gtc', 'blood_rna_gtc'), ('dna_amniotic_fluid', 'dna_amniotic_fluid'), ('dna_fresh_amniotic_fluid', 'dna_fresh_amniotic_fluid'), ('dna_sorted_cd138_positive_cells', 'dna_sorted_cd138_positive_cells'), ('dna_edta_blood', 'dna_edta_blood'), ('dna_li_hep_blood', 'dna_li_hep_blood'), ('dna_bone_marrow', 'dna_bone_marrow'), ('dna_chorionic_villus_sample', 'dna_chorionic_villus_sample'), ('dna_fresh_chronic_villus_sample', 'dna_fresh_chronic_villus_sample'), ('dna_unknown', 'dna_unknown'), ('dna_unkown_tumour', 'dna_unkown_tumour'), ('dna_fetal_edta_blood', 'dna_fetal_edta_blood'), ('dna_fibroblast_culture', 'dna_fibroblast_culture'), ('dna_fresh_fluid_sorted_other', 'dna_fresh_fluid_sorted_other'), ('dna_fresh_fluid_unsorted', 'dna_fresh_fluid_unsorted'), ('dna_other', 'dna_other'), ('dna_fresh_frozen_tissue', 'dna_fresh_frozen_tissue'), ('dna_fresh_tissue_in_culture_medium', 'dna_fresh_tissue_in_culture_medium'), ('dna_fresh_fluid_tumour', 'dna_fresh_fluid_tumour'), ('dna_fresh_frozen_tumour', 'dna_fresh_frozen_tumour')], max_length=44)),
                ('laboratory_sample_id', models.CharField(max_length=10)),
                ('laboratory_sample_volume', models.IntegerField()),
                ('is_proband', models.BooleanField()),
                ('is_repeat', models.CharField(choices=[('New', 'New'), ('Retrospective', 'Retrospective'), ('Repeat New', 'Repeat New'), ('Repeat Retrospective', 'Repeat Retrospective')], default='New', max_length=50)),
                ('tissue_type', models.CharField(choices=[('Normal or Germline sample', 'Normal or Germline sample'), ('Liquid tumour sample', 'Liquid tumour sample'), ('Solid tumour sample', 'Solid tumour sample'), ('Abnormal tissue sample', 'Abnormal tissue sample'), ('Omics sample', 'Omics sample')], max_length=50)),
                ('sample_delivery_mode', models.CharField(blank=True, choices=[('Tumour First', 'Tumour First'), ('Germline Late', 'Germline Late'), ('Family Only', 'Family Only'), ('Standard', 'Standard')], default='Standard', max_length=50)),
                ('sample_received', models.BooleanField(default=False)),
                ('sample_matched', models.BooleanField(default=False)),
                ('sample_received_datetime', models.DateTimeField(null=True)),
                ('norm_biorep_sample_vol', models.FloatField(blank=True, null=True)),
                ('norm_biorep_conc', models.FloatField(blank=True, null=True)),
                ('issue_identified', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True, null=True)),
                ('issue_outcome', models.CharField(blank=True, choices=[('Not resolved', 'Not resolved'), ('Ready for plating', 'Ready for plating'), ('Sample returned to extracting GLH', 'Sample returned to extracting GLH'), ('Sample destroyed', 'Sample destroyed')], max_length=64, null=True)),
                ('bypass_plating_rules', models.BooleanField(default=False)),
                ('receiving_rack', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platerplotter.receivingrack')),
            ],
            options={
                'verbose_name': 'Sample',
                'verbose_name_plural': 'Samples',
                'db_table': 'Sample',
            },
        ),
        migrations.CreateModel(
            name='Plate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plate_id', models.CharField(max_length=13, unique=True)),
                ('gel_1008_csv', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_plate', to='platerplotter.gel1008csv')),
            ],
            options={
                'verbose_name': 'Plate',
                'verbose_name_plural': 'Plates',
                'db_table': 'Plate',
            },
        ),
        migrations.CreateModel(
            name='HoldingRackWell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('well_id', models.CharField(choices=[('A01', 'A01'), ('A02', 'A02'), ('A03', 'A03'), ('A04', 'A04'), ('A05', 'A05'), ('A06', 'A06'), ('A07', 'A07'), ('A08', 'A08'), ('A09', 'A09'), ('A10', 'A10'), ('A11', 'A11'), ('A12', 'A12'), ('B01', 'B01'), ('B02', 'B02'), ('B03', 'B03'), ('B04', 'B04'), ('B05', 'B05'), ('B06', 'B06'), ('B07', 'B07'), ('B08', 'B08'), ('B09', 'B09'), ('B10', 'B10'), ('B11', 'B11'), ('B12', 'B12'), ('C01', 'C01'), ('C02', 'C02'), ('C03', 'C03'), ('C04', 'C04'), ('C05', 'C05'), ('C06', 'C06'), ('C07', 'C07'), ('C08', 'C08'), ('C09', 'C09'), ('C10', 'C10'), ('C11', 'C11'), ('C12', 'C12'), ('D01', 'D01'), ('D02', 'D02'), ('D03', 'D03'), ('D04', 'D04'), ('D05', 'D05'), ('D06', 'D06'), ('D07', 'D07'), ('D08', 'D08'), ('D09', 'D09'), ('D10', 'D10'), ('D11', 'D11'), ('D12', 'D12'), ('E01', 'E01'), ('E02', 'E02'), ('E03', 'E03'), ('E04', 'E04'), ('E05', 'E05'), ('E06', 'E06'), ('E07', 'E07'), ('E08', 'E08'), ('E09', 'E09'), ('E10', 'E10'), ('E11', 'E11'), ('E12', 'E12'), ('F01', 'F01'), ('F02', 'F02'), ('F03', 'F03'), ('F04', 'F04'), ('F05', 'F05'), ('F06', 'F06'), ('F07', 'F07'), ('F08', 'F08'), ('F09', 'F09'), ('F10', 'F10'), ('F11', 'F11'), ('F12', 'F12'), ('G01', 'G01'), ('G02', 'G02'), ('G03', 'G03'), ('G04', 'G04'), ('G05', 'G05'), ('G06', 'G06'), ('G07', 'G07'), ('G08', 'G08'), ('G09', 'G09'), ('G10', 'G10'), ('G11', 'G11'), ('G12', 'G12'), ('H01', 'H01'), ('H02', 'H02'), ('H03', 'H03'), ('H04', 'H04'), ('H05', 'H05'), ('H06', 'H06'), ('H07', 'H07'), ('H08', 'H08'), ('H09', 'H09'), ('H10', 'H10'), ('H11', 'H11'), ('H12', 'H12')], max_length=3)),
                ('buffer_added', models.BooleanField(default=False)),
                ('holding_rack', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wells', to='platerplotter.holdingrack')),
                ('sample', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='holding_rack_well', to='platerplotter.sample')),
            ],
            options={
                'verbose_name': 'Holding rack well',
                'verbose_name_plural': 'Holding rack wells',
                'db_table': 'HoldingRackWell',
            },
        ),
        migrations.AddField(
            model_name='holdingrack',
            name='plate',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='holding_rack', to='platerplotter.plate'),
        ),
        migrations.AddField(
            model_name='gel1004csv',
            name='gel_1005_csv',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='platerplotter.gel1005csv'),
        ),
        migrations.CreateModel(
            name='RackScannerSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_id', models.CharField(max_length=10)),
                ('position', models.CharField(choices=[('A01', 'A01'), ('A02', 'A02'), ('A03', 'A03'), ('A04', 'A04'), ('A05', 'A05'), ('A06', 'A06'), ('A07', 'A07'), ('A08', 'A08'), ('A09', 'A09'), ('A10', 'A10'), ('A11', 'A11'), ('A12', 'A12'), ('B01', 'B01'), ('B02', 'B02'), ('B03', 'B03'), ('B04', 'B04'), ('B05', 'B05'), ('B06', 'B06'), ('B07', 'B07'), ('B08', 'B08'), ('B09', 'B09'), ('B10', 'B10'), ('B11', 'B11'), ('B12', 'B12'), ('C01', 'C01'), ('C02', 'C02'), ('C03', 'C03'), ('C04', 'C04'), ('C05', 'C05'), ('C06', 'C06'), ('C07', 'C07'), ('C08', 'C08'), ('C09', 'C09'), ('C10', 'C10'), ('C11', 'C11'), ('C12', 'C12'), ('D01', 'D01'), ('D02', 'D02'), ('D03', 'D03'), ('D04', 'D04'), ('D05', 'D05'), ('D06', 'D06'), ('D07', 'D07'), ('D08', 'D08'), ('D09', 'D09'), ('D10', 'D10'), ('D11', 'D11'), ('D12', 'D12'), ('E01', 'E01'), ('E02', 'E02'), ('E03', 'E03'), ('E04', 'E04'), ('E05', 'E05'), ('E06', 'E06'), ('E07', 'E07'), ('E08', 'E08'), ('E09', 'E09'), ('E10', 'E10'), ('E11', 'E11'), ('E12', 'E12'), ('F01', 'F01'), ('F02', 'F02'), ('F03', 'F03'), ('F04', 'F04'), ('F05', 'F05'), ('F06', 'F06'), ('F07', 'F07'), ('F08', 'F08'), ('F09', 'F09'), ('F10', 'F10'), ('F11', 'F11'), ('F12', 'F12'), ('G01', 'G01'), ('G02', 'G02'), ('G03', 'G03'), ('G04', 'G04'), ('G05', 'G05'), ('G06', 'G06'), ('G07', 'G07'), ('G08', 'G08'), ('G09', 'G09'), ('G10', 'G10'), ('G11', 'G11'), ('G12', 'G12'), ('H01', 'H01'), ('H02', 'H02'), ('H03', 'H03'), ('H04', 'H04'), ('H05', 'H05'), ('H06', 'H06'), ('H07', 'H07'), ('H08', 'H08'), ('H09', 'H09'), ('H10', 'H10'), ('H11', 'H11'), ('H12', 'H12')], max_length=3)),
                ('matched', models.BooleanField(default=False)),
                ('rack_scanner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platerplotter.rackscanner')),
            ],
            options={
                'verbose_name': 'Rack scanner sample',
                'verbose_name_plural': 'Rack scanner samples',
                'db_table': 'RackScannerSample',
                'unique_together': {('rack_scanner', 'sample_id', 'position')},
            },
        ),
    ]
