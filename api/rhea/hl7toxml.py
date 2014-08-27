#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


#Author: UWANTWALI ZIGAMA Didier

##This class and method simply produces an XML representation of the same message. Note that this class isn't nearly clever enough to know what type of HL7 message it ##is converting - it merely creates an XML version of it. The point is that you can then use XPath to retrieve the segment you want to use since you know its location. ##

## This class takes an HL7 message
## and transforms it into an XML representation.

from xml.dom.minidom import *
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, XML
from xml.etree import ElementTree
from rapidsmsrw1000.apps.api.rhea.models import *
from rapidsmsrw1000.apps.api.rhea.utils import *
from xlrd import open_workbook ,cellname,XL_CELL_NUMBER,XLRDError
from django.db import connection
from django.core import management



class RheaNotification(object):
    def __init__ (self, *paths):
	    """ Initializing every notification constants that are be sent out of our system """

	    self.field_separator = "|"
	    self.component_separator = "^"
	    self.repetition_separator = "~"
	    self.escape_character = "\\"
	    self.subcomponent_separator = "&"

	    self.encoding_chars = self.component_separator + self.repetition_separator + self.escape_character + self.subcomponent_separator

	    self.sending_application = "RAPIDSMS"
	    self.receiving_application = "SHARED HEALTH RECORD"
	    self.receiving_facility = "RWANDA MOH"
	    self.oru = "ORU"
	    self.r01 = "R01"
	    self.oru_r01 = "ORU_R01"
	    self.processing_id_1 = "D"
	    self.processing_id_2 = "C"
	    self.version_id_1 = "2.5"
	    self.version_id_2 = "RWA"

    def getMessageHeader(self, report):
        headers = {"Birth":"BIR","Risk":"RISK", "Death": "MAT"}

        """ For the old RapidSMS, there were no specific Report for reporting death, that's why this line was there. Now let surround it with comment symbols it 
        as follows: """

        """if report.fields.filter(type__key__in = ['md','nd','cd']).exists():
            return "MAT"
        else:	return headers[report.type.name]"""

        return headers[report.type.name]

    def prettify(self, elem):
	    """Return a pretty-printed XML string for the Element.
	    """
	    rough_string = ElementTree.tostring(elem, 'utf-8')
	    reparsed = parseString(rough_string)
	    #return reparsed.toprettyxml(indent="  ")
	    return reparsed.toxml()

    def createXMLRoot(self):
	    # Configure one attribute with set()
	    root = Element("ORU_R01")
	    root.set("xmlns", "urn:hl7-org:v2xml")
	    return root

    def createMSH(self, root, report):
	    msh = SubElement(root, "MSH") 		#Message Header
	    msh_1 = SubElement(msh, "MSH.1") 	#Field Separator
	    msh_1.text = self.field_separator 	
	    msh_2 = SubElement(msh, "MSH.2")	#Encoding Characters
	    msh_2.text = self.encoding_chars
	    msh_3 = SubElement(msh, "MSH.3")	#Sending Application
	    msh_3_hd_1 = SubElement(msh_3, "HD.1");msh_3_hd_1.text = self.sending_application
	    msh_4 = SubElement(msh, "MSH.4")	#Sending Facility
	    msh_4_hd_1 = SubElement(msh_4, "HD.1");msh_4_hd_1.text = report.location.code
	    msh_5 = SubElement(msh, "MSH.5")	#Receiving Application
	    msh_5_hd_1 = SubElement(msh_5, "HD.1");msh_5_hd_1.text = self.receiving_application
	    msh_6 = SubElement(msh, "MSH.6")	#Receiving Facility
	    msh_5_hd_1 = SubElement(msh_6, "HD.1");msh_5_hd_1.text = self.receiving_facility
	    msh_7 = SubElement(msh, "MSH.7")	#DATE TIME MESSAGE SENT
	    msh_7_ts_1 = SubElement(msh_7, "TS.1");msh_7_ts_1.text = "%04d%02d%02d%02d%02d%02d"%(report.created.year,report.created.month,report.created.day,report.created.hour,report.created.minute,report.created.second)
	    msh_9 = SubElement(msh, "MSH.9")	#Message Type
	    msh_9_msg_1 = SubElement(msh_9, "MSG.1");msh_9_msg_1.text = self.oru
	    msh_9_msg_2 = SubElement(msh_9, "MSG.2");msh_9_msg_2.text = self.r01
	    msh_9_msg_3 = SubElement(msh_9, "MSG.3");msh_9_msg_3.text = self.oru_r01
	    msh_10 = SubElement(msh, "MSH.10")	#Message Control ID (ST)
	    msh_10.text = str(report.id)
	    msh_11 = SubElement(msh, "MSH.11")	#Processing ID
	    msh_11_pt_1 = SubElement(msh_11, "PT.1");msh_11_pt_1.text = self.processing_id_1
	    msh_11_pt_2 = SubElement(msh_11, "PT.2");msh_11_pt_2.text = self.processing_id_2
	    msh_12 = SubElement(msh, "MSH.12")	#Version ID
	    msh_12_vid_1 = SubElement(msh_12, "VID.1");msh_12_vid_1.text = self.version_id_1
	    msh_12_vid_2 = SubElement(msh_12, "VID.2")
	    msh_12_vid_2_ce_1 = SubElement(msh_12_vid_2, "CE.1");msh_12_vid_2_ce_1.text = self.version_id_2
	    msh_21 = SubElement(msh, "MSH.21")	#Message Profile Identifier
	    msh_21_ei_1 = SubElement(msh_21, "EI.1");msh_21_ei_1.text = self.getMessageHeader(report)

	
	    return msh

    def createPID(self, root, report):
        pid = SubElement(root, "PID")
        #pid_1 = SubElement(pid, "PID.1");pid_1.text = "1"
        pid_3 = SubElement(pid, "PID.3")
        #pid_5 = SubElement(pid, "PID.5")
        #report.patient.national_id = "123456789"#Remove this line in production and use the real national ID
        pid_3_cx_1 = SubElement(pid_3, "CX.1");pid_3_cx_1.text = report.patient.national_id
        pid_3_cx_5 = SubElement(pid_3, "CX.5");pid_3_cx_5.text = "NID"
        #pid_5_xpn_1 = SubElement(pid_5, "XPN.1")
        #pid_5_xpn_1_fn_1 = SubElement(pid_5_xpn_1, "FN.1");pid_5_xpn_1_fn_1.text = "No Information"
        #pid_5_xpn_2 = SubElement(pid_5, "XPN.2");pid_5_xpn_2.text = "No Information"
        if self.getMessageHeader(report) == "MAT":
            pid_29 = SubElement(pid, "PID.29");pid_29.text = "%04d%02d%02d%02d%02d%02d"%\
	            (report.created.year,report.created.month,report.created.day,report.created.hour,report.created.minute,report.created.second)
        return pid

    def createPV1(self, root, report):
        pv1 = SubElement(root, "PV1")
        pv1_2 = SubElement(pv1, "PV1.2");pv1_2.text = "0"
        pv1_4 = SubElement(pv1, "PV1.4");pv1_4.text = self.getMessageHeader(report)
        pv1_7 = SubElement(pv1, "PV1.7")
        #report.reporter.national_id = "3525410" #remember to change this in production
        pv1_7_xcn_1 = SubElement(pv1_7, "XCN.1");pv1_7_xcn_1.text = report.reporter.national_id 
        pv1_7_xcn_13 = SubElement(pv1_7, "XCN.13");pv1_7_xcn_13.text = "NID"
        return pv1

    def createOBR(self,root, report):
        obr = SubElement(root, "OBR")
        obr_1 = SubElement(obr, "OBR.1")
        obr_1.text = "0"
        obr_3 = SubElement(obr, "OBR.3")
        obr_3_ei_1 = SubElement(obr_3, "EI.1")
        obr_3_ei_1.text = "%d" % report.id
        obr_4 = SubElement(obr, "OBR.4")
        obr_4_ce_2 = SubElement(obr_4, "CE.2")
        obr_4_ce_2.text = self.getMessageHeader(report)
        obr_7 = SubElement(obr, "OBR.7")
        obr_7_ts_1 = SubElement(obr_7, "TS.1")
        obr_7_ts_1.text = "%04d%02d%02d%02d%02d%02d"%(report.created.year,report.created.month,report.created.day,
                                                        report.created.hour,report.created.minute,report.created.second)
        if report.type == "Birth":
            rdob = report.date or report.created
            obr_7_ts_1.text = "%04d%02d%02d%02d%02d%02d"%(rdob.year,rdob.month,rdob.day,00,00,00)

        if report.fields.filter(type__key__in = ['cl', 'hd']).exists():
            obr_20 = SubElement(obr, "OBR.20")
            obr_20.text = report.location.code
            obr_21 = SubElement(obr, "OBR.21")
            obr_21.text = report.location.name

        return obr

    def createDOB(self, root, index, report):
        concept = Concept.objects.get( name = "DATE OF BIRTH")
        rdob = report.date if report.date else datetime.date.today()
        dob = "%04d%02d%02d%02d%02d%02d"%(rdob.year,rdob.month,rdob.day,00,00,00)
        dob_obx = SubElement(root, "OBX")
        obx_1 = SubElement(dob_obx, "OBX.1");obx_1.text = str(index)
        obx_2 = SubElement(dob_obx, "OBX.2");obx_2.text = "TS"
        obx_3 = SubElement(dob_obx, "OBX.3")
        obx_3_ce_1 = SubElement(obx_3, "CE.1");obx_3_ce_1.text = concept.mapping_code
        obx_3_ce_2 = SubElement(obx_3, "CE.2");obx_3_ce_2.text = concept.mapping_code + " " + concept.name 
        obx_3_ce_3 = SubElement(obx_3, "CE.3");obx_3_ce_3.text = concept.mapping
        obx_5 = SubElement(dob_obx, "OBX.5")
        obx_3_ts_1 = SubElement(obx_5, "TS.1");obx_3_ts_1.text = dob

        return dob_obx

    def createWeightChildNumber(self, root, index, field):
	    if field.type.key == 'mother_weight':	concept = Concept.objects.get( name = "WEIGHT")
	    elif field.type.key == 'child_weight':	concept = Concept.objects.get( name = "BABY'S WEIGHT")
	    elif field.type.key == 'child_number':	concept = Concept.objects.get( name = "CHILD NUMBER")
	    we_obx = SubElement(root, "OBX")
	    obx_1 = SubElement(we_obx, "OBX.1");obx_1.text = str(index)
	    obx_2 = SubElement(we_obx, "OBX.2");obx_2.text = "NM"
	    obx_3 = SubElement(we_obx, "OBX.3")
	    obx_3_ce_1 = SubElement(obx_3, "CE.1");obx_3_ce_1.text = concept.mapping_code
	    obx_3_ce_2 = SubElement(obx_3, "CE.2");obx_3_ce_2.text = concept.mapping_code + " " + concept.name 
	    obx_3_ce_3 = SubElement(obx_3, "CE.3");obx_3_ce_3.text = concept.mapping
	    obx_5 = SubElement(we_obx, "OBX.5");obx_5.text = str(field.value)
	    obx_6 = SubElement(we_obx, "OBX.6")
	    obx_6_ce_1 = SubElement(obx_6, "CE.1");obx_6_ce_1.text = "Kg" if field.type.key == 'child_weight' else ""
	    obx_6_ce_3 = SubElement(obx_6, "CE.3");obx_6_ce_3.text = "UCUM"

	    return we_obx

    def createRiskLocationSex(self, root, index, field):
	    location = {'ho' : 'AT HOME', 'hp' : 'AT HOSPITAL FACILITY', 'or' : 'ON ROUTE', 'cl' : 'AT CLINIC FACILITY'}
	    sex = {'bo' : 'MALE', 'gi' : 'FEMALE'}
	    death = {'sb' : 'STILL BORN', 'nd' : 'NEWBORN DEATH', 'cd': 'CHILD DEATH' , 'md': 'MATERNAL DEATH'}
	    p, concept = None, None
	    #print field
	    if field.type.category.name == 'Risk Codes':###Make like this in old RapidSMS###if field.type.category.name == 'Risk':
		    try:
			    p = Concept.objects.get( name = "RISK", answer = "")
			    concept = Concept.objects.get( name = "RISK", mapping_code = field.type.key)
		    except:	pass
	    elif field.type.key in  ['bo', 'gi']:
		    try:
			    p = Concept.objects.get( name = "SEX", answer = "")
			    concept = Concept.objects.get( name = "SEX", answer = sex[field.type.key])
		    except:	pass
	    elif field.type.key in  location.keys():
		    try:
			    p = Concept.objects.get( name = "LOCATION", answer = "")
			    concept = Concept.objects.get( name = "LOCATION", answer = location[field.type.key])
		    except:	pass
	    elif field.type.category.name == 'Death Codes':###Make like this in old RapidSMS###elif field.type.category.name == 'Death':
		    try:
			    p = Concept.objects.get( name = "MATERNAL DEATH CODE", answer = "")
			    concept = Concept.objects.get( name = "MATERNAL DEATH CODE", answer = death[field.type.key])
		    except:	pass
	    if p and concept:
		    obx = SubElement(root, "OBX")
		    obx_1 = SubElement(obx, "OBX.1");obx_1.text = str(index)
		    obx_2 = SubElement(obx, "OBX.2");obx_2.text = "CE"#"NM"
		    obx_3 = SubElement(obx, "OBX.3")
		    obx_3_ce_1 = SubElement(obx_3, "CE.1");obx_3_ce_1.text = p.mapping_code
		    obx_3_ce_2 = SubElement(obx_3, "CE.2");obx_3_ce_2.text = p.mapping_code + " " + concept.name 
		    obx_3_ce_3 = SubElement(obx_3, "CE.3");obx_3_ce_3.text = p.mapping
		    obx_5 = SubElement(obx, "OBX.5")
		    obx_5_ce_1 = SubElement(obx_5, "CE.1");obx_5_ce_1.text = concept.mapping_code
		    obx_5_ce_2 = SubElement(obx_5, "CE.2");obx_5_ce_2.text = concept.mapping_code + " " + concept.answer 
		    obx_5_ce_3 = SubElement(obx_5, "CE.3");obx_5_ce_3.text = concept.mapping
		    return obx
	    else:	return
	

    def createOBX(self, root, report):
	
	    fields = [f for f in report.fields.all()]
	    for f in fields:
		     
		    if f.type.key in ['mother_weight', 'child_weight', 'child_number']:	self.createWeightChildNumber(SubElement(root, "ORU_R01.OBSERVATION")\
															    , fields.index(f), f)
		    elif f.type.category.name in ['Risk Codes','Death Codes', 'Location Codes'] or f.type.key in ['bo', 'gi']:	self.createRiskLocationSex(SubElement(root,\
														     "ORU_R01.OBSERVATION"), fields.index(f), f)
	     	
	    if report.type.name == "Birth" :	dob_obx = self.createDOB(SubElement(root, "ORU_R01.OBSERVATION"), len(fields), report)
				     
	    return root

    def createPatientResult(self, root, report):
	    patient_result = SubElement(root, "ORU_R01.PATIENT_RESULT")
	    patient = SubElement(patient_result, "ORU_R01.PATIENT")
	    pid = self.createPID(patient, report)
	    visit = SubElement(patient, "ORU_R01.VISIT")
	    pv1 = self.createPV1(visit, report)
	    order_observation = SubElement(patient_result, "ORU_R01.ORDER_OBSERVATION")
	    obr = self.createOBR(order_observation, report)
	    obxs = self.createOBX(order_observation, report)
	
	    return patient_result


    def createOutgoingNotification(self, report):
        root = self.createXMLRoot()
        self.createMSH(root,report)
        self.createPatientResult(root, report)
        output_xml = self.prettify(root)
        notif = None
        if report.type.name in ['Birth', 'Risk', 'Death'] :
            message = output_xml
            notif = Notification.objects.get(not_type = NotificationType.objects.get(name = report.type.name), report = report)
            notif.message = message
            notif.save() 
        return notif 

    def response_to_xml(self, data):
	    response = Element("error")
	    response_code = SubElement(response, "error_code")
	    response_msg = SubElement(response, "error_msg")
	
	    if data == True:
		    response_code.text = "201"
		    response_msg.text = "CREATED"

	    elif data == False:
		    response_code.text = "400"
		    response_msg.text = "BAD REQUEST"

	    else:
		    response_code.text = "500"
		    response_msg.text = "SERVER ERROR"

	    return self.prettify(response)

    def response_to_json(self, data):
	    response = { 'error' : { 'error_code' : '', 'error_msg' : '' }}
			
	    if data == True:
		    response['error']['error_code'] = "201"
		    response['error']['error_msg'] = "CREATED"

	    if data == False:
		    response['error']['error_code'] = "400"
		    response['error']['error_msg'] = "BAD REQUEST"

	    else:
		    response['error']['error_code'] = "500"
		    response['error']['error_msg'] = "SERVER ERROR"
	
	    return response

    def getPatientResult(self, root):
	
	    try:
		    pid = [ node for node in [ node for node in root.getElementsByTagName('ORU_R01.PATIENT')[0].childNodes if node.nodeName in ['PID']][0]\
				    .childNodes if node.nodeName in ['PID.1','PID.3','PID.29'] ]
		    patient_nid = [ n for n in [ node.childNodes for node in pid if node.nodeName in ['PID.3'] ][0]  if n.nodeName in ['CX.1']][0]\
				    .firstChild.data
		    pv1 = [ n for n in [ node for node in [ node for node in root.getElementsByTagName('ORU_R01.PATIENT')[0].childNodes if node.nodeName in ['ORU_R01.VISIT']][0]\
				    .childNodes if node.nodeName in ['PV1'] ][0].childNodes if n.nodeName in ['PV1.2','PV1.4','PV1.7'] ]

		    reporter_nid = [ n for n in [ node.childNodes for node in pv1 if node.nodeName in ['PV1.7'] ][0]  if n.nodeName in ['XCN.1']][0]\
				    .firstChild.data			
		    #print pid, patient_nid, pv1, reporter_nid

		    return {'patient_nid' : patient_nid, 'reporter_nid': reporter_nid,}
		
	    except:	pass
	    return True

    def getPatientObservation(self, root):

     try:
      nodes = [ node for node in [ node for node in root.getElementsByTagName('ORU_R01.ORDER_OBSERVATION')[0].childNodes]]

      observations = [node for node in nodes if node.nodeName in ['ORU_R01.OBSERVATION']]
      obxs = [ node for node in root.getElementsByTagName('OBX')]
      mapping_codes = []
      for obx in obxs:
       data = [n for n in obx.getElementsByTagName('CE.1')]
       for d in data:
        x = "".join([n.nodeValue for n in d.childNodes]).strip();mapping_codes.append(str(x))
            
      return {'length' : len(obxs), 'obxs': obxs, 'mapping_codes': mapping_codes}

     except Exception, e:	print e;pass
     return True

    def getMSH(self, root):
	
	    try:
		    msh_type = [ node for node in root.getElementsByTagName('MSH.21')[0].childNodes if node.nodeName in ['EI.1']][0].firstChild.data
		    msh_facility = [ node for node in root.getElementsByTagName('MSH.6')[0].childNodes if node.nodeName in ['HD.1']][0].firstChild.data
		    ###you can add more data to return as long as you need them
		    return {'facility' : msh_facility, 'msg_type' : msh_type}
	    except:	pass
	    return False

    def createIncomingNotification(self, request):
        data = parseString(request.raw_post_data)
        if data.documentElement.tagName != 'ORU_R01':
            data = False
        else:
            if data.documentElement.tagName == 'ORU_R01':
                message = data
                nodes = message.getElementsByTagName('ORU_R01')[0].childNodes
                main_nodes  = [ node for node in nodes if node.nodeName in ['MSH', 'ORU_R01.PATIENT_RESULT']  ]

                if len(main_nodes) == 2:
                    try:
                        msh = main_nodes[0]
                        result = main_nodes[1]
                        if msh.tagName == 'MSH' and result.tagName == 'ORU_R01.PATIENT_RESULT':
                            msh = self.getMSH(msh)
                            result = self.getPatientResult(result)
                            msg = None
                            if msh['msg_type'] == "REMINDER" or msh['msg_type'] == "ALERT":
                                msg = {'reporter' : {'nid' : result['reporter_nid']}, 'patient' : {'nid' : result['patient_nid']},\
                                 'facility' : {'code' : msh['facility']}  }

                            sent = send_reminder_message(msg)

                            if sent[0] == True:
                                patient_reporter = "%s_%s" % (result['patient_nid'],result['reporter_nid'])
                                concepts = self.getPatientObservation(main_nodes[1])['mapping_codes']
                                incoming = HIERequest(request = request,data=request.raw_post_data, concepts = concepts, patient_reporter =  patient_reporter,\
                                                        message = sent[1], sent = sent[0], response = self.response_to_xml(sent[0]))
                                incoming.save()			
                                data = True 		     ##Rember to uncomment this line after modem and credit check
                            else:	data = None ##Rember to uncomment this line after modem and credit check
                            
                        else:	data = False
                    except Exception, e:	data = None;print e
                else:	data = False
        response = self.response_to_xml(data)#;print response
        #response = self.response_to_json(data)
        return response


    ####this function send notification the interoperability layer and still wating to get the response.
    def sendNotification(self, notif):
        res = None
        
        try:
            #report.patient.national_id = "123456789"#Remove this line in production
            url = "/ws/rest/v1/patient/NID-%s/encounters?notificationType=%s" % (notif.report.patient.national_id, self.getMessageHeader(notif.report))
            #url = "https://%s:%s%s"%(conf["host"], conf["port"], url)
            data = notif.message
            request = create_rhea_request(url,data)#urllib2.Request(url, notif.message, headers = {'Content-Type': 'application/xml'})

            #base64string = base64.encodestring('%s:%s' % (conf["user"], conf["pass"]))[:-1]
            #request.add_header("Authorization", "Basic %s" % base64string)
            
            res = get_rhea_response(request)
            #print "REQUEST: %s, RESPONSE : %s " % (request, res)
            rr = RheaRequest(request=res['request'] ,data=res['data'], notification=notif, response=res['response'], status_reason=res['status_reason'])
            
            if res['response_code'] == 201:
                rr.notif_status = True
                rr.save()    
            else:
                rr.notif_status = False
                rr.save() #print "Patient: %s, Response Status: %s" % (report.patient, res)
                
        except Exception, e:
            print e
            pass

        return res
		

    def import_concepts(self, filepath = "rapidsmsrw1000/apps/api/rhea/concepts.xls", sheetname = "concepts", startrow = 1, maxrow = 48, namecol = 0, answercol = 1,\
         mappingcol = 2, codecol = 3, datacol = 4, valuecol = 5 ):
        concs = []
        book = open_workbook(filepath)
        sheet = book.sheet_by_name(sheetname)
        table='rhea_concept'
        cursor = connection.cursor()

        try:	
            cursor.execute("drop table %s" % table)
            management.call_command('syncdb')
        except Exception, e:
            print e
            management.call_command('syncdb')
            pass

        cursor.close()

        for row_index in range(sheet.nrows):

            if row_index < startrow: continue

            name = sheet.cell(row_index, namecol).value
            answer = sheet.cell(row_index, answercol).value
            mapping = sheet.cell(row_index, mappingcol).value
            mapping_code = sheet.cell(row_index, codecol).value
            data_type = sheet.cell(row_index, datacol).value
            value = sheet.cell(row_index, valuecol).value

            try:
                self.initialize_notificationtypes()
                concept = Concept( name = name , answer = answer , mapping = mapping , mapping_code = mapping_code, data_type = data_type, value = value)
                concept.save();concs.append(concept)

            except Exception ,e:
                print e		
                continue
        return concs

    def initialize_notificationtypes(self):
        t = ['ANC', 'Birth', 'Community Based Nutrition', 'Community Case Management', 'Child Health', 'Case Management Response', 'Death', 'Newborn Care', \
            'PNC', 'Pregnancy', 'Red Alert Result', 'Red Alert', 'Risk Result', 'Risk', 'Refusal', 'Departure' ]
        try:
            for r in t:
                NotificationType.objects.get_or_create(name = r)
        except: pass
        return True




