from flask import Flask, flash, render_template, json, request, url_for, redirect
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from flask import session
import random
import string
import time, geocoder
from time import gmtime, strftime
import zipfile
from pymongo import MongoClient
#from datetime import datetime
import datetime
import string
from bson.objectid import ObjectId
from bson import Binary, Code
from bson.json_util import dumps
import os 
from os import listdir
from flask import send_from_directory, send_file 
from werkzeug import secure_filename
import webbrowser







##EXAMPLE FUNCTION TO GET THE DATA 

#retrieve tender method
@app.route('/getTenders', methods=['POST'])
def getTenders():
    try:
        if session.get('user'):
            
            _user = session.get('user')
           
            _agencyName = session.get('agencyName')
            
            _offset = int(request.form['offset'])
            _limit = pageLimit
            
            releases = db.release.find({"releases.buyer.identifier.legalName":_agencyName}).sort([('_id', -1)]).skip(_offset).limit(_limit)

            res = db.release.find({"releases.buyer.identifier.legalName":_agencyName}).count()
            #print(res)

            response = []
            releases_dict = []
#parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON
            
            #looping through each query output
            for release in releases:
                #looping through each release in releases since all releases are in releases array
                #using [''] to go into curly brackets in MongoDB structure
                #e.g., "value": {"amount": 9480000 },  => inrel['tender']['value']['amount']
                #using [index] to get array element
                #e.g., Tag':rel['tag'][0], OR longit': coord[0],
                for inrel in release['releases']:

                    d = inrel['tender']['advertisementdate']
                    #collecting year, month and date from ISO date format
                    dString = d.strftime("%Y-%m-%d")
                    # to do the reverse
                    #example usage - parse_datetime(date)
                    release_dict = {
                                'OCID': inrel['ocid'],
                                'tender_Description' : inrel['tender']['description'],
                                'Number_of_tenderers': inrel['tender']['numberoftenderers'],
                                'tender_status': inrel['tender']['status'],
                                'advert_date': dString,
                                'estimated_cost': inrel['tender']['value']['amount']}

                    releases_dict.append(release_dict)
                    response.append(releases_dict)
                    response.append({'total':res})
                    #example output is in proper json using json.dumps converts it to json for you from bson
                    #[[{"OCID": "OCDS-2016-UNIBEN2016359-22-54-45", "Project_Description": "Road works", "Published_Date": "2016-12-28", "Release_Tag": ["Tender"]}], {"total": 1}]
            print json.dumps(response)
#convert into json after converting to dictionary
            return json.dumps(response)

        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))



   ##HELPER METHOD TO CONVERT DATE FROM FORM OR OTHERS TO ISO DATE FORMAT

   def parse_datetime(ocid_date):
    
    if ocid_date:
        #change format of date here to Isaacs date format or as stored in db
        ocid_date_no = datetime.datetime.strptime(ocid_date, "%Y-%m-%d")
        return ocid_date_no
    else:
        emptyfield = " "
        return emptyfield

    ##example usage - parse_datetime(prepbymdastart)





    #################################API JSON OUTPUT
 
    #retrieve tender method - can be get release

@app.route('/getTenders', methods=['POST'])
def getTenders():
    try:
        if session.get('user'):
            
            _user = session.get('user')
           
            _agencyName = session.get('agencyName')
            
            _offset = int(request.form['offset'])
            _limit = pageLimit
            
            releases = db.release.find({"releases.buyer.identifier.legalName":_agencyName}).sort([('_id', -1)]).skip(_offset).limit(_limit)

            res = db.release.find({"releases.buyer.identifier.legalName":_agencyName}).count()
            #print(res)
            
            response = {}
            #releases_dict = []
#parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON
            
            #looping through each query output
            for release in releases:
                #looping through each release in releases since all releases are in releases array
                #using [''] to go into curly brackets in MongoDB structure
                #e.g., "value": {"amount": 9480000 },  => inrel['tender']['value']['amount']
                #using [index] to get array element
                #e.g., Tag':rel['tag'][0], OR longit': coord[0],
                for inrel in release['releases']:

                    d = inrel['tender']['advertisementdate']
                    #collecting year, month and date from ISO date format
                    dString = d.strftime("%Y-%m-%d")
                    # to do the reverse
                    #example usage - parse_datetime(date)

                    releases_dict = 
                                'uri':'uri-topackage',
 'publisher':'Public Bureau Of Procurement Nigeria',
 'license':'BPPLicense',
 'publicationPolicy':'',
 'publishedDate':'',
 'records':[
     {
         'compiledReleases':'allReleases',
         'releases':[{'date':'', 'tag':'', 'uri'}]
     }
 ],   
 'releases':[
        {
            'language': 'en',
            'ocid': 'ocds-213czf-000-00002',
            'id': 'ocds-213czf-000-00002-01-tender',
            'date': '2016-01-01T09:30:00Z',
            'tag': [
                //options: planning,tender,tenderAmendment,tenderUpdate,tenderCancellation,award,awardUpdate,awardCancellation,contract,contratUpdate,ContractAmendment, implementation, implementationUpdate, contractTermination,compiled
                
                'tender'
            ],//append new tags to array, dont replace
            'initiationType': 'tender',
            'buyer': {
                'name': 'Open Data Services',
                'identifier': {
                    'scheme': 'NGA-AbbreviationOfBuyer',
                    'id': '09506232',
                    'legalName': 'Open Data Services Co-operative',
                    'uri': 'https://opencorporates.com/companies/gb/09506232'
                }
            },
            'tender': {
                'id': 'ocds-213czf-000-00001-01-tender',
                'title': 'Data merging tool',
                'description': 'Creation of a data merging tool.',
                'status': 'active',
                'items': [
                            {
                                'id': 'item1',
                                'description': 'Ceremonial Trumpets for Oxford Town Hall',
                                'classification': {
                                    'description': 'Trumpets',
                                    'scheme': 'CPV',
                                    'id': '37312100',
                                    'uri': 'http://purl.org/cpv/2008/code-37312100'
                                },
                                'deliveryLocation': {
                                    'geometry': {
                                        'type': 'Point',
                                        'coordinates': [51.751944, -1.257778]
                                    },
                                    'gazetteer': {
                                        'scheme': 'GEONAMES',
                                        'identifiers': ['2640729']
                                    },
                                    'description': 'Central Oxford',
                                    'uri': 'http://www.geonames.org/2640729/oxford.html'
                                },
                                'deliveryAddress': {
                                    'postalCode': 'OX1 1BX',
                                    'countryName': 'United Kingdom',
                                    'streetAddress': 'Town Hall, St Aldate`s',
                                    'region': 'Oxfordshire',
                                    'locality': 'Oxford'
                                },
                                'unit': {
                                    'name': 'Items',
                                    'value': {
                                        'currency': 'GBP',
                                        'amount': 10000
                                    }
                                },
                                'quantity': '10'
                            }
                        ],
                'value': {
                    'amount': 1000,
                    'currency': 'NGN'
                },
                'procurementMethod': 'open', 
                'awardCriteria': 'bestProposal',
                'submissionMethod': [
                    'electronicSubmission'
                ],
                'tenderPeriod': {
                    'startDate': '2016-01-31T09:00:00Z',
                    'endDate': '2016-02-15T18:00:00Z'
                },
                'awardPeriod': {
                    'startDate': '2016-04-01T00:00:00Z',
                    'endDate': '2016-06-01T23:59:59Z'
                },
                'enquiryPeriod': {
                    'startDate': '2016-01-31T09:00:00Z',
                    'endDate': '2016-02-15T18:00:00Z'
                },
                'hasEnquiries':'Yes',
                'eligibilityCriteria':'',
                'tenderers':
                [
                    {
                        'identifier':'Supplier Name',
                        'additionalidentifiers':'',
                        'name':'',
                        'address':
                        {
                            'streetAddress':'',
                            'locality':'',
                            'region':'',
                            'postalCode':'',
                            'countryName':''
                        },
                        'contactPoint':
                        {
                            'name':'Title Firstname Lastname',
                            'email':'contac@email.com',
                            'telephone':'',
                            'faxNumber':'',
                            'url':'http://contact.website'
                        }
                    }
                ],
                'numberOfTenderers':'tenderers length',
                'procuringEntity':
                 {
                        'identifier':'Supplier Name',
                        'additionalidentifiers':'',
                        'name':'',
                        'address':
                        {
                            'streetAddress':'',
                            'locality':'',
                            'region':'',
                            'postalCode':'',
                            'countryName':''
                        },
                        'contactPoint':
                        {
                            'name':'Title Firstname Lastname',
                            'email':'contac@email.com',
                            'telephone':'',
                            'faxNumber':'',
                            'url':'http://contact.website'
                        }
                    },
                'documents':
                [
                    {
                        'id':'documentid',
                        'documentType':'',
                        'title':'documentType',
                        'description':'description',
                        'url':'documentLink',
                        'datePublished':'date.now() uploaded',
                        'dateModified':'trackanychange',
                        'format':'mediaType',
                        'language':'documentLanguage'
                    }
                ],
                'milestones':
                [
                    {
                        'id':'milestoneid',
                        'title':'milestone title',
                        'description':'describe milestone',
                        'dueDate':'milestoneDue',
                        'dateModified':'',
                        'status':'', 
                         'documents':
                                [
                                    {
                                        'id':'documentid',
                                        'documentType':'',
                                        'title':'documentType',
                                        'description':'description',
                                        'url':'documentLink',
                                        'datePublished':'date.now() uploaded',
                                        'dateModified':'trackanychange',
                                        'format':'mediaType',
                                        'language':'documentLanguage'
                                    }
                                ],

                    }
                ]
                
            },
            'planning':{
                'budget':{
                    'source':'source',
                    'id':'budgetlineitem',
                    'description':'describe budget source',
                    'amount':100000,
                    'project':'project title',
                    'projectID':'projectid',
                    'uri':'http://to-records-for-this-project'
                },
                'rationale':'why project',
                'documents':
                [
                    {
                        'id':'documentid',
                        'documentType':'',
                        'title':'documentType',
                        'description':'description',
                        'url':'documentLink',
                        'datePublished':'date.now() uploaded',
                        'dateModified':'trackanychange',
                        'format':'mediaType',
                        'language':'documentLanguage'
                    }
                ]
                
            },
            'awards':[{
                'id':'award_id',
                'title':'',
                'description':'',
                'status':'pending',
                'date':'dateNow',
                'value':{
                    'amount':0,
                    'currency':'NGN'
                },
                'suppliers':
                [
                    {
                        'identifier':'Supplier Name',
                        'additionalidentifiers':'',
                        'name':'',
                        'address':
                        {
                            'streetAddress':'',
                            'locality':'',
                            'region':'',
                            'postalCode':'',
                            'countryName':''
                        },
                        'contactPoint':
                        {
                            'name':'Title Firstname Lastname',
                            'email':'contac@email.com',
                            'telephone':'',
                            'faxNumber':'',
                            'url':'http://contact.website'
                        }
                    }
                ],
               
                'items': [
                            {
                                'id': 'item1',
                                'description': 'Ceremonial Trumpets for Oxford Town Hall',
                                'classification': {
                                    'description': 'Trumpets',
                                    'scheme': 'CPV',
                                    'id': '37312100',
                                    'uri': 'http://purl.org/cpv/2008/code-37312100'
                                },
                                'deliveryLocation': {
                                    'geometry': {
                                        'type': 'Point',
                                        'coordinates': [51.751944, -1.257778]
                                    },
                                    'gazetteer': {
                                        'scheme': 'GEONAMES',
                                        'identifiers': ['2640729']
                                    },
                                    'description': 'Central Oxford',
                                    'uri': 'http://www.geonames.org/2640729/oxford.html'
                                },
                                'deliveryAddress': {
                                    'postalCode': 'OX1 1BX',
                                    'countryName': 'United Kingdom',
                                    'streetAddress': 'Town Hall, St Aldate`s',
                                    'region': 'Oxfordshire',
                                    'locality': 'Oxford'
                                },
                                'unit': {
                                    'name': 'Items',
                                    'value': {
                                        'currency': 'GBP',
                                        'amount': 10000
                                    }
                                },
                                'quantity': '10'
                            }
                        ]
            }
                     ],
            'contracts':[{
                'id':'',
                'awardID':'award.id.ocds',
                'title':'',
                'description':'',
                'status':'award', 
                'period': {
                    'startDate': '2016-04-01T00:00:00Z',
                    'endDate': '2016-06-01T23:59:59Z'
                },
                'value': {
                    'amount': 1000,
                    'currency': 'NGN'
                },
                'items': [
                            {
                                'id': 'item1',
                                'description': 'Ceremonial Trumpets for Oxford Town Hall',
                                'classification': {
                                    'description': 'Trumpets',
                                    'scheme': 'CPV',
                                    'id': '37312100',
                                    'uri': 'http://purl.org/cpv/2008/code-37312100'
                                },
                                'deliveryLocation': {
                                    'geometry': {
                                        'type': 'Point',
                                        'coordinates': [51.751944, -1.257778]
                                    },
                                    'gazetteer': {
                                        'scheme': 'GEONAMES',
                                        'identifiers': ['2640729']
                                    },
                                    'description': 'Central Oxford',
                                    'uri': 'http://www.geonames.org/2640729/oxford.html'
                                },
                                'deliveryAddress': {
                                    'postalCode': 'OX1 1BX',
                                    'countryName': 'United Kingdom',
                                    'streetAddress': 'Town Hall, St Aldate`s',
                                    'region': 'Oxfordshire',
                                    'locality': 'Oxford'
                                },
                                'unit': {
                                    'name': 'Items',
                                    'value': {
                                        'currency': 'GBP',
                                        'amount': 10000
                                    }
                                },
                                'quantity': '10'
                            }
                        ],
                'dateSigned':'ISO-DATE',
                 'documents':
                                [
                                    {
                                        'id':'documentid',
                                        'documentType':'',
                                        'title':'documentType',
                                        'description':'description',
                                        'url':'documentLink',
                                        'datePublished':'date.now() uploaded',
                                        'dateModified':'trackanychange',
                                        'format':'mediaType',
                                        'language':'documentLanguage'
                                    }
                                ],
                'implementation':{
                    'transactions':[
                        {
                            'id':'id.transactions',
                            'source':'uri',
                            'date':'date iso',
                            'amount': 
                                        {
                                'amount': 1000,
                                'currency': 'NGN'
                            },
                            'providerOrganization': {
                    'scheme': 'NGN-COH',
                    'id': '09506232',
                    'legalName': 'Open Data Services Co-operative',
                    'uri': 'https://opencorporates.com/companies/gb/09506232'
                },
                            'recieverOrganization': {
                    'scheme': 'NGN-COH',
                    'id': '09506232',
                    'legalName': 'Open Data Services Co-operative',
                    'uri': 'https://opencorporates.com/companies/gb/09506232'
                },
                            'uri':'http://transaction'
                        }
                    ],
                     'milestones':
                [
                    {
                        'id':'milestoneid',
                        'title':'milestone title',
                        'description':'describe milestone',
                        'dueDate':'milestoneDue',
                        'dateModified':'',
                        'status':'', 
                         'documents':
                                [
                                    {
                                        'id':'documentid',
                                        'documentType':'',
                                        'title':'documentType',
                                        'description':'description',
                                        'url':'documentLink',
                                        'datePublished':'date.now() uploaded',
                                        'dateModified':'trackanychange',
                                        'format':'mediaType',
                                        'language':'documentLanguage'
                                    }
                                ],

                    }
                ],
                     'documents':
                                [
                                    {
                                        'id':'documentid',
                                        'documentType':'',
                                        'title':'documentType',
                                        'description':'description',
                                        'url':'documentLink',
                                        'datePublished':'date.now() uploaded',
                                        'dateModified':'trackanychange',
                                        'format':'mediaType',
                                        'language':'documentLanguage'
                                    }
                                ]
                    
                }
                
            }]
        }
        
    ]

                    #releases_dict.append(release_dict)
                    response.append(releases_dict)
                    #response.append({'total':res})

            print json.dumps(response)
#convert into json after converting to dictionary
            return json.dumps(response)

        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))


