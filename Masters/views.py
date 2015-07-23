from django.shortcuts import render
from Masters.models import *
from django.http import HttpResponse
import json
from collections import defaultdict
import time
from datetime import date, timedelta
import datetime

def doc_data(request):
    result = []
    if request.method == 'GET':
        doc = str(request.GET.get('id',''))
        doc_data = DimDoctorForm.objects.filter(doctoridentifier=str(doc)).values_list('form','id')
        for data in doc_data:
            temp = {}
            temp['id']=data[1]
            temp['form_data']=data[0]
            result.append(temp)
        doc_data = json.dumps(result)
        return doc_data


def get_drugdata(request):
    all_info=defaultdict(list)
    drug_details = DrugInfo.objects.all().values_list('drug_name','frequency','dosage__dosage','direction__directions')
    for drug in drug_details:
        drug_data = {}
        drug_data['name']=drug[0]
        drug_data['frequency'] = int(drug[1])
        drug_data['dosage']=drug[2]
        drug_data['direction']=drug[3]
        all_info['drug_data'].append(drug_data)
    diagnosis = ICD10.objects.filter(can_select='True',status='True').values_list('ICD10_Chapter','ICD10_Code','ICD10_Name')
    for d in diagnosis:
        diagnosis_data={}
        diagnosis_data['ICD10_Chapter']=d[0]
        diagnosis_data['ICD10_Code']=d[1]
        diagnosis_data['ICD10_Name']=d[2]
        all_info['diagnosis_data'].append(diagnosis_data)
    investigation_info = Investigations.objects.filter(is_active=True).values_list('service_group_name','investigation_name')
    for investigation in investigation_info:
        investigation_data = {}
        investigation_data['service_group_name'] = investigation[0]
        investigation_data['investigation_name'] = investigation[1]
        all_info['investigation_data'].append(investigation_data)
    result_json = json.dumps(all_info)
    return HttpResponse(result_json)

def poc_update(request):
    if request.method =="GET":
        document_id=request.GET.get("docid","")
        poc_info=request.GET.get("pocinfo","")
        visitid=request.GET.get("visitid","")
        entityid=request.GET.get("entityid","")
        docid=request.GET.get("doctorid","")
        pending =request.GET.get("pending","")

    elif request.method =="POST":
        document_id=request.POST.get("docid","")
        poc_info=request.POST.get("pocinfo","")
        visitid=request.POST.get("visitid","")
        entityid=request.POST.get("entityid","")
        docid=request.POST.get("doctorid","")
        pending =request.POST.get("pending","")
    poc = []
    poc_data = {}
    poc_data['pending']=pending
    poc_data['poc'] = str(poc_info)
    poc.append(poc_data)
    poc_backup = json.dumps(poc)

    #Adding poc and related doctor to backup table helpful for history
    add_poc_backup = PocBackup(visitentityid=str(visit_info[0][0]),entityidec=str(visit_info[0][1]),docid=str(docid),poc=poc_backup)
    add_poc_backup.save()

    #Getting old poc value give to patient
    visit_backup = PocBackup.objects.filter(visitentityid=str(visitid),entityidec=str(entityid)).values_list('poc','id')
    if len(visit_backup)>0:
    	for visit in visit_backup:
            old_poc= json.loads(visit[0][0])
            poc.append(old_poc)

    #Reading all values from document
    result = {}
    entity_detail="curl -s -H -X GET http://202.153.34.169:5984/drishti-form/_design/FormSubmission/_view/by_id/?key=%22"+str(document_id)+"%22"
    poc_output=commands.getoutput(entity_detail)
    poutput=json.loads(poc_output)
    form_ins= poutput['rows'][0]['value'][2]
    row_data = poutput['rows'][0]['value'][2]['formInstance']['form']['fields']
    #Updating docPocInfo with pending reason or poc
    for i in range((len(row_data))):
        row = row_data[i]
        if 'name' in row.keys():
            if str(row['name']) == 'docPocInfo':
                old_poc = json.loads(row['value'])
                if len(old_poc)==0:
                    poc_json = json.dumps(poc)
                    row['value']=poc_json
                    row_data[i]=row
    #Creating new document with latest docPocInfo
    result["_id"]=str(form_ins["_id"])
    result["_rev"]=str(form_ins["_rev"])
    result["anmId"]=str(form_ins["anmId"])
    result["clientVersion"]=str(form_ins["clientVersion"])
    result["entityId"]=str(form_ins["entityId"])
    result["formDataDefinitionVersion"]=str(form_ins["formDataDefinitionVersion"])
    result["formInstance"]=form_ins["formInstance"]
    result["formName"]=str(form_ins["formName"])
    result["instanceId"]=str(form_ins["instanceId"])
    result["serverVersion"]=int(round(time.time() * 1000))
    result["type"]=str(form_ins["type"])
    ord_result = json.dumps(result)
    poc_doc_update_curl = "curl -vX PUT http://202.153.34.169:5984/drishti-form/%s -d '''%s'''" %(str(document_id),ord_result)
    poc_doc_update=commands.getoutput(poc_doc_update_curl)

    if len(pending)>0:
        update_poc=PocInfo.objects.filter(visitentityid=str(visitid),entityidec=str(entityid)).update(pending=str(pending),docid=str(docid))

    #Updating backup table with latest poc/pending status info
    visit_info = PocInfo.objects.filter(visitentityid=str(visitid),entityidec=str(entityid)).values_list('visitentityid','entityidec')
    if len(pending)==0:
        #Removing record provided POC
        del_poc = PocInfo.objects.filter(visitentityid=str(visitid),entityidec=str(entityid)).delete()
    return HttpResponse(json.dumps({"status":"success"}))


