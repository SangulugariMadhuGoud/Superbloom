from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import ContactSubmission, Workshop, WorkshopRegistration


def health(request):
    return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, name="dispatch")
class ContactView(View):
	def post(self, request):
		try:
			data = json.loads(request.body.decode("utf-8"))
			name = data.get("name", "").strip()
			email = data.get("email", "").strip()
			service = data.get("service", "").strip()
			message = data.get("message", "").strip()
			if not name or not email or not message:
				return JsonResponse({"error": "Missing required fields"}, status=400)
			sub = ContactSubmission.objects.create(
				name=name, email=email, service=service, message=message
			)
			return JsonResponse({"id": sub.id, "created_at": sub.created_at.isoformat()})
		except json.JSONDecodeError:
			return JsonResponse({"error": "Invalid JSON"}, status=400)


class WorkshopsView(View):
	def get(self, request):
		items = []
		for ws in Workshop.objects.order_by('-date').all():
			items.append({
				'id': ws.id,
				'title': ws.title,
				'description': ws.description,
				'date': ws.date,
				'start_time': ws.start_time,
				'end_time': ws.end_time,
				'venue': ws.venue,
				'perks': ws.perks,
				'capacity': ws.capacity,
				'image_url': request.build_absolute_uri(ws.image.url) if getattr(ws, 'image', None) and ws.image else '',
				'status': ws.status,
				'upi_id': ws.upi_id,
				'bank_name': ws.bank_name,
				'account_no': ws.account_no,
				'amount': str(ws.amount),
				'payment_qr': request.build_absolute_uri(ws.payment_qr.url) if ws.payment_qr else '',
				'registrations_count': ws.registrations.count(),
				'is_sold_out': ws.is_sold_out,
			})
		return JsonResponse({'items': items})


class WorkshopDetailView(View):
	def get(self, request, workshop_id: int):
		try:
			ws = Workshop.objects.get(id=workshop_id)
		except Workshop.DoesNotExist:
			return JsonResponse({"error": "Not found"}, status=404)
		data = {
			'id': ws.id,
			'title': ws.title,
			'description': ws.description,
			'date': ws.date,
			'start_time': ws.start_time,
			'end_time': ws.end_time,
			'venue': ws.venue,
			'perks': ws.perks,
			'capacity': ws.capacity,
			'image_url': request.build_absolute_uri(ws.image.url) if getattr(ws, 'image', None) and ws.image else '',
			'status': ws.status,
			'upi_id': ws.upi_id,
			'bank_name': ws.bank_name,
			'account_no': ws.account_no,
			'amount': str(ws.amount),
			'payment_qr': request.build_absolute_uri(ws.payment_qr.url) if ws.payment_qr else '',
			'registrations_count': ws.registrations.count(),
			'is_sold_out': ws.is_sold_out,
		}
		return JsonResponse(data)


@method_decorator(csrf_exempt, name="dispatch")
class WorkshopRegisterView(View):
	def post(self, request, workshop_id: int):
		try:
			ws = Workshop.objects.get(id=workshop_id)
		except Workshop.DoesNotExist:
			return JsonResponse({"error": "Not found"}, status=404)
		try:
			if request.content_type and request.content_type.startswith('application/json'):
				data = json.loads(request.body.decode('utf-8'))
			else:
				data = request.POST
			name = (data.get('name') or '').strip()
			email = (data.get('email') or '').strip()
			whatsapp = (data.get('whatsapp') or '').strip()
			organization = (data.get('organization') or '').strip()
			if not name or not email:
				return JsonResponse({"error": "Missing required fields"}, status=400)
			if ws.is_sold_out:
				return JsonResponse({"error": "Sold out"}, status=400)
			reg, created = WorkshopRegistration.objects.get_or_create(
				workshop=ws, email=email,
				defaults={'name': name, 'whatsapp': whatsapp, 'organization': organization}
			)
			# If multipart with file
			if getattr(request, 'FILES', None):
				file_obj = request.FILES.get('payment_proof')
				if file_obj:
					reg.payment_proof = file_obj
					reg.save()
			return JsonResponse({"id": reg.id, "created": created, "registrations_count": ws.registrations.count()})
		except json.JSONDecodeError:
			return JsonResponse({"error": "Invalid JSON"}, status=400)
