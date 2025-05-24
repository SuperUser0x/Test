from django.test import TestCase, Client as DjangoClient # Renamed to avoid conflict with models.Client
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.contrib.messages import get_messages
from unittest.mock import patch

from .models import Client
from .forms import WhatsAppMessageForm

class ClientModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_client_creation(self):
        client = Client.objects.create(
            name="Test Client",
            phone_number="1234567890",
            owner=self.user,
            email="test@example.com"
        )
        self.assertEqual(str(client), "Test Client")
        self.assertEqual(client.status, 'Lead') # Test default status
        self.assertEqual(client.owner, self.user)

class WhatsAppMessageFormTests(TestCase):
    def test_valid_form(self):
        form = WhatsAppMessageForm(data={'message': 'Hello there!'})
        self.assertTrue(form.is_valid())

    def test_invalid_form_empty_message(self):
        form = WhatsAppMessageForm(data={'message': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

class ClientViewTests(TestCase):
    def setUp(self):
        self.django_client = DjangoClient() # HTTP client
        self.user1 = User.objects.create_user(username='user1', password='password123', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='password123', email='user2@example.com')

        self.client1_user1 = Client.objects.create(name="Client1 User1", phone_number="111111", owner=self.user1)
        self.client2_user1 = Client.objects.create(name="Client2 User1", phone_number="222222", owner=self.user1)
        self.client1_user2 = Client.objects.create(name="Client1 User2", phone_number="333333", owner=self.user2)

        self.login_url = reverse('login')

    def _create_client(self, owner, name_prefix="Test Client"):
        return Client.objects.create(
            name=f"{name_prefix} {owner.username}",
            phone_number="000000",
            owner=owner
        )

    # Test views for unauthenticated access
    def test_client_list_view_unauthenticated(self):
        response = self.django_client.get(reverse('clients:client_list'))
        self.assertRedirects(response, f"{self.login_url}?next={reverse('clients:client_list')}")

    def test_client_detail_view_unauthenticated(self):
        url = reverse('clients:client_detail', kwargs={'pk': self.client1_user1.pk})
        response = self.django_client.get(url)
        self.assertRedirects(response, f"{self.login_url}?next={url}")

    def test_client_create_view_unauthenticated(self):
        url = reverse('clients:client_add')
        response = self.django_client.get(url)
        self.assertRedirects(response, f"{self.login_url}?next={url}")
        response_post = self.django_client.post(url, {})
        self.assertRedirects(response_post, f"{self.login_url}?next={url}")


    def test_client_update_view_unauthenticated(self):
        url = reverse('clients:client_edit', kwargs={'pk': self.client1_user1.pk})
        response = self.django_client.get(url)
        self.assertRedirects(response, f"{self.login_url}?next={url}")
        response_post = self.django_client.post(url, {})
        self.assertRedirects(response_post, f"{self.login_url}?next={url}")

    def test_client_delete_view_unauthenticated(self):
        url = reverse('clients:client_delete', kwargs={'pk': self.client1_user1.pk})
        response = self.django_client.get(url)
        self.assertRedirects(response, f"{self.login_url}?next={url}")
        response_post = self.django_client.post(url, {})
        self.assertRedirects(response_post, f"{self.login_url}?next={url}")

    def test_send_whatsapp_message_view_unauthenticated(self):
        url = reverse('clients:send_whatsapp_message', kwargs={'pk': self.client1_user1.pk})
        response = self.django_client.post(url, {'message': 'test'}) # POST only view mostly
        self.assertRedirects(response, f"{self.login_url}?next={url}")


    # ClientListView Tests
    def test_client_list_view_authenticated_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.get(reverse('clients:client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.client1_user1.name)
        self.assertContains(response, self.client2_user1.name)
        self.assertNotContains(response, self.client1_user2.name)

    # ClientCreateView Tests
    def test_client_create_view_get(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.get(reverse('clients:client_add'))
        self.assertEqual(response.status_code, 200)
        # Check if the form in context has the expected fields for a Client ModelForm
        form = response.context['form']
        expected_fields = ['name', 'phone_number', 'email', 'status', 'notes']
        for field_name in expected_fields:
            self.assertIn(field_name, form.fields)

    def test_client_create_view_post(self):
        self.django_client.login(username='user1', password='password123')
        initial_client_count = Client.objects.filter(owner=self.user1).count()
        client_data = {
            'name': 'New Client User1',
            'phone_number': '123456789',
            'email': 'newclient@example.com',
            'status': 'Contacted',
            'notes': 'Some notes'
        }
        response = self.django_client.post(reverse('clients:client_add'), client_data)
        self.assertRedirects(response, reverse('clients:client_list'))
        self.assertEqual(Client.objects.filter(owner=self.user1).count(), initial_client_count + 1)
        new_client = Client.objects.get(name='New Client User1', owner=self.user1)
        self.assertEqual(new_client.owner, self.user1)
        self.assertEqual(new_client.phone_number, '123456789')

    # ClientDetailView Tests
    def test_client_detail_view_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.get(reverse('clients:client_detail', kwargs={'pk': self.client1_user1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.client1_user1.name)
        self.assertIsInstance(response.context['whatsapp_form'], WhatsAppMessageForm)


    def test_client_detail_view_not_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.get(reverse('clients:client_detail', kwargs={'pk': self.client1_user2.pk}))
        self.assertEqual(response.status_code, 404)

    # ClientUpdateView Tests
    def test_client_update_view_get_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.get(reverse('clients:client_edit', kwargs={'pk': self.client1_user1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.client1_user1.name)

    def test_client_update_view_post_owner(self):
        self.django_client.login(username='user1', password='password123')
        updated_name = "Updated Client1 User1"
        client_data = {
            'name': updated_name,
            'phone_number': self.client1_user1.phone_number, # Keep existing
            'email': self.client1_user1.email or '',
            'status': 'Converted',
            'notes': 'Updated notes'
        }
        response = self.django_client.post(reverse('clients:client_edit', kwargs={'pk': self.client1_user1.pk}), client_data)
        self.assertRedirects(response, reverse('clients:client_list'))
        self.client1_user1.refresh_from_db()
        self.assertEqual(self.client1_user1.name, updated_name)
        self.assertEqual(self.client1_user1.status, 'Converted')

    def test_client_update_view_get_not_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.get(reverse('clients:client_edit', kwargs={'pk': self.client1_user2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_client_update_view_post_not_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.post(reverse('clients:client_edit', kwargs={'pk': self.client1_user2.pk}), {'name': 'Attempt Update'})
        self.assertEqual(response.status_code, 404)

    # ClientDeleteView Tests
    def test_client_delete_view_get_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.get(reverse('clients:client_delete', kwargs={'pk': self.client1_user1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.client1_user1.name)

    def test_client_delete_view_post_owner(self):
        self.django_client.login(username='user1', password='password123')
        initial_client_count = Client.objects.filter(owner=self.user1).count()
        response = self.django_client.post(reverse('clients:client_delete', kwargs={'pk': self.client1_user1.pk}))
        self.assertRedirects(response, reverse('clients:client_list'))
        self.assertEqual(Client.objects.filter(owner=self.user1).count(), initial_client_count - 1)
        with self.assertRaises(Client.DoesNotExist):
            Client.objects.get(pk=self.client1_user1.pk)

    def test_client_delete_view_get_not_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.get(reverse('clients:client_delete', kwargs={'pk': self.client1_user2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_client_delete_view_post_not_owner(self):
        self.django_client.login(username='user1', password='password123')
        response = self.django_client.post(reverse('clients:client_delete', kwargs={'pk': self.client1_user2.pk}))
        self.assertEqual(response.status_code, 404)


class SendWhatsAppMessageViewTests(TestCase):
    def setUp(self):
        self.django_client = DjangoClient()
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.client_user1 = Client.objects.create(name="Client User1", phone_number="1234567890", owner=self.user1)
        self.client_user2 = Client.objects.create(name="Client User2", phone_number="0987654321", owner=self.user2)

    def test_send_whatsapp_message_view_unauthenticated(self):
        url = reverse('clients:send_whatsapp_message', kwargs={'pk': self.client_user1.pk})
        response = self.django_client.post(url, {'message': 'test'})
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    @patch('builtins.print') # Mocks the print function
    def test_send_whatsapp_message_post_owner_success(self, mock_print):
        self.django_client.login(username='user1', password='password123')
        url = reverse('clients:send_whatsapp_message', kwargs={'pk': self.client_user1.pk})
        message_content = "Test WhatsApp message"
        
        response = self.django_client.post(url, {'message': message_content})
        
        self.assertRedirects(response, reverse('clients:client_detail', kwargs={'pk': self.client_user1.pk}))
        
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Simulated WhatsApp message sent to {self.client_user1.name}: '{message_content[:50]}...'")
        
        # Check print was called (simulation of sending)
        mock_print.assert_called_once_with(f"SIMULATING SENDING WHATSAPP to {self.client_user1.phone_number}: {message_content}")

    def test_send_whatsapp_message_post_invalid_form(self):
        self.django_client.login(username='user1', password='password123')
        url = reverse('clients:send_whatsapp_message', kwargs={'pk': self.client_user1.pk})
        
        response = self.django_client.post(url, {'message': ''}) # Empty message
        
        self.assertRedirects(response, reverse('clients:client_detail', kwargs={'pk': self.client_user1.pk}))
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertTrue("Error in 'Message'" in str(messages[0])) # Check part of the error message

    def test_send_whatsapp_message_post_not_owner(self):
        self.django_client.login(username='user1', password='password123')
        url = reverse('clients:send_whatsapp_message', kwargs={'pk': self.client_user2.pk})
        message_content = "Attempt to send"
        
        response = self.django_client.post(url, {'message': message_content})
        
        self.assertEqual(response.status_code, 404) # Should be forbidden/not found

    def test_send_whatsapp_message_get_redirects(self):
        self.django_client.login(username='user1', password='password123')
        url = reverse('clients:send_whatsapp_message', kwargs={'pk': self.client_user1.pk})
        response = self.django_client.get(url) # GET request
        self.assertRedirects(response, reverse('clients:client_detail', kwargs={'pk': self.client_user1.pk}))
