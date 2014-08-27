#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##


from rapidsmsrw1000.apps.api.locations.models import *
s = create_location_type_model("District", 10, 40, ["Nation", "Province"])