def doctor_data(request):
    ''' Method to show all pending cases on doctor home screen with patient details'''
    if request.method == "GET":
        doc_name= request.GET.get('docname',"")
        password = request.GET.get('pwd',"")
    elif request.method == "POST":
        doc_name= request.GET.get('docname',"")
        password = request.GET.get('pwd',"")
    end_res = '{}'
    doc_phc = str(DocInfo.objects.filter(docname=str(doc_name)).values_list('phc__name')[0][0])
    doc_pwd = hashlib.sha1()
    doc_pwd.update(password)
    doc_password = doc_pwd.hexdigest()
    user_pwd_db = DimUserLogin.objects.filter(name=str(doc_name)).values_list('password')
    resultdata=defaultdict(list)
    display_result=[]
    entity_list = PocInfo.objects.filter(phc=doc_phc).values_list('visitentityid','entityidec','pending','docid').distinct()

    #If no record availble for doctor screen display
    if len(entity_list) == 0:
    	return HttpResponse(json.dumps(display_result))

    #Iterating all pending cases to display over doctor home screen
    for entity in entity_list:
        if str(entity[2])!='None':
            if len(entity[2])>1 and str(doc_name) != str(entity[3]):
                continue
    	entity_detail_id=str(entity[1])
        #Curl command to read visit related data
        ancvisit_detail="curl -s -H -X GET http://202.153.34.169:5984/drishti-form/_design/FormSubmission/_view/by_EntityId?key=%22"+str(entity[0])+"%22"
        visit_output = commands.getoutput(ancvisit_detail)
        visit_data1 = json.loads(visit_output)
        row = visit_data1['rows']
        visit_data=[]
        poc_len=1
        doc_con='no'
        for i in range(len(row)):
            visit={}
            newvisitdata=defaultdict(list)
            newvisit={}
            field_data = row[i]['value'][1]['form']['fields']
            for f in range((len(field_data)-1),-1,-1):
                fd = field_data[f]
                if 'name' in fd.keys():
                    if fd['name'] == 'docPocInfo':
                        poc_len=len(fd['value'])
                    elif fd['name'] == 'isConsultDoctor':
                        doc_con = fd['value']
            #Check if record is recommended for doctor consultation
            if doc_con == 'yes':
                #-----------------PNC DATA --------------
                if row[i]['value'][0] == 'pnc_visit':
                    doc_id=row[i]['id']
                    for visitdata in row[i]['value'][1]['form']['fields']:
                        key = visitdata.get('name')
                        if 'value' in visitdata.keys(): 
                            value = visitdata.get('value')
                        else:
                        	value=''
                        if key == 'pncNumber':
                            visit['pncNumber']=value
                        elif key=='pncVisitDate':
                            visit['pncVisitDate']=value
                        elif key == 'difficulties1':
                            visit['difficulties1']=value
                        elif key == 'difficulties2':
                            visit['difficulties2']=value
                        elif key == 'abdominalProblems':
                            visit['abdominalProblems']=value
                        elif key == 'urineStoolProblems':
                            visit['urineStoolProblems']=value
                        elif key == 'hasFeverSymptoms':
                            visit['hasFeverSymptoms']=value    
                        elif key == 'breastProblems':
                            visit['breastProblems']=value
                        elif key == 'vaginalProblems':
                            visit['vaginalProblems']=value
                        elif key == 'bpSystolic':
                            visit['bpSystolic']=value
                        elif key == 'bpDiastolic':
                            visit['bpDiastolic']=value
                        elif key == 'temperature':
                            visit['temperature']=value
                        elif key == 'pulseRate':
                            visit['pulseRate']=value
                        elif key == 'bloodGlucoseData':
                            visit['bloodGlucoseData']=value
                        elif key == 'weight':
                            visit['weight']=value
                        elif key == 'pncVisitPlace':
                        	visit['pncVisitPlace']=value
                        elif key == 'pncVisitDate':
                        	visit['pncVisitDate']=value                        	
                        elif key == 'isHighRisk':
                        	visit['isHighRisk']=value
                        elif key == 'hbLevel':
                            visit['Hblevel']=value
                            visit['visit_type'] = 'PNC'
                        visit["entityid"] = entity[0]
                        visit['id']=doc_id 
                    visit_data.append(visit)

                elif row[i]['value'][0] == 'anc_visit': 
                    doc_id=row[i]['id']
                    for visitdata in row[i]['value'][1]['form']['fields']:
                        key = visitdata.get('name') 
                        if 'value' in visitdata.keys(): 
                            value = visitdata.get('value')
                        else:
                        	value=''
                        if key == 'ancVisitNumber':
                            visit['ancVisitNumber']=value
                        elif key == 'ancNumber':
                            visit['ancNumber']=value                            
                        elif key == 'ancVisitPerson':
                            visit['ancVisitPerson']=value
                        elif key=='ancVisitDate':
                            visit['ancVisitDate']=value
                        elif key == 'riskObservedDuringANC':
                            visit['riskObservedDuringANC']=value
                        elif key == 'bpSystolic':
                            visit['bpSystolic']=value
                        elif key == 'bpDiastolic':
                            visit['bpDiastolic']=value
                        elif key == 'temperature':
                            visit['temperature']=value
                        elif key == 'pulseRate':
                            visit['pulseRate']=value
                        elif key == 'bloodGlucoseData':
                            visit['bloodGlucoseData']=value
                        elif key == 'weight':
                            visit['weight']=value
                        elif key == 'fetalData':
                            visit['fetalData']=value
                            visit['visit_type'] = 'ANC'
                        visit["entityid"] = entity[0]
                        visit['id']=doc_id   
                    visit_data.append(visit)
                elif row[i]['value'][0] == 'child_illness':
                    doc_id=row[i]['id']
                    for childdata in row[i]['value'][1]['form']['fields']:
                        key = childdata.get('name') 
                        if 'value' in childdata.keys(): 
                            value = childdata.get('value')
                        else:
                        	value=''
                        if key =='dateOfBirth':
                        	visit['dateOfBirth']=value
                        	age = datetime.datetime.today()-datetime.datetime.strptime(str(value),"%Y-%m-%d")
                        	visit['age']=age.days
                        	visit['visit_type'] = 'CHILD'
                        elif key == 'childSigns':
                        	visit['childSigns']=value
                        elif key =='childSignsOther':
                        	visit['childSignsOther']=value
                        elif key =='immediateReferral':
                        	visit['immediateReferral']=value
                        elif key =='immediateReferralReason':
                        	visit['immediateReferralReason']=value
                        elif key =='reportChildDisease':
                        	visit['reportChildDisease']=value
                        elif key =='reportChildDiseaseOther':
                        	visit['reportChildDiseaseOther']=value
                        elif key =='reportChildDiseaseDate':
                        	visit['reportChildDiseaseDate']=value
                        elif key =='reportChildDiseasePlace':
                        	visit['reportChildDiseasePlace']=value
                        elif key =='numberOfORSGiven':
                        	visit['numberOfORSGiven']=value
                        elif key =='childReferral':
                        	visit['childReferral']=value
                        elif key =='submissionDate':
                        	visit['submissionDate']=value
                        elif key == 'id':
                        	visit['id']=doc_id
                        	visit["entityid"] = entity[0]
                    visit_data.append(visit)
        #CURL command to read registration related info
        entity_detail="curl -s -H -X GET http://202.153.34.169:5984/drishti-form/_design/FormSubmission/_view/by_EntityId?key=%22"+entity_detail_id+"%22"
        poc_output=commands.getoutput(entity_detail)
        poutput=json.loads(poc_output)
        row1 = poutput['rows']
        if len(visit_data)>0 and len(row1)>0:
            result=defaultdict(list)
            for data in row1[0]["value"][1]['form']['fields']:
                key=data.get('name')
                value=data.get('value')
                if key=='wifeName':
                    temp={}
                    temp={key:value}
                    result.update(temp)
                elif key=='wifeAge':
                    temp={}
                    temp={key:value}
                    result.update(temp)
                elif key=='district':
                    temp={}
                    temp={key:value}
                    result.update(temp)
                elif key=='husbandName':
                    temp={}
                    temp={key:value}
                    result.update(temp)
                elif key=='village':
                    temp={}
                    temp={key:value}
                    result.update(temp)
                elif key == 'aadharNumber':
                    temp={}
                    temp={key:value}
                    result.update(temp)
            if row1[0]['value'][0] == "anc_registration_oa" or row1[0]['value'][0]=="anc_registration":
                for data in row1[0]["value"][1]['form']['fields']:
                    key=data.get('name')
                    value=data.get('value')
                    if key=='edd':
                        temp={}
                        temp={key:value}
                        visit['edd']=value
            elif row1[0]['value'][0] == "child_registration_oa":
            	for child_data in row1[0]["value"][1]['form']['fields']:
                    key = child_data.get('name') 
                    if 'value' in child_data.keys(): 
                        value = child_data.get('value')
                    else:
                        value=''
                    if key == 'gender':
                        visit['gender']=value
                    elif key == 'name':
                        visit['name']=value
                    elif key == 'registrationDate':
                        visit['registrationDate']=value
                    elif key =='edd':
                    	visit['edd']=value
                    elif key == 'motherName':
                        temp={}
                        temp={key:value}
                        result.update(temp)
                    elif key == 'fatherName':
                        temp={}
                        temp={key:value}
                        result.update(temp)
            temp_list=[]
            temp_list.append(visit_data[-1])
            result["riskinfo"]=temp_list
            result["entityidec"] = entity_detail_id
            result["anmId"] = row1[0]['value'][2]
            display_result.append(result)
        end_res= json.dumps(display_result)
    return HttpResponse(end_res)