class Hl7ToXml(object):
	def __init__ (self, *paths):
		# This is the XML document we'll be creating
		self._xmlDoc = Document()

	# <summary>
	# Converts an HL7 message into an XML representation of the same message.
	# </summary>
	# <param name="sHL7">The HL7 to convert</param>
	# <returns></returns>

	def convertToXml(self, stringHL7):
		
		#Go and create the base XML
		self._xmlDoc = self.createXmlDocument()

		# HL7 message segments are terminated by carriage returns,
		# so to get an array of the message segments, split on carriage return
		stringHL7Lines = stringHL7.split('\r')

		# Now we want to replace any other unprintable control
		# characters with whitespace otherwise they'll break the XML
		
		#for s in stringHL7Lines:
		#	s.replace("^","").replace("~","")

		# Go through each segment in the message
		# and first get the fields, separated by pipe (|),
		# then for each of those, get the field components,
		# separated by carat (^), and check for
		# repetition (~) and also check each component
		# for subcomponents, and repetition within them too.
		i = 0
		for s in stringHL7Lines:
			if i == len(stringHL7Lines):
				break
			else:
				# Don't care about empty lines
				if s.strip() != "":

					#Get the line and get the line's segments
					stringHL7Line = s
					stringFields = self.getMessageFields(stringHL7Line)
					#print stringFields,stringHL7Line
					# Create a new element in the XML for the line
					elline = self._xmlDoc.createElement(stringFields[0])
					self._xmlDoc.firstChild.appendChild(elline)

					# For each field in the line of HL7
					a = 0
					for f in stringFields:
						# Create a new element

						fieldEl = self._xmlDoc.createElement(stringFields[0] + "." + str(a))
						#print fieldEl, stringHL7Line
						if a == len(stringFields) :
							break
						else:
						

							# Part of the HL7 specification is that part
							# of the message header defines which characters
							# are going to be used to delimit the message
							# and since we want to capture the field that
							# contains those characters we need
							# to just capture them and stick them in an element.
					
				    			if stringFields[a] != "^~\\&":

								# Get the components within this field, separated by carats (^)
								# If there are more than one, go through and create an element for
								# each, then check for subcomponents, and repetition in both.

								stringComponents = self.getComponents(stringFields[a])
								#print stringFields[a],stringComponents,s
								if len(stringComponents) > 1:
									b = 0
									for c in stringComponents:
										if b == len(stringComponents):
											break
										else:
											componentEl = self._xmlDoc.createElement(stringFields[0] + "." \
										+ str(stringFields.index(f)) + "." + str(b+1))
											
											subComponents = self.getSubComponents(stringComponents[b])
											#print stringComponents, subComponents
											if len(subComponents) > 1:
												#There were subcomponents
												c = 0
												for sub in subComponents:
													if c == len(subComponents):
														break
													else:

													
														# Check for repetition
														subComponentRepetitions = self.getRepetitions(subComponents[c])
														#print subComponentRepetitions
														if len(subComponentRepetitions) > 1:
															d = 0
															for subr in subComponentRepetitions:
																if d == len(subComponentRepetitions):
																	break
																else:
																	subComponentRepEl = self._xmlDoc.createElement(stringFields[0] +  
																	"." + str(a+1) + \
																	 "." + str(b+1) + \
																	"." + str(c+1) + \
										  							"." + str(d+1))
																	if subComponentRepetitions[d] != "":
																		subComponentRepEl.appendChild(self._xmlDoc.createTextNode\
														(subComponentRepetitions[d]))
																		componentEl.appendChild(subComponentRepEl)
																	d += 1 
														else:
															subComponentEl = self._xmlDoc.createElement(stringFields[0] +  
																"." + str(a+1) + \
																 "." + str(b+1) + \
																"." + str(c+1))
															componentEl.appendChild(subComponentRepEl)
														c +=1
											
												if stringComponents[b] != "":
													fieldEl.appendChild(componentEl)
											else:
												#There were no subcomponents
												stringRepetitions = self.getRepetitions(stringComponents[b])
												if len(stringRepetitions) > 1:
													repetitionEl = ""
													e = 0
													
													for cr in stringRepetitions:
														if e == len(stringRepetitions):
															break
														else:
															repetitionEl = self._xmlDoc.createElement(sFields[0] +  
																			"." + str(a+1) + \
																			 "." + str(b+1) + \
																			"." + str(e+1))
															if stringRepetitions[e] != "":
																repetitionEl.appendChild(self._xmlDoc.createTextNode(stringRepetitions[e])) 
																componentEl.appendChild(repetitionEl)
															e += 1

													if stringComponents[b] != "":
														fieldEl.appendChild(componentEl)
														elline.appendChild(fieldEl)
												
												else:
													componentEl.appendChild( self._xmlDoc.createTextNode(stringComponents[b]))
												if stringComponents[b] != "":
													fieldEl.appendChild(componentEl)
													elline.appendChild(fieldEl)

											b += 1

								else:
									if stringFields[a] != "":
										fieldEl.appendChild( self._xmlDoc.createTextNode(stringFields[a]))
										elline.appendChild(fieldEl)
						
						

							else:
								#print stringFields[a]
								if stringFields[a] != "":
									fieldEl.appendChild( self._xmlDoc.createTextNode(stringFields[a]))
									elline.appendChild(fieldEl)
						
							a += 1

			i += 1
			#print i

		return self._xmlDoc.toxml()


	# <summary>
	# Split a line into its component parts based on pipe.
	# </summary>
	# <param name="s"></param>
	# <returns></returns>

	def  getMessageFields(self, s):
		return s.split('|')

	#<summary>
	# Get the components of a string by splitting based on carat.
	# </summary>
	# <param name="s"></param>
	# <returns></returns>

	def getComponents(self, s):
		return s.split('^')
		
	# <summary>
	# Get the subcomponents of a string by splitting on ampersand.
	# </summary>
	# <param name="s"></param>
	# <returns></returns>

	def getSubComponents(self, s):
		return s.split('&')

	# <summary>
	# Get the repetitions within a string based on tilde.
	# </summary>
	# <param name="s"></param>
	# <returns></returns>

	def getRepetitions(self, s):
		return s.split('~')

	# <summary>
	# Create the basic XML document that represents the HL7 message
	# </summary>
	# <returns></returns>


	def createXmlDocument(self):
		output = self._xmlDoc
		rootNode = output.createElement("HL7Message")
		output.appendChild(rootNode)
		return output


