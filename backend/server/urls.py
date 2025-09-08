"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.template.response import TemplateResponse
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.db.models import Count
from api.models import Workshop, WorkshopRegistration


def home(_request):
	return HttpResponse("Backend OK")

def admin_dashboard(request):
	stats = {
		"workshops_total": Workshop.objects.count(),
		"registrations_total": WorkshopRegistration.objects.count(),
		"registrations_verified": WorkshopRegistration.objects.filter(status='verified').count(),
		"registrations_pending": WorkshopRegistration.objects.filter(status='pending').count(),
	}
	by_workshop = (
		Workshop.objects
		.annotate(reg_count=Count('registrations'))
		.values('id','title','status','date','reg_count')
		.order_by('-date')[:20]
	)
	context = admin.site.each_context(request)
	context.update({
		"title": "Workshops Dashboard",
		"stats": stats,
		"by_workshop": list(by_workshop),
	})
	return TemplateResponse(request, 'admin/dashboard.html', context)

urlpatterns = [
	path('', home, name='home'),
	path('admin/dashboard/', admin.site.admin_view(admin_dashboard), name='admin-dashboard'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# Serve media files even in production when MEDIA_ROOT is present.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
