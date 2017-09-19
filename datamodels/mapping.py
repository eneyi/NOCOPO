#this script mpps old bpp releases data to new ocds formats
import random, json, datetime
from bson import json_util
from dateutil import parser



def create_ocds_data_model(ocid,title, description, agency, abb, ministry, pm, tag,amount, quantity,suppliers,milestoneDescription,milestoneStatus,awardDate,awardAmount, tenderAmount, planningAmount, contractAmount,contractStartDate,contractEndDate,tenderStartDate, tenderEndDate, awardStartDate, awardEndDate):
    rand1= randd(8)
    data={
            "language": "EN",
            "ocid": ocid.lower(),
            "date":awardDate,
            "tag": [tag],
            "initiationType": "tender",
            "buyer": {
                "name": agency,
                "identifier": {
                    "scheme": "NGA-"+abb.upper(),
                    "id": randd(8),
                    "legalName": agency,
                    "uri": ""
                }
            },
            "tender": {
                "id": ocid.lower()+"-tender",
                "title": title.lower(),
                "description": description.lower(),
                "status": "", #active,planned,cancelled,unsuccesful,complete
                "items": [
                            {
                                "id": ocid.lower()+"-tender-item-"+rand1,
                                "description": "",
                                "classification": {
                                    "description": "",
                                    "scheme": "CPV",
                                    "id": rand1,
                                    "uri": ""
                                },
                                "deliveryLocation": {
                                    "geometry": {
                                        "type": "Point",
                                        "coordinates": [51.751944, -1.257778]
                                    },
                                    "gazetteer": {
                                        "scheme": "GEONAMES",
                                        "identifiers": ["2640729"]
                                    },
                                    "description": "",
                                    "uri": ""
                                },
                                "deliveryAddress": {
                                    "postalCode": "",
                                    "countryName": "",
                                    "streetAddress": "",
                                    "region": "",
                                    "locality": ""
                                },
                                "unit": {
                                    "name": "",
                                    "value": {
                                        "currency": "NGN",
                                        "amount": tenderAmount
                                    }
                                },
                                "quantity": quantity
                            }
                        ],
                "value": {
                    "amount":tenderAmount,
                    "currency": "NGN"
                },
                "procurementMethod": pm, 
                "awardCriteria": "",
                "submissionMethod": [
                    ""
                ],
                "tenderPeriod": {
                    "startDate": tenderStartDate,
                    "endDate":tenderEndDate
                },
                "awardPeriod": {
                    "startDate": awardStartDate,
                    "endDate": awardEndDate
                },
                "enquiryPeriod": {
                    "startDate": "",
                    "endDate": ""
                },
                "hasEnquiries":"No",
                "eligibilityCriteria":"",
                "tenderers":
                [
                    {
                        "identifier":"",
                        "additionalidentifiers":"",
                        "name":"",
                        "address":
                        {
                            "streetAddress":"",
                            "locality":"",
                            "region":"",
                            "postalCode":"",
                            "countryName":""
                        },
                        "contactPoint":
                        {
                            "name":"",
                            "email":"",
                            "telephone":"",
                            "faxNumber":"",
                            "url":""
                        }
                    }
                ],
                "numberOfTenderers":"",
                "procuringEntity":
                 {
                        "identifier":agency,
                        "additionalidentifiers":agency,
                        "name":"",
                        "address":
                        {
                            "streetAddress":"",
                            "locality":"",
                            "region":"",
                            "postalCode":"",
                            "countryName":"Nigeria"
                        },
                        "contactPoint":
                        {
                            "name":"",
                            "email":"",
                            "telephone":"",
                            "faxNumber":"",
                            "url":""
                        }
                    },
                "documents":
                [
                    {
                        "id":"documentid",
                        "documentType":"",
                        "title":"",
                        "description":"",
                        "url":"",
                        "datePublished":"",
                        "dateModified":"",
                        "format":"",
                        "language":"EN"
                    }
                ],
                "milestones":
                [
                    {
                        "id":"",
                        "title":"",
                        "description":"",
                        "dueDate":"",
                        "dateModified":"",
                        "status":"",#met,notMet,partiallyMet,
                         "documents":
                                [
                                    {
                                        "id":ocid.lower()+"-tender-milestone",
                                        "documentType":"",
                                        "title":"",
                                        "description":"",
                                        "url":"",
                                        "datePublished":"",
                                        "dateModified":"",
                                        "format":"",
                                        "language":"EN"
                                    }
                                ]

                    }
                ]
                
            },
            "planning":{
                "budget":{
                    "source":"",
                    "id":ocid.lower()+"-budgetlineitem",
                    "description":"",
                    "amount":planningAmount,
                    "project":title,
                    "projectID":"",
                    "uri":""
                },
                "rationale":"",
               "documents":
                    [
                        {
                            "id":ocid.lower()+"-planning-document",
                            "documentType":"",
                            "title":"",
                            "description":"",
                            "url":"documentLink",
                            "datePublished":"",
                            "dateModified":"",
                            "format":"",
                            "language":"EN"
                        }
                    ]
                
            },
            "awards":[{
                "id":ocid.lower()+"-award",
                "title":title,
                "description":description,
                "status":"",
                "date":awardDate,
                "value":{
                    "amount":awardAmount,
                    "currency":"NGN"
                },
                "suppliers":
                [
                    
                ],
               
                "items": [
                            {
                                "id": ocid.lower()+"-award-item",
                                "description": "",
                                "classification": {
                                    "description": "",
                                    "scheme": "CPV",
                                    "id": rand1,
                                    "uri": ""
                                },
                                "deliveryLocation": {
                                    "geometry": {
                                        "type": "Point",
                                        "coordinates": [51.751944, -1.257778]
                                    },
                                    "gazetteer": {
                                        "scheme": "GEONAMES",
                                        "identifiers": [rand1]
                                    },
                                    "description": "",
                                    "uri": ""
                                },
                                "deliveryAddress": {
                                    "postalCode": "",
                                    "countryName": "",
                                    "streetAddress": "",
                                    "region": "",
                                    "locality": ""
                                },
                                "unit": {
                                    "name": "Items",
                                    "value": {
                                        "currency": "NGN",
                                        "amount": 0
                                    }
                                },
                                "quantity": 1                            }
                        ]
            }
                     ],
            "contracts":[{
                "id":ocid.lower()+"-contract",
                "awardID": ocid.lower()+"-award",#should be in award.id+ocds
                "title":"",
                "description":description,
                "status":"awarded", #pending,active,cancelled,terminated,
                "period": {
                    "startDate": contractStartDate,
                    "endDate": contractEndDate
                },
                "value": {
                    "amount":contractAmount,
                    "currency": "NGN"
                },
                "items": [
                            {
                                "id": ocid.lower()+"-contract-milestone",
                                "description": "",
                                "classification": {
                                    "description": "",
                                    "scheme": "CPV",
                                    "id": randd(8),
                                    "uri": ""
                                },
                                "deliveryLocation": {
                                    "geometry": {
                                        "type": "Point",
                                        "coordinates": [9.0820, 8.6753]
                                    },
                                    "gazetteer": {
                                        "scheme": "GEONAMES",
                                        "identifiers": [rand1]
                                    },
                                    "description": "",
                                    "uri": ""
                                },
                                "deliveryAddress": {
                                    "postalCode": "",
                                    "countryName": "",
                                    "streetAddress": "",
                                    "region": "",
                                    "locality": ""
                                },
                                "unit": {
                                    "name": ocid.lower()+"-unit-item",
                                    "value": {
                                        "currency": "NGN",
                                        "amount":0
                                    }
                                },
                                "quantity": 1
                            }
                        ],
                "dateSigned":"",
                 "documents":
                                [
                                    {
                                        "id":ocid.lower()+"-contract-document",
                                        "documentType":"",
                                        "title":"",
                                        "description":"",
                                        "url":"documentLink",
                                        "datePublished":"",
                                        "dateModified":"",
                                        "format":"",
                                        "language":"EN"
                                    }
                                ],
                "implementation":{
                    "transactions":[
                        {
                            "id":ocid.lower()+"-nga-contract-document-transactions-"+randd(8),
                            "source":"",
                            "date":awardDate,
                            "amount": 
                                        {
                                "amount":awardAmount,
                                "currency": "NGN"
                            },
                            "providerOrganization": {
                    "scheme": "NGN-"+abb.upper(),
                    "id":randd(8),
                    "legalName": agency,
                    "uri": ""
                },
                            "recieverOrganization": {
                    "scheme": "NGN-"+abb.upper(),
                    "id": randd(8),
                    "legalName": agency,
                    "uri": ""
                },
                            "uri":"http://transaction"
                        }
                    ],
                     "milestones":
                [
                    {
                        "id":ocid.lower()+"-contract-implementation-milestone",
                        "title":title.lower()+"-implementation-progress",
                        "description":milestoneDescription,
                        "dueDate":"",
                        "dateModified":"",
                        "status":milestoneStatus, #met,notMet,partiallyMet,
                         "documents":
                                [
                                    {
                                        "id":"",
                                        "documentType":"",
                                        "title":"",
                                        "description":"",
                                        "url":"",
                                        "datePublished":"",
                                        "dateModified":"",
                                        "format":"",
                                        "language":"EN"
                                    }
                                ]

                    }
                    ],
                     "documents":
                                [
                                    {
                                        "id":ocid.lower()+"-contract-implementation-document",
                                        "documentType":"",
                                        "title":"",
                                        "description":"",
                                        "url":"documentLink",
                                        "datePublished":"",
                                        "dateModified":"",
                                        "format":"",
                                        "language":"EN"
                                    }
                                ]
                    
                }
                
            }]
        }
        
        
    for supplier in suppliers:
        data['awards'][0]['suppliers'].append({
                    "identifier":supplier['name'],
                        "additionalidentifiers":supplier['additionalIdentifiers'],
                        "name":supplier['name'],
                        "address":
                        {
                            "streetAddress":"",
                            "locality":"",
                            "region":"",
                            "postalCode":"",
                            "countryName":""
                        },
                        "contactPoint":
                        {
                            "name":"",
                            "email":"",
                            "telephone":"",
                            "faxNumber":"",
                            "url":""
                        }
                    })
    return data