def buildValidatingOpener(ca_certs):
    """Build an opener with a given certs bundle and validate the ssl connection.

    @author: http://atlee.ca/blog/2011/02/10/verifying-https-python

    """

    class VerifiedHTTPSConnection(httplib.HTTPSConnection):
        def connect(self):
            # Overrides the version in httplib so that we do certificate verification
            sock = socket.create_connection((self.host, self.port),
                                            self.timeout)
            if self._tunnel_host:
                self.sock = sock
                self._tunnel()

            # Wrap the socket using verification with the root certs in trusted_root_certs
            self.sock = ssl.wrap_socket(sock,
                                        self.key_file,
                                        self.cert_file,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ca_certs=ca_certs,
                                        )

    # Wraps https connections with ssl certificate verification
    class VerifiedHTTPSHandler(urllib2.HTTPSHandler):
        def __init__(self, connection_class=VerifiedHTTPSConnection):
            self.specialized_conn_class = connection_class
            urllib2.HTTPSHandler.__init__(self)

        def https_open(self, req):
            return self.do_open(self.specialized_conn_class, req)

    https_handler = VerifiedHTTPSHandler()
    url_opener = urllib2.build_opener(https_handler)

    return url_opener



#stringHL7 = "MSH|^~\&|SHR|RwandaMOH|RapidSMS|316|20111109075738||ORU^R01^ORU_R01||D^C|V2.5^RWA|||||||||ALERT\rPID|||1198270120343040^^^^NID||\rOBR|1|||^Maternal Health Alert|||||||||||||||||||||||||||||||||||||||||||CHW\rOBX|1|CE|RISK^Alert^||HE||||||F"#%unichr(124)

