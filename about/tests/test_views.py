from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }

        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse(reverse_name))

                self.assertTemplateUsed(response, template)

    def test_url_exists_at_desired_location(self):
        url_names = {
            'about:author': HTTPStatus.OK,
            'about:tech': HTTPStatus.OK,
        }

        for url_name, page_code in url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse(url_name))

                self.assertEqual(response.status_code, page_code)
