from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.views import View
from django.contrib import messages
from .models import Client
from .forms import WhatsAppMessageForm

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user).order_by('-created_at')

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['whatsapp_form'] = WhatsAppMessageForm()
        return context


class SendWhatsAppMessageView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # This view is primarily for POST, but a GET might redirect or show an error.
        # For now, redirecting to detail view is fine if accessed via GET.
        return redirect('clients:client_detail', pk=pk)

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, owner=request.user)
        form = WhatsAppMessageForm(request.POST)

        if form.is_valid():
            message_content = form.cleaned_data['message']
            
            # TODO: Replace logging with actual WhatsApp API call (e.g., Twilio)
            # from twilio.rest import Client
            # account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
            # auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
            # client_twilio = Client(account_sid, auth_token) # Renamed to avoid conflict
            # message_twilio = client_twilio.messages.create( # Renamed to avoid conflict
            #     from_='whatsapp:YOUR_TWILIO_WHATSAPP_NUMBER',
            #     body=message_content,
            #     to=f'whatsapp:{client.phone_number}'
            # )
            # print(f"Twilio Message SID: {message_twilio.sid}") # Renamed to avoid conflict

            print(f"SIMULATING SENDING WHATSAPP to {client.phone_number}: {message_content}")
            messages.success(request, f"Simulated WhatsApp message sent to {client.name}: '{message_content[:50]}...'")
        else:
            # Handle invalid form
            for error_field, error_messages in form.errors.items():
                for error_message in error_messages:
                    messages.error(request, f"Error in '{form.fields[error_field].label}': {error_message}")

        return redirect('clients:client_detail', pk=pk)

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['name', 'phone_number', 'email', 'status', 'notes']
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['name', 'phone_number', 'email', 'status', 'notes']
    success_url = reverse_lazy('clients:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')
    context_object_name = 'client'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)
