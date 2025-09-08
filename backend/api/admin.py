from django.contrib import admin
from .models import ContactSubmission, Workshop, WorkshopRegistration
from django.utils.html import format_html
from django.conf import settings
from django.contrib import messages
from django.urls import path
from django.template.response import TemplateResponse


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "service", "created_at")
	search_fields = ("name", "email", "service")
	list_filter = ("service", "created_at")


class WorkshopRegistrationInline(admin.TabularInline):
	model = WorkshopRegistration
	extra = 0
	readonly_fields = ("created_at", "proof_preview")
	fields = ("name", "email", "whatsapp", "organization", "payment_proof", "proof_preview", "status", "admin_notes", "created_at")

	def proof_preview(self, obj):
		if obj.payment_proof:
			return format_html('<img src="{}" style="max-height:100px;" />', obj.payment_proof.url)
		return ""


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
	list_display = ("title", "status", "date", "venue", "capacity", "registrations_count")
	search_fields = ("title", "venue")
	list_filter = ("status", "date", "venue")
	fields = ("title", "status", "description", "date", "start_time", "end_time", "venue", "perks", "capacity", "image", "payment_qr", "upi_id", "bank_name", "account_no", "amount")
	inlines = [WorkshopRegistrationInline]
	actions = ("export_workshop_registrations_csv", "export_workshop_registrations_xlsx", "export_workshop_registrations_to_google_sheets")

	def get_urls(self):
		urls = super().get_urls()
		custom = [
			path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='workshop-dashboard'),
		]
		return custom + urls

	def dashboard_view(self, request):
		from django.db.models import Count
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
		context = dict(
			self.admin_site.each_context(request),
			title="Workshops Dashboard",
			stats=stats,
			by_workshop=list(by_workshop),
		)
		return TemplateResponse(request, 'admin/dashboard.html', context)

	def _serialize_workshop_regs(self, queryset):
		regs = WorkshopRegistration.objects.select_related('workshop').filter(workshop__in=queryset)
		rows = []
		for r in regs:
			rows.append({
				"Workshop": r.workshop.title,
				"Name": r.name,
				"Email": r.email,
				"WhatsApp": r.whatsapp,
				"Organization": r.organization,
				"Status": r.status,
				"Admin Notes": r.admin_notes or '',
				"Created At": r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			})
		return rows

	@admin.action(description="Download registrations (CSV)")
	def export_workshop_registrations_csv(self, request, queryset):
		import csv
		from django.http import HttpResponse
		rows = self._serialize_workshop_regs(queryset)
		header = list(rows[0].keys()) if rows else ["Workshop","Name","Email","WhatsApp","Organization","Status","Admin Notes","Created At"]
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="workshop_registrations.csv"'
		writer = csv.DictWriter(response, fieldnames=header)
		writer.writeheader()
		for row in rows:
			writer.writerow(row)
		return response

	@admin.action(description="Download registrations (XLSX)")
	def export_workshop_registrations_xlsx(self, request, queryset):
		try:
			from openpyxl import Workbook
		except Exception:
			self.message_user(request, "openpyxl not installed. Run: backend/.venv/Scripts/pip install openpyxl", level=messages.ERROR)
			return
		from django.http import HttpResponse
		rows = self._serialize_workshop_regs(queryset)
		header = list(rows[0].keys()) if rows else ["Workshop","Name","Email","WhatsApp","Organization","Status","Admin Notes","Created At"]
		wb = Workbook()
		ws = wb.active
		ws.title = 'Registrations'
		ws.append(header)
		for row in rows:
			ws.append([row[h] for h in header])
		response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = 'attachment; filename="workshop_registrations.xlsx"'
		wb.save(response)
		return response

	@admin.action(description="Export registrations to Google Sheets")
	def export_workshop_registrations_to_google_sheets(self, request, queryset):
		try:
			import gspread  # type: ignore
			from google.oauth2.service_account import Credentials  # type: ignore
		except Exception:
			self.message_user(request, "gspread/google-auth not installed. Run: backend/.venv/Scripts/pip install gspread google-auth", level=messages.ERROR)
			return
		creds_path = getattr(settings, 'GOOGLE_SHEETS_CREDENTIALS_FILE', None)
		spreadsheet_id = getattr(settings, 'GOOGLE_SHEETS_SPREADSHEET_ID', None)
		if not creds_path or not spreadsheet_id:
			self.message_user(request, "Google Sheets credentials or Spreadsheet ID not configured in settings.", level=messages.ERROR)
			return
		scope = [
			'https://www.googleapis.com/auth/spreadsheets',
			'https://www.googleapis.com/auth/drive',
		]
		credentials = Credentials.from_service_account_file(str(creds_path), scopes=scope)
		client = gspread.authorize(credentials)
		sh = client.open_by_key(spreadsheet_id)
		try:
			worksheet = sh.worksheet('Registrations')
		except gspread.WorksheetNotFound:
			worksheet = sh.add_worksheet(title='Registrations', rows=1000, cols=20)
		header = ["Workshop","Name","Email","WhatsApp","Organization","Status","Admin Notes","Created At"]
		existing = worksheet.get_all_values()
		if not existing:
			worksheet.append_row(header)
		rows = self._serialize_workshop_regs(queryset)
		if rows:
			worksheet.append_rows([[r[h] for h in header] for r in rows], value_input_option='USER_ENTERED')
		self.message_user(request, f"Exported {len(rows)} registrations to Google Sheets.")


