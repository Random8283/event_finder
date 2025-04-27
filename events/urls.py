from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('<int:pk>/register/', views.EventRegistrationView.as_view(), name='event_register'),
    path('<int:pk>/deregister/', views.EventDeregisterView.as_view(), name='event_deregister'),
    path('registrations/<int:pk>/update/', views.RegistrationUpdateView.as_view(), name='registration_update'),
    path('registrations/<int:pk>/delete/', views.RegistrationDeleteView.as_view(), name='registration_delete'),
    path('my-events/', views.UserEventListView.as_view(), name='user_events'),
    path('registrations/', views.UserRegistrationListView.as_view(), name='user_registrations'),
] 