#stringHL7 = "MSH|^~\&|RapidSMS|F316|SHR|RwandaMOH|20120229153909||ORU^R01^ORU_R01|2|D^C|2.5^RWA|||||||||PRE\rPID|||1197970079952017^^^^NID||name not available\rPV1|1|Community Health|316||||1198680069759062|||||||||||||||||||||||||||||||||||||20120229153909\rOBR|1|||^Maternal Health Reporting\rOBX|1|TS|^Date of Last Menstrual Period^||20111203||||||F\rOBX|2|NM|^Mother's Weight^||80.2|k|||||F\rOBX|3|TS|^Estimated Date of Delivery^||20120905||||||F\rOBX|4|CE|^Malaria^||ma||||||F\rOBX|5|CE|^Has Toilet^||to||||||F\rOBX|6|CE|^Has hand washing^||hw||||||F\r"

#stringHL7 = "MSH|^~\&|RapidSMS|F316|SHR|RwandaMOH|20120229154622||ORU^R01^ORU_R01|3|D^C|2.5^RWA|||||||||RISK\rPID|||1197970079952017^^^^NID||name not available\rPV1|1|Community Health|316||||1198680069759062|||||||||||||||||||||||||||||||||||||20120229154622\rOBR|1|||^Maternal Health Reporting\rOBX|1|NM|^Mother's Weight^||71.2|k|||||F\rOBX|2|CE|^Fever^||fe||||||F\rOBX|3|CE|^Hemorrhaging Bleeding^||he||||||F\rOBX|4|CE|^At home^||ho||||||F\r"

