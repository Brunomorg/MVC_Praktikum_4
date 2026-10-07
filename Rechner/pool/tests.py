from django.test import TestCase
from django.urls import reverse
from .models import Topic, Person, Expense


class TopicListViewTest(TestCase):

    def setUp(self):
        """Set up test data before each individual test."""
        # Resolve the URL dynamically by name from urls.py.
        self.url = reverse('topics_list')

        # Create a test topic in the test database.
        self.topic_1 = Topic.objects.create(title="Sommerurlaub 2026")

    def test_topic_list_view_get(self):
        """Check whether the topic list loads and renders correctly (GET)."""
        response = self.client.get(self.url)

        # 1. Check that the HTTP status code is 200 (OK).
        self.assertEqual(response.status_code, 200)

        # 2. Check that the correct template is rendered.
        self.assertTemplateUsed(response, 'pool/themen_liste.html')

        # 3. Check that the created topic appears in the HTML output.
        self.assertContains(response, "Sommerurlaub 2026")

        # 4. Check that the context variables exist.
        self.assertIn('topics', response.context)
        self.assertIn('form', response.context)
        self.assertEqual(len(response.context['topics']), 1)

    def test_topic_creation_success_post(self):
        """Test successful creation of a new topic via POST."""
        post_data = {
            'title': 'Wohnung renovieren'
        }

        # Send a POST request to the view.
        response = self.client.post(self.url, data=post_data)

        # 1. After a successful creation, a redirect (302) should happen.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)

        # 2. Check that the topic was actually saved in the test database.
        self.assertTrue(Topic.objects.filter(title='Wohnung renovieren').exists())
        self.assertEqual(Topic.objects.count(), 2)

    def test_topic_creation_invalid_post(self):
        """Test sending invalid form data (for example, an empty field)."""
        post_data = {
            'title': ''  # Empty string because the title is a required field in the model.
        }

        response = self.client.post(self.url, data=post_data)

        # 1. No redirect, but a status 200 (page is re-rendered with errors).
        self.assertEqual(response.status_code, 200)

        # 2. No new topic should have been created in the database.
        self.assertEqual(Topic.objects.count(), 1)

        # 3. The form in the context should contain validation errors.
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('title', form.errors)

    def test_topic_delete_post(self):
        """Test deleting an existing topic via POST."""
        response = self.client.post(self.url, data={
            'action': 'delete_topic',
            'topic_id': self.topic_1.id,
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        self.assertEqual(Topic.objects.count(), 0)