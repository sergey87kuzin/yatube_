from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_url_exists_at_desired_location(self):
        url_names = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for url_name, page_code in url_names.items():
            with self.subTest():
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, page_code)