@admin.register(WorkshopRegistration)
class WorkshopRegistrationAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "workshop", "status", "created_at")
	list_filter = ("status", "workshop", "created_at")
	search_fields = ("name", "email", "workshop__title")
	readonly_fields = ("created_at", "proof_preview")
	fields = ("workshop", "name", "email", "whatsapp", "organization", "payment_proof", "proof_preview", "status", "admin_notes", "created_at")

	actions = ("mark_verified", "mark_rejected", "export_to_google_sheets", "download_csv", "download_xlsx")

	def _serialize_queryset(self, queryset):
		rows = []
		for r in queryset.select_related('workshop'):
			rows.append({
				"Workshop": r.workshop.title,
				"Name": r.name,
				"Email": r.email,
				"WhatsApp": r.whatsapp,
				"Organization": r.organization,
				"Status": r.status,
				"Admin Notes": r.admin_notes or '',
				"Created At": r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			})
		return rows

	def proof_preview(self, obj):
		if obj.payment_proof:
			return format_html('<img src="{}" style="max-height:150px;" />', obj.payment_proof.url)
		return ""

	@admin.action(description="Mark as Payment Verified")
	def mark_verified(self, request, queryset):
		updated = queryset.update(status="verified")
		self.message_user(request, f"Marked {updated} registrations as verified.")

	@admin.action(description="Mark as Rejected")
	def mark_rejected(self, request, queryset):
		updated = queryset.update(status="rejected")
		self.message_user(request, f"Marked {updated} registrations as rejected.")

	@admin.action(description="Export selected to Google Sheets")
	def export_to_google_sheets(self, request, queryset):
		try:
			import gspread  # type: ignore
			from google.oauth2.service_account import Credentials  # type: ignore
		except Exception:
			self.message_user(request, "gspread/google-auth not installed. Run: backend/.venv/Scripts/pip install gspread google-auth", level=messages.ERROR)
			return
		creds_path = getattr(settings, 'GOOGLE_SHEETS_CREDENTIALS_FILE', None)
		spreadsheet_id = getattr(settings, 'GOOGLE_SHEETS_SPREADSHEET_ID', None)
		if not creds_path or not spreadsheet_id:
			self.message_user(request, "Google Sheets credentials or Spreadsheet ID not configured in settings.", level=messages.ERROR)
			return
		scope = [
			'https://www.googleapis.com/auth/spreadsheets',
			'https://www.googleapis.com/auth/drive',
		]
		credentials = Credentials.from_service_account_file(str(creds_path), scopes=scope)
		client = gspread.authorize(credentials)
		sh = client.open_by_key(spreadsheet_id)
		try:
			worksheet = sh.worksheet('Registrations')
		except gspread.WorksheetNotFound:
			worksheet = sh.add_worksheet(title='Registrations', rows=1000, cols=20)
		# Header
		header = [
			"Workshop",
			"Name",
			"Email",
			"WhatsApp",
			"Organization",
			"Status",
			"Admin Notes",
			"Created At",
		]
		existing = worksheet.get_all_values()
		if not existing:
			worksheet.append_row(header)
		rows = []
		for r in queryset.select_related('workshop'):
			rows.append([
				r.workshop.title,
				r.name,
				r.email,
				r.whatsapp,
				r.organization,
				r.status,
				r.admin_notes or '',
				r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			])
		if rows:
			worksheet.append_rows(rows, value_input_option='USER_ENTERED')
		self.message_user(request, f"Exported {len(rows)} registrations to Google Sheets.")

	@admin.action(description="Download selected as CSV")
	def download_csv(self, request, queryset):
		import csv
		from django.http import HttpResponse
		rows = self._serialize_queryset(queryset)
		header = list(rows[0].keys()) if rows else ["Workshop","Name","Email","WhatsApp","Organization","Status","Admin Notes","Created At"]
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="registrations.csv"'
		writer = csv.DictWriter(response, fieldnames=header)
		writer.writeheader()
		for row in rows:
			writer.writerow(row)
		return response

	@admin.action(description="Download selected as XLSX")
	def download_xlsx(self, request, queryset):
		try:
			from openpyxl import Workbook
		except Exception:
			self.message_user(request, "openpyxl not installed. Run: backend/.venv/Scripts/pip install openpyxl", level=messages.ERROR)
			return
		from django.http import HttpResponse
		rows = self._serialize_queryset(queryset)
		header = list(rows[0].keys()) if rows else ["Workshop","Name","Email","WhatsApp","Organization","Status","Admin Notes","Created At"]
		wb = Workbook()
		ws = wb.active
		ws.title = 'Registrations'
		ws.append(header)
		for row in rows:
			ws.append([row[h] for h in header])
		response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = 'attachment; filename="registrations.xlsx"'
		wb.save(response)
		return response