####parses a time and date 'ocid_date'
def stripdate(date):
    patterns = ['%m-%d-%y', '%m/%d/%y', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%y', '%d/%m/%Y', '%d-%m-%y', '%d-%m-%Y']
    formatted = ""
    
    if ("-" in date or "/" in date):
        for pattern in patterns:
            if formatted == "":
                try:
                    formatted = datetime.datetime.strptime(date, pattern).date()
                except:
                    formatted=""
            else:
                break;
    else:
        try:
            formatte = datetime.date.fromordinal(int(date))
            formatted = datetime.datetime.strptime(formatted.strftime(formatte), pattern).date()
        except:
            formatted ="Unknown"
            return formatted
    return str(formatted)+"T00:00:00Z"
    
    
def abbreviate(stringInput):
    words = stringInput.split()
    letters = "".join([i[0] for i in words])
    abb = letters.upper()
    return abb

def randd(lengthNum):
    integer = ''
    for i in range(0,8):
        integer+=str(random.randint(0,10))
    return integer

with open('releases.json', 'r') as ff:
    for line in ff:
        try:
       
            data = json.loads(line)
            ocid=data['ocid']
            title=data['tender']['title']
            description = data['tender']['description']
            agency=data['buyer']['identifier']['legalName']
            abb = abbreviate(agency)
            ministry= "NA"
            pm=data['tender']['procurementMethod']
            tag=data['tag'][0]
            amount=data['planning']['budget']['amount']['amount']
            quantity=1
            suppliers=data['awards'][0]['suppliers']
            milestoneDescription=data['contracts'][0]['implementation']['milestones'][0]['description']
            milestoneStatus=data['contracts'][0]['implementation']['milestones'][0]['status']
            awardAmount=data['awards'][0]['value']['amount']
            planningAmount=data['planning']['budget']['amount']['amount']
            tenderAmount=data['tender']['value']['amount']
            contractAmount=data['awards'][0]['value']['amount']
            
            try:
                awardDate = stripdate(data['awards'][0]['date'])
            except:
                awardDate="Unknown"
                
            try:
                awardStartDate = stripdate(data['awards'][0]['date'])
            except:
                awardStartDate ="Unknown"
                
            try:
                awardEndDate = stripdate(data['awards'][0]['date'])
            except:
                awardEndDate ="Unknown"
            
            try:
                tenderStartDate = stripdate(data['tender']['tenderPeriod']['startDate'])
            except:
                tenderStartDate = "Unknown"
            
            try:
                
                tenderEndDate = stripdate(data['tender']['tenderPeriod']['endDate'])
            except:
                tenderEndDate = "Unknown"
            
            try:
                contractStartDate = stripdate(data['contracts'][0]['period']['startDate'])
            except:
                "Uknown"
            
            try:
                contractEndDate = stripdate(data['contracts'][0]['period']['endDate'])
            except:
                "Unknown"
            newdata = create_ocds_data_model(ocid,title, description, agency, abb, ministry, pm, tag,amount, quantity,suppliers,milestoneDescription,milestoneStatus,awardDate,awardAmount, tenderAmount, planningAmount, contractAmount,contractStartDate,contractEndDate,tenderStartDate,tenderEndDate, awardStartDate, awardEndDate)
            print(json.dumps(newdata))
            print(",")
        except:
            pass
    