#stringHL7 = "MSH|^~\&|RapidSMS|F316|SHR|RwandaMOH|20120229155325||ORU^R01^ORU_R01|4|D^C|2.5^RWA|||||||||BIR\rPID|||1197970079952017^^^^NID||name not available\rPV1|1|Community Health|316||||1198680069759062|||||||||||||||||||||||||||||||||||||20120229155325\rOBR|1|||^Maternal Health Reporting\rOBX|1|TS|^Birth Date^||20120105||||||F\rOBX|2|NM|^Baby Weight^||3.3|k|||||F\rOBX|3|CE|^Male^||bo||||||F\rOBX|4|CE|^At clinic facility^||cl||||||F\rOBX|5|NM|^Child Number^||1.00000||||||F\r"

#stringHL7 = "MSH|^~\&|RapidSMS|F316|SHR|RwandaMOH|20120229155627||ORU^R01^ORU_R01|5|D^C|2.5^RWA|||||||||MAT\rPID|||1197970079952017^^^^NID||name not available||||||||||||||||||||||||20120229155627\rPV1|1|Community Health|316||||1198680069759062|||||||||||||||||||||||||||||||||||||20120229155627\rOBR|1|||^Maternal Health Reporting\rOBX|1|CE|^New Born Death^||nd||||||F\r"

