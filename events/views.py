from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.db.models import Q
from .models import Event, Registration
from .forms import EventForm, RegistrationForm, UserSignupForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone

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
        return ['events/event_list.html']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters
        search_query = self.request.GET.get('search')
        campus = self.request.GET.get('campus')
        category = self.request.GET.get('category')
        date_range = self.request.GET.get('date_range')

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Apply campus filter
        if campus:
            queryset = queryset.filter(campus=campus)

        # Apply category filter
        if category:
            queryset = queryset.filter(category=category)

        # Apply date range filter
        today = timezone.now().date()
        if date_range:
            if date_range == 'today':
                queryset = queryset.filter(date=today)
            elif date_range == 'week':
                start_of_week = today - timezone.timedelta(days=today.weekday())
                end_of_week = start_of_week + timezone.timedelta(days=6)
                queryset = queryset.filter(date__range=[start_of_week, end_of_week])
            elif date_range == 'month':
                start_of_month = today.replace(day=1)
                if today.month == 12:
                    end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timezone.timedelta(days=1)
                else:
                    end_of_month = today.replace(month=today.month + 1, day=1) - timezone.timedelta(days=1)
                queryset = queryset.filter(date__range=[start_of_month, end_of_month])
            elif date_range == 'upcoming':
                queryset = queryset.filter(date__gte=today)
            elif date_range == 'past':
                queryset = queryset.filter(date__lt=today)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campus_choices'] = Event.CAMPUS_CHOICES
        context['category_choices'] = Event.EVENT_TYPES
        
        # Get current filter parameters
        context['filter_params'] = {
            'search': self.request.GET.get('search', ''),
            'campus': self.request.GET.get('campus', ''),
            'category': self.request.GET.get('category', ''),
            'date_range': self.request.GET.get('date_range', '')
        }
        
        return context

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

    # Get the search query and filters
    search_query = request.GET.get('search')
    campus = request.GET.get('campus')
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Apply search filter
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Apply campus filter
    if campus:
        events = events.filter(campus=campus)

    # Apply category filter
    if category:
        events = events.filter(category=category)

    # Apply date range filter
    if start_date:
        events = events.filter(date__gte=start_date)
    if end_date:
        events = events.filter(date__lte=end_date)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(events, 10)  # Show 10 events per page
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    # Get filter parameters for pagination
    filter_params = {
        'search': search_query,
        'campus': campus,
        'category': category,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'events/event_list.html', {
        'events': events,
        'campus_choices': Event.CAMPUS_CHOICES,
        'category_choices': Event.EVENT_TYPES,
        'filter_params': filter_params,
        'is_paginated': paginator.num_pages > 1,
    })
