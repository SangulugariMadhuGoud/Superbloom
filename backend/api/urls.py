from django.urls import path
from .views import health, ContactView, WorkshopsView, WorkshopDetailView, WorkshopRegisterView

urlpatterns = [
	path('health', health, name='health'),
	path('contact', ContactView.as_view(), name='contact'),
	path('workshops', WorkshopsView.as_view(), name='workshops_list'),
	path('workshops/<int:workshop_id>', WorkshopDetailView.as_view(), name='workshops_detail'),
	path('workshops/<int:workshop_id>/register', WorkshopRegisterView.as_view(), name='workshops_register'),
]
