from django.db import models
from rapidsmsrw1000.apps.ubuzima.models import *
from django.db.models.signals import post_save, pre_save
import urllib2

# Create your Django models here, if you need them.

class NotificationType(models.Model):

	name = models.CharField(max_length=30, unique=True)
    
	def __unicode__(self):
		return self.name 
	class Meta:

		# define a permission for this app to use the @permission_required
		# in the admin's auth section, we have a group called 'manager' whose
		# users have this permission -- and are able to see this section
		permissions = (
		    ("can_view", "Can view"),
		)

class Concept(models.Model):
	name = models.CharField(max_length=30, blank=True)
	answer = models.CharField(max_length=30, blank=True)
	mapping = models.CharField(max_length=30, default = "RSMS", blank=True)
	mapping_code = models.CharField(max_length=30, blank=True)
	data_type = models.CharField(max_length=30, blank=True)
	value = models.CharField(max_length=30, default = "N/A", blank=True)
	
	class Meta:

		# define a permission for this app to use the @permission_required
		# in the admin's auth section, we have a group called 'manager' whose
		# users have this permission -- and are able to see this section
		permissions = (
		    ("can_view", "Can view"),
		)
		

	
	def __unicode__(self):
		return "%s" % (self.name +"  "+ self.answer)

class Notification(models.Model):
	
	not_type = models.ForeignKey(NotificationType)
	message = models.TextField()
	report = models.ForeignKey(Report)
	created = models.DateTimeField(auto_now_add=True)
	class Meta:

		# define a permission for this app to use the @permission_required
		# in the admin's auth section, we have a group called 'manager' whose
		# users have this permission -- and are able to see this section
		permissions = (
		    ("can_view", "Can view"),
		)
		
		unique_together = ('report', 'not_type',)

	
	def __unicode__(self):
		return self.message

class RheaRequest(models.Model):
	request = models.TextField()
	data = models.TextField()
	notification = models.ForeignKey(Notification, unique = True)
	notif_status = models.BooleanField(default=False)
	response = models.TextField()
	status_reason = models.CharField(max_length=30)

	
	def __unicode__(self):
		return self.notif_status

class HIERequest(models.Model):
	request = models.TextField()
	data = models.TextField()
	concepts = models.TextField()
	patient_reporter = models.CharField(max_length=50)
	message = models.TextField()
	sent = models.BooleanField(default=False)
	response = models.TextField()
	

	def summary(self):
		try:	reporter = Reporter.objects.get(national_id = self.patient_reporter.split('_')[1]).connection().identity
		except:	reporter = None
		try:	patient = Patient.objects.get(national_id = self.patient_reporter.split('_')[0]).national_id
		except:	patient = None
		try:
			concepts = Concept.objects.filter( mapping_code__in = [s.strip().replace("'", "") \
						for s in self.concepts.encode('ASCII').replace('[','').replace(']','').split(',')]).exclude(answer = "")
			concepts = " ".join(c.answer for c in concepts)
		except:	concepts = None
		msg = "Reporter = %s, Patient = %s, Observation: %s" % (reporter, patient, concepts)
		return msg

	
	def __unicode__(self):
		return self.summary()
	
def notify_rhea(sender, **kwargs):

	if kwargs.get('created', False):
		try:
			from rapidsmsrw1000.apps.api.rhea.hl7toxml import RheaNotification
			import time
			report = kwargs['instance']
			if report.type.name in ['Birth', 'Risk', 'Death']:
				notif = Notification(not_type = NotificationType.objects.get(name = report.type.name), report = report)
				notif.save()
			else:
				pass		
			
		except Exception,e:
			print "ERROR: %s" % e
			pass


post_save.connect(notify_rhea, sender = Report)
	
