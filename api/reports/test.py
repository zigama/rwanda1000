from rapidsmsrw1000.apps.api.reports.models import *
from rapidsmsrw1000.apps.api.locations.models import *
filename = "%s/models.py" % THIS_PATH
sms = SMSReport.objects.all()[0]
sms.keyword
keyword = sms.keyword
fields = SMSReportField.objects.filter(sms_report = sms)
fields
locations = [l.name for l in LocationType.objects.all()]
links = []
start, end, default_return = "", "", "nid"
d = create_or_update_sms_report_model(filename, keyword, fields, locations, links, start, end, default_return)
