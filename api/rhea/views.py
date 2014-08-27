#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

# Create your webui views here.
#from rapidsms.webui.utils import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Count
from rapidsmsrw1000.apps.api.rhea.models import *
from rapidsmsrw1000.apps.utils import *

### START OF HELPERS

def rhea_request_match_filters(req):
    rez = {}
    pst = {}
    prd = {}
    level = get_level(req)
    period = default_period(req)
    try:
        loc = int(req.REQUEST['location'])
        rez['notification__report__location'] = loc
    except KeyError:
        try:
            dst=int(req.REQUEST['district'])
            rez['notification__report__district'] = dst
        except KeyError:
            try:
                prv=int(req.REQUEST['province'])
                rez['notification__report__province'] = prv
            except KeyError:    pass

    if level['level'] == 'Nation':  pst['notification__report__nation'] = level['uloc'].nation.id
    elif level['level'] == 'Province':  pst['notification__report__province'] = level['uloc'].province.id
    elif level['level'] == 'District':  pst['notification__report__district'] = level['uloc'].district.id
    elif level['level'] == 'HealthCentre':  pst['notification__report__location'] = level['uloc'].health_centre.id

    prd = {'notification__created__gte' : period['start'], 'notification__created__lte' : period['end'] }

    return [rez,pst, prd]


@permission_required('rhea.can_view')
def paginated(req, data):
    req.base_template = "webapp/layout.html"
    paginator = Paginator(data, 5)

    try: page = int(req.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        data = paginator.page(page)
    except (InvalidPage, EmptyPage):
        data = paginator.page(paginator.num_pages)

    return data

@permission_required('rhea.can_view')
def index(req,**flts):
    req.base_template = "webapp/layout.html"
    
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)} 

    match = rhea_request_match_filters(req)
    #print match
    notifications = RheaRequest.objects.filter( **match[2]).filter(**match[1]).filter(**match[0])
    #print notifications.count()
        
    notifications_by_district = notifications.values('notification__report__district__name',).annotate(total = Count('id')).order_by('notification__report__district__name')
    dst_data = []; nbr = 0
    for n in notifications_by_district:

        d = n
        nbr += 1
        d['id'] = nbr

        d['birth'] = notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Birth').count()
        d['death'] =  notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Death').count()
        d['risk'] =  notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Risk').count()

        d['birth_passed'] = notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Birth', notif_status = True).count()
        d['death_passed'] =  notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Death', notif_status = True).count()
        d['risk_passed'] =  notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Risk', notif_status = True).count()

        d['birth_failed'] = notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Birth', notif_status = False).count()
        d['death_failed'] =  notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Death', notif_status = False).count()
        d['risk_failed'] =  notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notification__not_type__name = 'Risk', notif_status = False).count()

        d['failed'] =  notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notif_status = False).count()
        d['passed'] =  notifications.filter( notification__report__district__name = n ['notification__report__district__name'], notif_status = True).count() 

        dst_data.append(d) 
        
    #print dst_data    
    
    lox, lxn = 0, location_name(req)
    if req.REQUEST.has_key('location') and req.REQUEST['location'] != '0':
        lox = int(req.REQUEST['location'])
        lxn = HealthCentre.objects.get(id = lox)
        lxn=lxn.name+' '+"Health Centre"+', '+lxn.district.name+' '+"District"+', '+lxn.province.name+' '

    if req.REQUEST.has_key('excel'):
        return reports_to_excel(reports.order_by("-id"))
    else:

        # TODO start date and end date
        
        return render_to_response("rhea/index.html", {'notifications_by_district' : dst_data,"notifications": paginated(req, notifications),'usrloc':UserLocation.objects.get(user=req.user),\
                                                    'start_date': date.strftime(filters['period']['start'], '%d.%m.%Y'),\
                                                    'end_date': date.strftime(filters['period']['end'], '%d.%m.%Y'),\
                                                    'filters':filters,'locationname':lxn,'postqn':(req.get_full_path().split('?', 2) + [''])[1], \
                                    },\
                                 context_instance=RequestContext(req))