#stringHL7 = "MSH|^~\&|RapidSMS|F316|SHR|RwandaMOH|20120301084552||ORU^R01^ORU_R01|1|D^C|2.5^RWA|||||||||REG\rSTF||1198680069759062||Community Health Worker||||^Manu\rORG|1||||^^^^^316\rLAN|1|RW\r"

#stringHL7 = "MSH|^~\&#|SHR|RwandaMOH|RapidSMS|F316|20120323173401||ORU^R01^ORU_R01||D^C|2.5^RWA|||||||||ALERT\rPID|||1198680069759062^^^^NID||\rOBR|1|||^Maternal Health Reporting|||||||||||||||||||||||||||||||||||||||||||CHW\rOBX|1|CE|Reminder^Antenatal Care Visit^||anc4||||||F\r"


stringHL7 = "MSH|^~\&#|SHR|RwandaMOH|RapidSMS|F316|20120312191055||ORU^R01^ORU_R01||D^C|2.5^RWA|||||||||ALERT\rPID|||1198680069759062^^^^NID||\rOBR|1|||^Maternal Health Reporting|||||||||||||||||||||||||||||||||||||||||||CHW\rOBX|1|CE|Risk^Hemorrhaging Bleeding^||he||||||F\r"

#wayne@jembi.org, suranga@jembi.org
# Send pregnancy notifications to the SHR (pregnancy.xml)
# Send birth notifications to the SHR (birth.xml)
# Send risk notifications to the SHR	(risk.xml)
# Send maternal death notifications to the SHR (death.xml)
# Send Community Health Worker registration notifications to the SHR (chw.xml)

# Receive alert from SHR (alert.xml)

# Receive reminder from SHR (reminder.xml)
#
#
#

#print RheaNotification().createOutgoingNotification(Report.objects.get(pk = 5))
#print RheaNotification().import_concepts()
#print Hl7ToXml().convertToXml(stringHL7)



