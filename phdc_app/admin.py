from django.contrib import admin
from .models import *


class StudentAdmin(admin.ModelAdmin):
	list_display = ['fullname', 'phone', 'email']
	search_fields = ['lastname', 'firstname', 'middlename', 'phone', 'email']
	list_per_page = 10

	def get_fields(self, request, obj = None):
		fields = super().get_fields(request, obj)
		if obj:
			fields.remove('lastname')
			fields.remove('firstname')
			fields.remove('middlename')
		return fields

admin.site.register(Teacher)
admin.site.register(StudyGroup)
admin.site.register(PostgraduateStudent, StudentAdmin)
admin.site.register(ResearchIndPlan)
admin.site.register(EducIndPlan)
admin.site.register(Dissertation)
admin.site.register(Reviewers)
admin.site.register(DissertationState)
admin.site.register(Department)
admin.site.register(Specialty)
admin.site.register(Edition)
admin.site.register(EditionSpecialties)
admin.site.register(PublicationTypes)
admin.site.register(Publication)
admin.site.register(Authors)
admin.site.register(Seminar)
admin.site.register(SeminarSubscription)
admin.site.register(Protocol)
admin.site.register(Deadline)
admin.site.register(DeadlineSubmission)
admin.site.register(BlackList)
admin.site.register(NotificationAdmin)
admin.site.register(Notifications)
admin.site.register(NotificationStudent)
admin.site.register(Email)
admin.site.register(Report)
admin.site.register(RegistrationStatus)
