from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.ClientListView.as_view(), name='client_list'),
    path('<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('add/', views.ClientCreateView.as_view(), name='client_add'),
    path('<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('<int:pk>/send_whatsapp/', views.SendWhatsAppMessageView.as_view(), name='send_whatsapp_message'),
]
