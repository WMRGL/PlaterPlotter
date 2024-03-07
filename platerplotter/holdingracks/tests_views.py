from django.contrib.auth.models import User
from django.test import TestCase, Client

import os
import pytz
import glob
from datetime import datetime, date

from django.urls import reverse

from platerplotter.models import Gel1004Csv, ReceivingRack, Sample, Gel1005Csv, HoldingRack, HoldingRackWell


# Create your tests here.
