from django.db import models

# Create your models here.


class ContactSubmission(models.Model):
	name = models.CharField(max_length=200)
	email = models.EmailField()
	service = models.CharField(max_length=100, blank=True)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.name} <{self.email}> @ {self.created_at:%Y-%m-%d %H:%M}"


class Workshop(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	venue = models.CharField(max_length=200)
	perks = models.TextField(blank=True)
	capacity = models.PositiveIntegerField(default=30)
	image = models.ImageField(upload_to='workshops/images/', blank=True, null=True)
	status = models.CharField(max_length=16, choices=(("active", "Active"), ("inactive", "Inactive")), default="active")
	payment_qr = models.ImageField(upload_to='workshops/qr/', blank=True, null=True)
	upi_id = models.CharField(max_length=128, blank=True)
	bank_name = models.CharField(max_length=128, blank=True)
	account_no = models.CharField(max_length=64, blank=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return self.title

	@property
	def registrations_count(self) -> int:
		return self.registrations.count()

	@property
	def is_sold_out(self) -> bool:
		return self.registrations_count >= self.capacity


class WorkshopRegistration(models.Model):
	workshop = models.ForeignKey(Workshop, related_name='registrations', on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	email = models.EmailField()
	whatsapp = models.CharField(max_length=30, blank=True)
	organization = models.CharField(max_length=200, blank=True)
	payment_proof = models.ImageField(upload_to='workshops/proofs/', blank=True, null=True)
	status = models.CharField(
		max_length=20,
		choices=(
			("pending", "Pending"),
			("verified", "Payment Verified"),
			("rejected", "Rejected"),
		),
		default="pending",
	)
	admin_notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("workshop", "email")

	def __str__(self) -> str:
		return f"{self.name} - {self.workshop.title}"