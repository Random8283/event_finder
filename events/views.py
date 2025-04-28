from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.db.models import Q
from .models import Event, Registration
from .forms import EventForm, RegistrationForm, UserSignupForm

# Create your views here.

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    ordering = ['-date']
    paginate_by = 10

    def get_template_names(self):
        if self.request.user.is_staff:
            return ['events/admin/event_list.html']
        return ['events/user/event_list.html']

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset

class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    def get_template_names(self):
        if self.request.user.is_staff:
            return ['events/admin/event_detail.html']
        return ['events/user/event_detail.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_registered'] = Registration.objects.filter(
                event=self.object,
                user=self.request.user
            ).exists()
        context['is_past_event'] = self.object.is_past_event
        return context

class EventCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

class EventDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Event deleted successfully.')
        return HttpResponseRedirect(success_url)

class EventRegistrationView(LoginRequiredMixin, CreateView):
    model = Registration
    form_class = RegistrationForm
    template_name = 'events/registration_form.html'

    def get_success_url(self):
        event_id = self.kwargs.get('pk')
        if event_id:
            return reverse_lazy('events:event_detail', kwargs={'pk': event_id})
        return reverse_lazy('events:event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('pk')
        if event_id:
            context['event'] = get_object_or_404(Event, pk=event_id)
        return context

    def form_valid(self, form):
        event_id = self.kwargs.get('pk')
        if not event_id:
            messages.error(self.request, 'Invalid event.')
            return redirect('events:event_list')
            
        event = get_object_or_404(Event, pk=event_id)
        if event.is_past_event:
            messages.error(self.request, 'Cannot register for past events.')
            return redirect('events:event_detail', pk=event.pk)
        
        if Registration.objects.filter(event=event, user=self.request.user).exists():
            messages.error(self.request, 'You are already registered for this event.')
            return redirect('events:event_detail', pk=event.pk)

        form.instance.event = event
        form.instance.user = self.request.user
        form.instance.status = 'confirmed'  # Automatically confirm the registration
        messages.success(self.request, 'Successfully registered for the event!')
        return super().form_valid(form)

class UserEventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/user_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user).order_by('-date')

class UserRegistrationListView(LoginRequiredMixin, ListView):
    model = Registration
    template_name = 'events/user_registrations.html'
    context_object_name = 'registrations'

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user).order_by('-registration_date')

class SignupView(CreateView):
    form_class = UserSignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully. Please log in.')
        return response

class RegistrationUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Registration
    fields = ['status']
    template_name = 'events/registration_update.html'
    
    def get_success_url(self):
        return reverse_lazy('events:event_detail', kwargs={'pk': self.object.event.pk})

class RegistrationDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Registration
    template_name = 'events/registration_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        event_pk = self.object.event.pk
        self.object.delete()
        messages.success(request, 'Registration deleted successfully.')
        return HttpResponseRedirect(reverse_lazy('events:event_detail', kwargs={'pk': event_pk}))

class EventDeregisterView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        registration = Registration.objects.filter(event=event, user=request.user).first()
        
        if registration:
            registration.delete()
            messages.success(request, 'You have been successfully deregistered from the event.')
        else:
            messages.error(request, 'You are not registered for this event.')
        
        return redirect('events:event_detail', pk=pk)

def event_list(request):
    events = Event.objects.all()

    # Get the search query
    search_query = request.GET.get('search')
    print(f"Search Query: {search_query}")  # Debugging output

    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
        print(f"Filtered Events: {events}")  # Debugging output

    return render(request, 'events/event_list.html', {
        'events': events,
        'campus_choices': Event.CAMPUS_CHOICES,
        'category_choices': Event.EVENT_TYPES,
    })
