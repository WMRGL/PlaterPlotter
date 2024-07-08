from django.test import TestCase
from django.urls import reverse, resolve

from discards import views


class Urls(TestCase):

    def test_discards_index_url(self):
        url = reverse('discards:discards_index')
        self.assertEqual(resolve(url).func, views.discards_index)

    def test_all_discards_url(self):
        url = reverse('discards:all_discards_view')
        self.assertEqual(resolve(url).func, views.all_discards_view)
