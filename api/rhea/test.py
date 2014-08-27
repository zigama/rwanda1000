from rapidsmsrw1000.apps.api.rhea.hl7toxml import *
cmd = RheaNotification()
b = Report.objects.filter(type__name = 'Birth')[200]
r = Report.objects.filter(type__name = 'Risk')[200]
d = Report.objects.filter(type__name = 'Death')[200]

from rapidsmsrw1000.apps.api.rhea.hl7toxml import *
birth = Report.objects.filter(type__name = 'Birth').order_by('-id')
risk = Report.objects.filter(type__name = 'Risk').order_by('-id')
death = Report.objects.filter(type__name = 'Death').order_by('-id')
birth = Report.objects.filter(type__name = 'Birth').order_by('-id')[0:100]
risk = Report.objects.filter(type__name = 'Risk').order_by('-id')[0:100]
death = Report.objects.filter(type__name = 'Death').order_by('-id')[0:100]
cmd = RheaNotification()

def get_notif(report = birth[0], cmd = cmd):
 if report.type.name in ['Birth', 'Risk', 'Death']:
  notif, created = Notification.objects.get_or_create(not_type = NotificationType.objects.get(name = report.type.name), report = report)
  notif.save()
  return notif

def send(r):
 notif = get_notif(report = r)
 notif = cmd.createOutgoingNotification(r)
 response = cmd.sendNotification(notif)
 return response

print "TEST BIRTH:\n"
broot = cmd.createXMLRoot()
cmd.createMSH(broot, b)
cmd.createPatientResult(broot, b)
boutput_xml = cmd.prettify(broot)
f = open("birth.xml" , 'w')
f.write( boutput_xml )
f.close()

print "TEST RISK:\n"
rroot = cmd.createXMLRoot()
cmd.createMSH(rroot, r)
cmd.createPatientResult(rroot, r)
routput_xml = cmd.prettify(rroot)
f = open("risk.xml" , 'w')
f.write( routput_xml )
f.close()

print "TEST DEATH:\n"
droot = cmd.createXMLRoot()
cmd.createMSH(droot,d)
cmd.createPatientResult(droot, d)
doutput_xml = cmd.prettify(droot)
f = open("death.xml" , 'w')
f.write( doutput_xml )
f.close()

