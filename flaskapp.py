from flask import Flask, Response, render_template, url_for, jsonify, session, request, flash, redirect, send_from_directory, send_file, make_response
from flask_mail import Message, Mail
import random, datetime, string, os, webbrowser, json, zipfile, requests
from bson import json_util
from flask import Flask, flash, render_template, json, request, url_for, redirect
from werkzeug import generate_password_hash, check_password_hash
from werkzeug import secure_filename
from flask import session
import random

from pymongo import MongoClient
#from datetime import datetime
import datetime


####################################app configurations ########################################################
pageLimit = 20
today = datetime.date.today().strftime("%Y-%m-%d")
app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'
app.config["MAIL_SERVER"] = "mail.nigeriaoc.org"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'app@nigeriaoc.org'
app.config["MAIL_PASSWORD"] = '@nigeria2017'
app.config['UPLOAD_FOLDER'] = '/media/ruth/U/NOCOPO/static/uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'json', 'csv', 'docx', 'xlsx', 'xls', 'doc'])
mail = Mail()
mail.init_app(app)
language="EN"
###############################################################error handlers#####################################################


###########################################################################################################################################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403

@app.errorhandler(410)
def page_pulled(e):
    return render_template("errors/410.html"), 410

##############################################################################################Dashboard#####################################################




################################################################utilities###################################################################################
#####connects to mongo db database and returns Cursor
def connect_db():
    c = MongoClient(host="localhost", port=27017)
    db = c.open_contracts
    return db

db = connect_db()

@app.template_filter('datetime')
def _jinja2_filter_datetime(date):
    if date == "" or date =="null":
        return "null"
    try:
        date = date.split("T")[0]
        formatted = datetime.datetime.strptime(date, "%Y-%m-%d")
    except:
        formatted=None
    return formatted

def js(cursor, ocid=None):

    
    if ocid != None:
        data = list(db.releases.find({"ocid": ocid}))
        for i in data:
            i.pop("_id")
        db.close
        data = jsonify(data)
        try:
            return data.get_data()
        except:
            return "Oops, Something Went Wrong"
    else:
        data = json.dumps(cursor)
        return data


def intervals(end, start):
    if end == "" or end=="null" or start == "null" or start == "" or end==None or start==None:
        return None
    tdelta = end - start
    years = 0;
    months = 0;
    days = 0;

    if tdelta.days >= 365:
        years = round(tdelta.days / 365)
        m = tdelta.days % 365
        if m > 0:
            months = round(m / 30)
            days = m % 30

    elif tdelta.days >= 30 and tdelta.days < 365:
        months = round(tdelta.days / 30)
        days = tdelta.days % 30
    else:
        days = tdelta.days

    interval = [str(years) + " years ", str(months) + " months ", str(days) + " days "];
    diff = ""
    for i in interval:
        if i[0] != "0":
            diff += i
    return diff


def repl(stri,old, new):
    replaces = [")", "(", ".", "&", "/", "'"]
    for i in replaces:
        stri = stri.replace(i, "")
    return stri.replace(old,new)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def getCoords(address):
    api_key = "AIzaSyCSTh76cAoDiRGgW4k1l_NRn7UMvlihdK0"
    api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}'.format(address))
    api_response_dict = api_response.json()

    if api_response_dict['status'] == 'OK':
        latitude = api_response_dict['results'][0]['geometry']['viewport']['northeast']['lat']
        longitude = api_response_dict['results'][0]['geometry']['viewport']['northeast']['lng']
        return [latitude, longitude]


def bubbles(db_data):
    data = []

    for element in db_data:
        if element['planning']['basicdata']['procurementcategory'] and element['planning']['basicdata'][
            'procurementcategory'] != "" and element['contracts']['implementation']['tilldate'] and \
                        element['contracts']['implementation']['tilldate'] != "":
            data.append(
                {"value": int(element['planning']['budget']['amount']['amount']), "name": element['description'],
                 "group": element['planning']['basicdata']['procurementcategory'],
                 "progress": int(element['contracts']['implementation']['tilldate'])})

    return json.dumps(data)


####parses a time and date 'ocid_date'
def parse_datetime(ocid_date):
    if ocid_date == "" or ocid_date == "null":
        return False
        
    if ocid_date:
        ocid_date_no = datetime.datetime.strptime(ocid_date, "%Y-%m-%d")
        return ocid_date_no
    else:
        emptyfield = "null"
        return emptyfield

#####################################uploads##################################

##############################################UPLOADS

# Route that will process the file upload
@app.route('/planningUpload', methods=['POST'])
def upload():
    if session.get('user'):
        # return render_template('userHome.html')

        # Get the name of the uploaded file
        file = request.files['file']
        OCID = request.form['OCID']

        print(OCID)
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            # Move the file from the temporal folder to
            # the upload folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # store filename in mongodb
            query = db.releases.update_one({"ocid": OCID},
                                           {
                                               "$push":
                                                   {
                                                       "planning.documents": (filename)

                                                   }

                                           })

            if query.modified_count is 1:
                # TO REMOVE/REUSE
                # Redirect the user to the uploaded_file route, which
                # will basicaly show on the browser the uploaded file
                # return redirect(url_for('uploaded_file',
                # filename=filename))
                return render_template('myplans.html')

    else:
        return render_template('dashboard/error.html', error='Unauthorized Access')


@app.route('/tenderUpload', methods=['POST'])
def tenderUpload():
    if session.get('user'):
        # return render_template('userHome.html')

        # Get the name of the uploaded file
        file = request.files['file']
        OCID = request.form['OCID']

        print(OCID)
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            # Move the file from the temporal folder to
            # the upload folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # store filename in mongodb
            query = db.releases.update_one({"ocid": OCID},
                                           {
                                               "$push":
                                                   {
                                                       "tender.documents": (filename)

                                                   }

                                           })

            if query.modified_count is 1:
                # TO REMOVE/REUSE
                # Redirect the user to the uploaded_file route, which
                # will basicaly show on the browser the uploaded file
                # return redirect(url_for('uploaded_file',
                # filename=filename))
                return render_template('mytenders.html')

    else:
        return render_template('dashboard/error.html', error='Unauthorized Access')


@app.route('/contractUpload', methods=['POST'])
def contractUpload():
    if session.get('user'):
        # return render_template('userHome.html')

        # Get the name of the uploaded file
        file = request.files['file']
        OCID = request.form['OCID']

        print(OCID)
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            # Move the file from the temporal folder to
            # the upload folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # store filename in mongodb
            query = db.releases.update_one({"ocid": OCID},
                                           {
                                               "$push":
                                                   {
                                                       "contracts.documents": (filename)

                                                   }

                                           })

            if query.modified_count is 1:
                # TO REMOVE/REUSE
                # Redirect the user to the uploaded_file route, which
                # will basicaly show on the browser the uploaded file
                # return redirect(url_for('uploaded_file',
                # filename=filename))
                return render_template('mycontracts.html')

    else:
        return render_template('dashboard/error.html', error='Unauthorized Access')

##########################################end uploads#############################################################

#######################################downloads#####################################################
@app.route('/planDownload', methods=['POST'])
def planDownload():
    directory = os.path.dirname(os.path.abspath(__file__))
    test = os.listdir(directory)

    # delete previously stored zips
    for item in test:
        if item.endswith(".zip"):
            os.remove(os.path.join(directory, item))

    _id = request.form['OCID']
    documents = db.releases.find_one({"ocid": _id})

    # begin downloading new zip
    timestamp = strftime('%Y-%m-%d:%H-%M-%S', gmtime())
    zfname = 'files-' + str(timestamp) + '.zip'
    zf = zipfile.ZipFile(zfname, "w")
    for dirname, subdirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        # zf.write(dirname)
        if documents:
            doc = documents['planning']['documents']
            filename = str(doc[0])
            for documentname in doc:
                print(str(documentname))
                for filename in files:
                    if documentname == filename:
                        zf.write(dirname + filename, filename)
    zf.close()

    return send_from_directory(directory, zfname, as_attachment=True)


# download tender documents
@app.route('/tenderDownload', methods=['POST'])
def tenderDownload():
    directory = os.path.dirname(os.path.abspath(__file__))
    test = os.listdir(directory)

    # delete previously stored zips
    for item in test:
        if item.endswith(".zip"):
            os.remove(os.path.join(directory, item))

    _id = request.form['OCID']
    documents = db.releases.find_one({"ocid": _id})

    # begin downloading new zip
    timestamp = strftime('%Y-%m-%d:%H-%M-%S', gmtime())
    zfname = 'files-' + str(timestamp) + '.zip'
    zf = zipfile.ZipFile(zfname, "w")
    for dirname, subdirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        # zf.write(dirname)
        if documents:

            doc = documents['tender']['documents']
            filename = str(doc[0])
            for documentname in doc:
                print(str(documentname))
                for filename in files:
                    if documentname == filename:
                        zf.write(dirname + filename, filename)
    zf.close()

    return send_from_directory(directory, zfname, as_attachment=True)


# download contract documents
@app.route('/contractDownload', methods=['POST'])
def contractDownload():
    directory = os.path.dirname(os.path.abspath(__file__))
    test = os.listdir(directory)

    # delete previously stored zips
    for item in test:
        if item.endswith(".zip"):
            os.remove(os.path.join(directory, item))

    _id = request.form['OCID']
    documents = db.releases.find_one({"ocid": _id})

    # begin downloading new zip
    timestamp = strftime('%Y-%m-%d:%H-%M-%S', gmtime())
    zfname = 'files-' + str(timestamp) + '.zip'
    zf = zipfile.ZipFile(zfname, "w")
    for dirname, subdirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        # zf.write(dirname)
        if documents:

            doc = documents['contracts']['documents']
            filename = str(doc[0])
            for documentname in doc:
                print(str(documentname))
                for filename in files:
                    if documentname == filename:
                        zf.write(dirname + filename, filename)
    zf.close()

    return send_from_directory(directory, zfname, as_attachment=True)

#################################end downloads#############################################################################

###validates a user is registered and signed in to view page 'pathtofile' and returns
def validate_access(pathtofile, vars=None):
    if session.get('user'):
        return render_template(pathtofile, vars=vars)
    else:
        return render_template('forms/signin.html',
                               error='You must be registered and signed in to view any internal contract details')


###creates a new release data model and returns a json object with empty release data feilds
def create_bpp_data_model(ocid, description, agency, ministry):
    rl = {
        "ocid": ocid,
        "id": "ocds-gyl66f-Example MDA-1",
        "description": description,
        "agencyreference": session["reference"],
        "tag": [
            "contract"
        ],
        "buyer": {
            "identifier": {
                "legalName": agency
            }
        },
        "website": "www.uniben.com",
        "date": "",
        "language": "",
        "tender": {
            "title": description,
            "procuringEntity": {
                "additionalIdentifiers": [
                    {
                        "legalName": ministry
                    }
                ],
                "name": ministry
            },
            "description": description,
            "status": "",
            "advertisementdate": "",
            "advertmedia": "",
            "value": {
                "amount": 0
            },
            "procurementMethod": "",
            "rationale": "",
            "bppletterofobjection": "",
            "awardcriteria": "",
            "awardcriteriadetails": "",
            "submissionmethod": "",
            "submissionmethoddetails": "",
            "hasenquiries": "",
            "enquiryperiod": "",
            "enquiryperiodend": "",
            "haspetition": "",
            "petitionremark": "",
            "eligibilitycriteria": "",
            "numberoftenderers": "",
            "awardstart": "",
            "awardend": "",
            "projtype": "",
            "tenderPeriodstart": "",
            "tenderPeriodend": "",
            "docs": []
            ,
            "milestones": [
                {
                    "status": "On-Going"
                }
            ],
            "actualadvert": "",
            "actualadvertend": "",
            "actualevaluation": "",
            "actualevaluationend": "",
            "actualshortlistapprove": "",
            "actualshortlistapproveend": "",
            "actualshortlistpublish": "",
            "actualproposalinvite": "",
            "actualproposalinviteend": "",
            "actualopeningoftechprop": "",
            "actualevaluationtech": "",
            "actualevaluationtechend": "",
            "actualevaluationtechapprov": "",
            "actualevaluationtechapprovend": "",
            "actualopenfinancialprop": "",
            "actualsubmittechreport": "",
            "actualsubmittechreportend": "",
            "actualnegotiations": "",
            "actualnegotiationsend": "",
            "actualprocuringenteval": "",
            "actualprocuringentevalend": "",
            "actualcertificateobj": "",
            "actualcertificateobjend": "",
            "actualadvertprequal": "",
            "actualadvertprequalend": "",
            "actualprequalopening": "",
            "actualevalpreqalsubm": "",
            "actualevalpreqalsubmend": "",
            "actualprequalapprov": "",
            "actualprequalapprovend": "",
            "actualprequalpublish": "",
            "actualfirstbid": "",
            "actualfirstbidend": "",
            "actualsecondbid": "",
            "actualsecondbidend": "",
            "actualbidinvite": "",
            "actualbidclose": "",
            "actualbidevaluation": "",
            "actualbidevaluationend": "",
            "actualprocuringenteval": "",
            "actualprocuringentevalend": "",
            "actualcertificateobjevalreport": "",
            "actualcertificateobjevalreportend": "",
            "actualfecapproval": "",
            "actualfecapprovalend": "",
            "actualcontractoffer": "",
            "actualcontractofferend": "",
            "actualcontractsignature": "",
            "actualcontractsignatureend": "",
            "actualmobilization": "",
            "actualmobilizationend": "",
            "actualsubmissiondraftrep": "",
            "actualsubmissionfinalrep": "",
            "actualgoodsarrival": "",
            "actualgoodsarrivalend": "",
            "actualsubstantialcomplete": "",
            "actualfinalaccept": "",
            "actualfinalacceptend": ""
        },

        "planning": {
            "identity": {
                "rationale": "",
                "description": "",
                "package": "",
                "lot": ""
            },
            "budget": {
                "amount": {
                    "description": description,
                    "code": "",
                    "source": "",
                    "amount": 0,
                    "estimate": 0
                }
            },
            "basicdata": {
                "procurementcategory": "",
                "contracttype": "",
                "procurementmethod": "",
                "letterofobjection": "",
                "approvalauthority": "",
                "selectionmethod": "",
                "qualification": "",
                "reviewtype": ""
            },
            "scheduling": {
                "requestforproposalstart": "",
                "requestforproposalend": "",
                "proposaldocument": "",
                "plannedadvert": "",
                "plannedadvertend": "",
                "plannedevaluation": "",
                "plannedevaluationend": "",
                "plannedshortlistapprove": "",
                "plannedshortlistapproveend": "",
                "plannedshortlistpublish": "",
                "plannedproposalinvite": "",
                "plannedproposalinviteend": "",
                "plannedopeningoftechprop": "",
                "plannedevaluationtech": "",
                "plannedevaluationtechend": "",
                "plannedevaluationtechapprov": "",
                "plannedevaluationtechapprovend": "",
                "plannedopenfinancialprop": "",
                "plannedsubmittechreport": "",
                "plannedsubmittechreportend": "",
                "plannednegotiations": "",
                "plannednegotiationsend": "",
                "plannedprocuringenteval": "",
                "plannedprocuringentevalend": "",
                "plannedcertificateobj": "",
                "plannedcertificateobjend": "",
                "biddingdocsstart": "",
                "biddingdocsend": "",
                "biddingdocument": "",
                "plannedadvertprequal": "",
                "plannedadvertprequalend": "",
                "plannedprequalopening": "",
                "plannedevalpreqalsubm": "",
                "plannedevalpreqalsubmend": "",
                "plannedprequalapprov": "",
                "plannedprequalapprovend": "",
                "plannedprequalpublish": "",
                "plannedfirstbid": "",
                "plannedfirstbidend": "",
                "plannedsecondbid": "",
                "plannedsecondbidend": "",
                "plannedbidinvite": "",
                "plannedbidclose": "",
                "plannedbidevaluation": "",
                "plannedbidevaluationend": "",
                "plannedprocuringenteval": "",
                "plannedprocuringentevalend": "",
                "plannedcertificateobjevalreport": "",
                "plannedcertificateobjevalreportend": "",
                "plannedfecapproval": "",
                "plannedfecapprovalend": "",
                "plannedcontractoffer": "",
                "plannedcontractofferend": "",
                "plannedcontractsignature": "",
                "plannedcontractsignatureend": "",
                "plannedmobilization": "",
                "plannedmobilizationend": "",
                "plannedsubmissiondraftrep": "",
                "plannedsubmissionfinalrep": "",
                "plannedgoodsarrival": "",
                "plannedgoodsarrivalend": "",
                "plannedsubstantialcomplete": "",
                "plannedfinalaccept": "",
                "plannedfinalacceptend": ""
            },
            "publishplan": "",
            "justification": "",
            "date": "",
            "docs": []
        },
        "awards": [
            {
                "title": description,
                "reference": "",
                "description": description,
                "status": "",
                "bppcertificateofobjectionnumber": "",
                "bppcertificateofobjectiondate": "",
                "procuringentityapprovaldate": "",
                "date": "",
                "value": {
                    "amount": 0
                },
                "suppliers": [
                    {
                        "identifier": {
                            "legalName": "Cursor IP"
                        },
                        "additionalIdentifiers": [
                            {
                                "legalName": "Cursor IP"
                            }
                        ],
                        "name": "Cursor IP",
                        "bppNO": ""
                    }
                ],
                "contractdetails": "",

                "contractPeriod": {
                    "startDate": "13/9/2014",
                    "endDate": "31/12/2015"
                },
                "lowestbidder": "",
                "justification": "",
                "amendment": {
                    "date": "0"
                }
            }
        ],
        "contracts":
            {
                "title": description,
                "reference": "",
                "description": description,
                "status": "",
                "signeddate": "",
                "period": {
                    "startDate": "13/9/2014",
                    "endDate": "31/12/2015"
                },
                "projectlocation": {
                    "streetaddress": "",
                    "city": "",
                    "state": "",
                    "country": "",
                    "coord": [9.0820, 8.6753]
                },
                "docs": []
                ,
                "implementation": {
                    "amountspaid": [],
                    "projectstatus": "",
                    "finalcost": "",
                    "variation": "",
                    "bppapprovalvariation": "",
                    "variationamount": "",
                    "revisedestimatedcontractamount": "",
                    "tilldate": "",
                    "milestones":
                        {
                            "description": "0.7",
                            "status": "On-Going"
                        }

                }
            }

    }
    return rl

##creates an ocds formatted json data model

def past(date):
    if date=="":
        return False
    return date < datetime.datetime.strptime(datetime.date.today().strftime("%d-%m-%y"), '%d-%m-%y').date()


app.add_template_global(js, name='js')
app.add_template_global(past, name='past')
app.add_template_global(intervals, name='interval')
app.add_template_global(repl, name='repl')


###########################################################################################################################################################User Validation fUNCTIONS########################################################


def super_validate(username, password):

    checked = db.admins.find_one({"username": username, "password": password})
    if checked:
        return True
    else:
        return False


# download planning document
########################################helper functions####################################################


###################################################################views#######################################################################'
##displays home page##########################################################################################################
@app.route("/")
def home():
    c = connect_db()
    rel = c.releases.find()
    mapdata = []
    return render_template("index.html", rel=rel, mapdata=json.dumps(mapdata))

@app.route("/bids")
@app.route("/tenders")
def bids():

    bids = db.releases.find()
    return render_template("listings/bids.html", bids=bids)

@app.route("/forcsos")
def forcsos():

    contracts = db.releases.find()
    agency_freq = db.releases.aggregate([{"$group": {"_id": "buyer.identifier.legalName", "count": {"$sum": 1}}}])
    loc_freq = db.releases.aggregate([{"$group": {"_id": "tender.procurementMethod", "count": {"$sum": 1}}}])
    contractors = db.releases.aggregate([{"$group": {"_id": "awards.$.suppliers.name", "count": {"$sum": 1}}}])
    db.close
    return render_template("listings/forcsos.html", contracts=contracts, contractors=contractors, loc=loc_freq)


@app.route("/csos")
def csos():

    csos = db.csos.find()
    db.close
    return render_template("listings/csos.html", csos=csos)


@app.route("/contracts")
def contracts():

    contracts = db.releases.find()
    agency_freq = db.releases.aggregate([{"$group": {"_id": "buyer.identifier.legalName", "count": {"$sum": 1}}}])
    loc_freq = db.releases.aggregate([{"$group": {"_id": "tender.procurementMethod", "count": {"$sum": 1}}}])
    contractors = db.releases.aggregate([{"$group": {"_id": "awards.$.suppliers.name", "count": {"$sum": 1}}}])
    db.close
    return render_template("listings/contracts.html", contracts=contracts, contractors=contractors, loc=loc_freq)


@app.route("/contractors")
def contractors():

    contractors = db.releases.aggregate([{"$group": {
        "_id": {"contractor": "$awards.suppliers.identifier.legalName", "buyer": "$buyer.identifier.legalName"},
        "count": {"$sum": 1},
        "totalamount": {"$sum": "$planning.budget.amount"}}},
                                    {"$group": {"_id": {"contractor": "$_id.contractor","buyer": "$_id.buyer"},
                                                "totals": {
                                                    "$addToSet": {"buyer": "$_id.buyer", "count": "$count",
                                                                  "totalamount": "$totalamount"}},
                                                "count": {"$sum": "$count"}, "totalamount": {"$sum": "$totalamount"}}},
                                    {"$group": {"_id": "$_id.contractor", "buyer": {
                                        "$push": {"buyer": "$_id.buyer", "times": "$count",
                                                  "total": "$totalamount"}}}}, {"$sort": {"buyer.times": -1}}

                                    ])
    db.close

    return render_template("listings/contractors.html", contractors=contractors)



@app.route("/agencies")
def agencies():


    agents= db.releases.aggregate([{"$group": {"_id": {"buyer":"$buyer.identifier.legalName", "contractor":"$awards.suppliers.identifier.legalName"}, "count": {"$sum": 1},
                                                     "totalamount": {"$sum": "$planning.budget.amount"}}},
                                   {"$group":{"_id":{"buyer":"$_id.buyer", "contractor":"$_id.contractor"},"totals":{"$addToSet":{"supplier":"$_id.contractor","count":"$count", "totalamount":"$totalamount"}}, "count":{"$sum":"$count"},"totalamount":{"$sum":"$totalamount"}}},
                                   {"$group":{"_id":"$_id.buyer", "contractors":{"$push":{"contractor":"$_id.contractor", "times":"$count", "total":"$totalamount"}}}}, {"$sort":{"contractors.times":-1}}

                                   ])

    db.close

    return render_template("listings/agencies.html", agents=agents)


##################################### USER AUTHENTICATION

# render the signup page once a request comes to /showSignUp
@app.route('/showSignUp')
def showSignUp():
    return render_template('forms/superuser.html')


# signup method
@app.route('/signUp', methods=['POST'])
def signUp():
    try:
        # read the posted values from the UI
        _ministry = request.form['ministry_name']
        _agencyName = request.form['agency_name']
        _agencyabbrev = request.form['agency_abb']

        _state = request.form['state']
        _city = request.form['agency_locality']
        _street = request.form['agency_street']
        _phonenum = request.form['contactphone']
        _email = request.form['contactemail']
        _fax = request.form['fax']
        _username = request.form['username']
        _password = request.form['password']
        _website = request.form['url']
        country = request.form['country']

        # validate the received values
        if _username and _email and _password and _ministry and _agencyName and _agencyabbrev and _state and _city and _phonenum:
            # All Good, let's call MySQL

            _hashed_password = generate_password_hash(_password)
            # string concatenation - "your %s is in the %s" % (object, location) -- add year and day of the year
            _reference = "%s%s%s" % (
            _agencyabbrev, datetime.date.today().strftime("%Y"), datetime.date.today().strftime("%j"))

            query = db.mdas.update_one(
                {"agencyreference": _reference,
                 "basicdata": {"ministry": _ministry, "agencyname": _agencyName, "agencyabbreviation": _agencyabbrev},
                 "address": {"state": _state, "city": _city, "streetaddress": _street, "country": country},
                 "contact": {"phone": _phonenum, "email": _email, "fax": _fax, "website": _website},
                 "username": _username, "password": _hashed_password},
                {"$set": {"agencyreference": _reference, "basicdata": {"ministry": _ministry, "agencyname": _agencyName,
                                                                       "agencyabbreviation": _agencyabbrev},
                          "address": {"state": _state, "city": _city, "streetaddress": _street, "country": country},
                          "contact": {"phone": _phonenum, "email": _email, "fax": _fax, "website": _website},
                          "username": _username, "password": _hashed_password}},
                upsert=True)

            if query.matched_count is 0:

                message = """Thanks for your registration. For your records:
                            Your User Name is %s and
                            your Agency Reference is %s.""".replace('\n', ' ') % (_username, _reference)
                # return json.dumps({'message':'User created successfully !'})
                flash(message)
                return redirect('/registered')

            else:

                error = 'UserName or Agency Abbreviation already exists. Please review'
                # duplicate where unique
                # return json.dumps({'error':str(data[0])})
                return render_template('dashboard/signup.html', error=error)
        else:
            error = 'Enter the required fields.'
            # check required fields
            # return json.dumps({'html':'<span>Enter the required fields</span>'})
            return render_template('dashboard/signup.html', error=error)
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        db.close


@app.route('/registered')
def registered():
    return render_template('dashboard/registered.html')


# render the signup page once a request comes to /showSignin
@app.route('/showSignin')
def showSignin():
    return render_template('dashboard/signin.html')


# signin method
@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputUsername']
        _password = request.form['inputPassword']

        query = db.mdas.find_one({"username": _username})


        if query and check_password_hash(query['password'], _password):

            # BSON TO STRING
            # populating session with user info
            session['user'] = str(query['_id'])

            session['username'] = query['username']

            session['agencyName'] = query['basicdata']['agencyname']

            session['reference'] = query['agencyreference']

            flash('You were successfully logged in')
            return redirect('/userHome')
        else:
            return render_template('dashboard/signin.html', error='Wrong UserName or Password.')


    except Exception as e:
        return render_template('dashboard/signin.html', error=str(e))
    finally:
        db.close


#user dashboard on successful login with user id for session taken from login method
@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('dashboard/userHome.html')
    else:
        return render_template('dashboard/error.html',error = 'Unauthorized Access')



@app.route("/agency_registration")
def agency_registration():
    return render_template("forms/superuser.html")


@app.route("/superuser", methods=['GET', 'POST'])
def superuser():
    username = request.form['superusername']
    password = request.form['password']

    if username and password and super_validate(username, password):
        return render_template("dashboard/signup.html")
    else:
        return render_template("forms/superuser.html", error="Please fill in the correct details")
##################################### END OF USER AUTHENTICATION





@app.route("/contact")
def contact():
    return(render_template("forms/contact.html"))


@app.route("/messagefrom/<page>", methods=['GET', 'POST'])
def messagefrom(page):
    if request.method == 'POST':
        firstname = request.form.get('firstname', '')
        lastname = request.form.get('lastname','')
        organization = request.form.get('organization','')
        email = request.form.get('email','')
        phone = str(request.form.get('phone',''))
        subject = request.form.get('subject','').upper()
        message = request.form.get('message','')

        if message:

            msg = Message(message, sender='app@nigeriaoc.org', recipients=['app@nigeriaoc.org', 'eneyibabe@gmail.com'])
            msg.body = """
                  From: %s \n Email: <%s>\n To: The Public Bureau of Procurement\n Subject: %s \n\n Message \n %s\n\n
                    Contact back Phone on : %s or by email on %s
                  """ % (firstname + " " + lastname, email, subject, message, phone, email)
            mail.send(msg)
            flash("Your Enquiry has been sent. A BPP staff would be in contact with you Shortly")
            return redirect(url_for(page))
        else:
            flash("You must fill in a message to send an enquiry")
            return redirect(url_for('contact'))
    return redirect(url_for(page))


##3DISPLAYS BPP process page
@app.route("/bppprocess")
def bppprocess():
    return render_template("displays/process.html")



###########################################################################################################################################################API########################################################
@app.route("/open_api")
@app.route("/overview")
def overview():

    contracts = db.releases.find()
    db.close
    return render_template("reports/overview.html", contracts=contracts)


        
@app.route("/release/<ocid>",methods=['GET', 'POST'])
def downloadocid(ocid):

    todays_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    matches = list(db.releases.find({"ocid":ocid}))
    for i in matches:
        i.pop("_id")
    db.close
    matches = {
        "uri":"http:nigeriaoc.org/releases/"+ocid, 
        "publishedDate":todays_date,
        "publisher":
            {"scheme":"NGA-COH",
        "name":"Public Bureau of Procurement",
        "uri":"http://www.bpp.gov.ng"
                
            },
        "license":"https://opendatacommons.org/licenses/pddl/1.0/",
        "publicationPolicy":"https://github.co/open-contracting/sample-data/",
        "releases":matches
        }
    
    return jsonify(matches)
    

@app.route("/downloadSelected", methods=['GET', 'POST'])
def downloadSelected():
    data = request.form.getlist('checks')
    format = request.form.get('options','')
    filename = 'releases' + ''.join([random.choice("0123455boleandgroundnutnagodennoshedadaniwazobia") for i in range(0, 5)])
    todays_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    if format == 'csv' or format == 'allcsv':
        filename = filename+".csv"
        file_loc = "/home/ubuntu/flaskapp/static/data/final1.csv"
        with open(file_loc, "r") as ff:
            lines = ff.read().decode('utf-8',"replace")
        ff.close()

        if format == 'allcsv':
            response = make_response(lines.encode("utf-8").strip())
            response.headers['Content-Disposition'] = 'attachment; filename=' + filename
        else:
            rows = [i for i in lines.split("\n")]
            cells = [i.split(",") for i in rows]
            matches = rows[0] + "\n" + '\n'.join([s for s in rows if any(ocid in s for ocid in data)])
            response = make_response(matches.encode("utf-8").strip())
            response.headers['Content-Disposition'] = 'attachment; filename=' + filename
        return response
        
    else:

        if format == 'alljson' or (format == '' and len(data)==0):
            
            data1 = list(db.releases.find())
        elif format == '' and len(data)==0:
            return jsonify({})
        else:
            data1 = list(db.releases.find({'ocid': {'$in': data}}))
            
        for i in data1:
            i.pop("_id")
        db.close

        matches = {
            "uri": "http:nigeriaoc.org/open_api",
            "publishedDate": todays_date,
            "publisher":
                {"scheme": "NGA-COH",
                 "name": "Public Bureau of Procurement",
                 "uri": "http://www.bpp.gov.ng"

                 },
            "license": "https://opendatacommons.org/licenses/pddl/1.0/",
            "publicationPolicy": "https://github.co/open-contracting/sample-data/",
            "releases": data1
        }
        return jsonify(matches)

		
############################################################################################################


################################### RELEASE


# render release form
@app.route('/showNewRelease')
def showNewRelease():
    return render_template('dashboard/release.html')


# add release method
@app.route('/addRelease', methods=['POST'])
def addRelease():
    try:

        if session.get('user'):

            _website = request.form['url']
            _releasetag = request.form['tag']
            _description = request.form['description']

            # validate the received values
            if _releasetag and _description:
                # All Good, let's call MySQL

                reference = session.get('reference')
                ocds = 'OCDS'
                _releaseID = "%s-%s-%s-%s" % (
                ocds, datetime.date.today().strftime("%Y"), reference, strftime("%H-%M-%S"))
                today = datetime.date.today().strftime('%Y-%m-%d')
                username = session.get('username')

                _agencyname = session.get('agencyName')
                # string concatenation - "your %s is in the %s" % (object, location)
                query = db.releases.update_one({
                    "ocid": _releaseID,
                    "id": _releaseID,
                    "description": _description,
                    "tag": [
                        _releasetag
                    ],
                    "buyer": {
                        "identifier": {
                            "id": _releaseID,
                            "name": _agencyname,
                            "legalName": _agencyname,
                            "language": language
                        }
                    },
                    "website": _website,
                    "initiationType": '',
                    "date": datetime.datetime.strptime(today, "%Y-%m-%d"),
                    "language": language}
                    ,
                    {"$set": {
                        "ocid": _releaseID,
                        "id": _releaseID,
                        "description": _description,
                        "tag": [
                            _releasetag
                        ],
                        "buyer": {
                            "identifier": {
                                "id": _releaseID,
                                "name": _agencyname,
                                "legalName": _agencyname,
                                "language": language
                            }
                        },
                        "website": _website,
                        "initiationType": '',
                        "date": datetime.datetime.strptime(today, "%Y-%m-%d"),
                        "language": language}
                    }
                    ,
                    upsert=True)

                if query.matched_count is 0:

                    message = """Thank you %s for your creating a new project release. For your records:
                            The OCID / Release Identification Number is %s and
                            your Agency Reference is %s.""".replace('\n', ' ') % (username, _releaseID, reference)
                    # return json.dumps({'message':'User created successfully !'})

                    flash(message)
                    return redirect('/userHome')

                else:
                    # duplicate where unique
                    # return json.dumps({'error':str(data[0])})
                    return render_template('dashboard/release.html', error='Please review form entry')
            else:
                # check required fields
                # return json.dumps({'html':'<span>Enter the required fields</span>'})
                return render_template('dashboard/release.html',
                                       error='Enter project description and choose a release tag/stage.')
        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:

        db.close





        #############################################DATA FETCHING METHODS


################################### START OF RELEASE MODAL
# retrieve release method
@app.route('/getRelease', methods=['POST'])
def getRelease():
    try:
        if session.get('user'):

            _user = session.get('user')

            _agencyName = session.get('agencyName')

            _offset = int(request.form['offset'])
            _limit = pageLimit

            releases = db.releases.find({"buyer.identifier.legalName": _agencyName}).sort([('_id', -1)]).skip(
                _offset).limit(_limit)
            # for rel in releases:
            #    print(rel['releases'])
            #    for inrel in rel['releases']:
            #       print(inrel['ocid'])

            # skip 5, limit 5

            res = db.releases.find({"buyer.identifier.legalName": _agencyName}).count()
            # print(res)



            response = []
            releases_dict = []

            # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON
            for release in releases:
                d = release['date']
                dString = d.strftime("%Y-%m-%d")

                release_dict = {
                    'OCID': release['ocid'],
                    'Project_Description': release['description'],
                    'Release_Tag': release['tag'],

                    'Published_Date': dString}
                releases_dict.append(release_dict)
                response.append(releases_dict)
                response.append({'total': res})

            print(json.dumps(response))
            # convert into json after converting to dictionary
            return json.dumps(response)





        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('dashboard/error.html', error=str(e))


# get particular release information
@app.route('/getReleaseById', methods=['POST'])
def getReleaseById():
    try:
        if session.get('user'):

            _id = request.form['id']

            # pymongo projection - fields
            releases = db.releases.find_one({"ocid": _id})

            # for rel in releases['releases']:
            # print(rel['tag'][0])


            response = []
            releases_dict = []

            for rel in releases:
                release_dict = {
                    'Description': rel['description'],
                    'Tag': rel['tag'][0],
                    'Website': rel['website']
                }
                releases_dict.append(release_dict)
                response.append(releases_dict)

            print(json.dumps(response))

            # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON

            return json.dumps(response)
        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('dashboard/error.html', error=str(e))


# update release
@app.route('/updateRelease', methods=['POST'])
def updateRelease():
    try:
        if session.get('user'):
            _website = request.form['website']
            _description = request.form['description']
            _release_id = request.form['id']
            _tag = request.form['tag']

            # print(_release_id+" --------")



            #####TO DO
            ###THIS SHOULD UPDATE ALL TAGS IN ALL STAGES

            query = db.releases.update_one({"ocid": _release_id},
                                           {
                                               "$set":
                                                   {"tag.0": _tag,
                                                    "description": _description,
                                                    "website": _website
                                                    }

                                           })

            if query.modified_count is 1:

                return json.dumps({'status': 'OK'})
            else:
                return json.dumps({'status': 'ERROR'})
    except Exception as e:
        return json.dumps({'status': 'Unauthorized access'})
    finally:
        db.close


# delete release
@app.route('/deleteRelease', methods=['POST'])
def deleteRelease():
    try:

        if session.get('user'):

            _release_id = request.form['id']

            result = db.releases.delete_one({"ocid": _release_id})

            if result.deleted_count is 1:
                return json.dumps({'status': 'OK'})
            else:
                return json.dumps({'status': 'An Error occured'})
        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')
    except Exception as e:
        return json.dumps({'status': str(e)})
    finally:
        db.close


################################### END OF RELEASE MODAL

################################### PLAN


# render planning form
@app.route('/showNewPlan')
def showNewPlan():
    return render_template('dashboard/planning.html')


# render plan view
@app.route('/showSavedPlan')
def showSavedPlan():
    if session.get('user'):
        return render_template('dashboard/myplans.html')
    else:
        return render_template('dashboard/error.html', error='Unauthorized Access')


# add a new plan
@app.route('/addPlan', methods=['POST'])
def addPlan():
    # preqadvertstart=request.form.get('preqadvertstart','')
    # print preqadvertstart

    try:

        if session.get('user'):

            ocid = request.form.get('ocid', '')
            rationale = request.form.get('rationale', '')
            projdesc = request.form.get('projdesc', '')
            packagenum = request.form.get('packagenum', '')
            lot = int(request.form['lot'])
            projtype = request.form.get('projtype', '')
            contrtype = request.form.get('contrtype', '')

            procmethod = request.form.get('procmethod', '')
            letterofnoobj = request.form.get('letterofnoobj', '')
            appauthority = request.form.get('appauthority', '')
            selecmethod = request.form.get('selecmethod', '')
            Qualification = request.form.get('Qualification', '')
            Review = request.form.get('Review', '')
            prepbymdastart = request.form.get('prepbymdastart', '')
            prepbymdaend = request.form.get('prepbymdaend', '')
            advertstart = request.form.get('advertstart', '')
            advertend = request.form.get('advertend', '')
            leadbefliststart = request.form.get('leadbefliststart', '')
            leadbeflistend = request.form.get('leadbeflistend', '')
            mdalistapprovestart = request.form.get('mdalistapprovestart', '')
            mdalistapproveend = request.form.get('mdalistapproveend', '')
            shortlistsubmission = request.form.get('shortlistsubmission', '')
            propinvitestart = request.form.get('propinvitestart', '')
            propinviteend = request.form.get('propinviteend', '')
            techpropopen = request.form.get('techpropopen', '')
            subtechEvreportstart = request.form.get('subtechEvreportstart', '')
            subtechEvreportend = request.form.get('subtechEvreportend', '')
            mdaapptechEvreportstart = request.form.get('mdaapptechEvreportstart', '')
            mdaapptechEvreportend = request.form.get('mdaapptechEvreportend', '')
            Openingfinancialpropstart = request.form.get('Openingfinancialpropstart', '')
            evalfinproposalst = request.form.get('submissionevareportstart', '')
            evalfinproposalend = request.form.get('submissionevareportend', '')
            Negotiationsstart = request.form.get('Negotiationsstart', '')
            Negotiationsend = request.form.get('Negotiationsend', '')
            Negotiationappobjectstart = request.form.get('Negotiationappobjectstart', '')
            Negotiationappobjectstartend = request.form.get('Negotiationappobjectstartend', '')
            planndcertnoobjstart = request.form.get('planndcertnoobjstart', '')
            planndcertnoobjend = request.form.get('planndcertnoobjend', '')
            biddocstart = request.form.get('biddocstart', '')
            biddocend = request.form.get('biddocend', '')

            preqadvertstart = request.form.get('preqadvertstart', '')
            preqadvertend = request.form.get('preqadvertend', '')
            Prequalificationopen = request.form.get('Prequalificationopen', '')
            Prequalificationstart = request.form.get('Prequalificationstart', '')
            Prequalificationend = request.form.get('Prequalificationend', '')
            Prequalificationappobjectstart = request.form.get('Prequalificationappobjectstart', '')
            Prequalificationappobjectend = request.form.get('Prequalificationappobjectend', '')
            Prequalificationpubl = request.form.get('Prequalificationpubl', '')
            firstbidstart = request.form.get('firstbidstart', '')
            firstbidend = request.form.get('firstbidend', '')
            secondbidstart = request.form.get('secondbidstart', '')
            secondbidend = request.form.get('secondbidend', '')
            bidinvite = request.form.get('bidinvite', '')
            bidclose = request.form.get('bidclose', '')
            bidevalrepstart = request.form.get('bidevalrepstart', '')
            bidevalrepend = request.form.get('bidevalrepend', '')
            bidevalMDAstart = request.form.get('bidevalMDAstart', '')
            bidevalMDAend = request.form.get('bidevalMDAend', '')
            certnoobjectstart = request.form.get('certnoobjectstart', '')
            certnoobjectend = request.form.get('certnoobjectend', '')
            fecapprovestart = request.form.get('fecapprovestart', '')
            fecapproveend = request.form.get('fecapproveend', '')
            controfferstart = request.form.get('controfferstart', '')
            controfferend = request.form.get('controfferend', '')
            contrsignstart = request.form.get('contrsignstart', '')
            contrsignend = request.form.get('contrsignend', '')
            Mobilizationstart = request.form.get('Mobilizationstart', '')
            Mobilizationend = request.form.get('Mobilizationend', '')
            draftreptstart = request.form.get('draftreptstart', '')
            finalreptstart = request.form.get('finalreptstart', '')
            arrivalgoodsstart = request.form.get('arrivalgoodsstart', '')
            arrivalgoodsend = request.form.get('arrivalgoodsend', '')
            substcomplend = request.form.get('substcomplend', '')
            finalacceptstart = request.form.get('finalacceptstart', '')
            finalacceptend = request.form.get('finalacceptend', '')

            Publishplanornot = request.form.get('Publishplanornot', '')
            plsjustify = request.form.get('plsjustify', '')

            budgsource = request.form.get('budgsource', '')
            Budgetcode = request.form.get('Budgetcode', '')
            Budgetdesc = request.form.get('Budgetdesc', '')
            Budget = int(request.form.get('Budget', ''))
            estimatedamt = int(request.form.get('estimatedamt', ''))

            query = db.releases.find_one({"ocid": ocid})

            if ocid and query:

                # validate ocid

                # check mandatory fields / basic data not null

                if rationale and projdesc and projtype and Budget and estimatedamt and Budgetcode and Publishplanornot:

                    query = db.releases.update_one({"ocid": ocid},
                                                   {
                                                       "$set":

                                                           {"planning.identity.rationale": rationale,
                                                            "planning.identity.description": projdesc,
                                                            "planning.identity.package": packagenum,
                                                            "planning.identity.lot": lot,

                                                            "planning.budget.project": projdesc,
                                                            "planning.budget.description": projdesc,

                                                            "planning.budget.id": ocid,
                                                            "planning.budget.value.currency": 'NGN',

                                                            "planning.budget.value.description": Budgetdesc,
                                                            "planning.budget.value.code": Budgetcode,
                                                            "planning.budget.value.source": budgsource,
                                                            "planning.budget.value.amount": Budget,
                                                            "planning.budget.value.estimate": estimatedamt,

                                                            "planning.basicdata.procurementcategory": projtype,
                                                            "planning.basicdata.contracttype": contrtype,
                                                            "planning.basicdata.procurementmethod": procmethod,
                                                            "planning.basicdata.letterofobjection": letterofnoobj,
                                                            "planning.basicdata.approvalauthority": appauthority,
                                                            "planning.basicdata.selectionmethod": selecmethod,
                                                            "planning.basicdata.qualification": Qualification,
                                                            "planning.basicdata.reviewtype": Review,
                                                            "planning.scheduling.requestforproposalstart": parse_datetime(
                                                                prepbymdastart),
                                                            "planning.scheduling.requestforproposalend": parse_datetime(
                                                                prepbymdaend),

                                                            "planning.scheduling.plannedadvert": parse_datetime(
                                                                advertstart),
                                                            "planning.scheduling.plannedadvertend": parse_datetime(
                                                                advertend),
                                                            "planning.scheduling.plannedevaluation": parse_datetime(
                                                                leadbefliststart),
                                                            "planning.scheduling.plannedevaluationend": parse_datetime(
                                                                leadbeflistend),
                                                            "planning.scheduling.plannedshortlistapprove": parse_datetime(
                                                                mdalistapprovestart),
                                                            "planning.scheduling.plannedshortlistapproveend": parse_datetime(
                                                                mdalistapproveend),
                                                            "planning.scheduling.plannedshortlistpublish": parse_datetime(
                                                                shortlistsubmission),
                                                            "planning.scheduling.plannedproposalinvite": parse_datetime(
                                                                propinvitestart),
                                                            "planning.scheduling.plannedproposalinviteend": parse_datetime(
                                                                propinviteend),
                                                            "planning.scheduling.plannedopeningoftechprop": parse_datetime(
                                                                techpropopen),
                                                            "planning.scheduling.plannedevaluationtech": parse_datetime(
                                                                subtechEvreportstart),
                                                            "planning.scheduling.plannedevaluationtechend": parse_datetime(
                                                                subtechEvreportend),
                                                            "planning.scheduling.plannedevaluationtechapprov": parse_datetime(
                                                                mdaapptechEvreportstart),
                                                            "planning.scheduling.plannedevaluationtechapprovend": parse_datetime(
                                                                mdaapptechEvreportend),
                                                            "planning.scheduling.plannedopenfinancialprop": parse_datetime(
                                                                Openingfinancialpropstart),
                                                            "planning.scheduling.plannedsubmittechreport": parse_datetime(
                                                                evalfinproposalst),
                                                            "planning.scheduling.plannedsubmittechreportend": parse_datetime(
                                                                evalfinproposalend),
                                                            "planning.scheduling.plannednegotiations": parse_datetime(
                                                                Negotiationsstart),
                                                            "planning.scheduling.plannednegotiationsend": parse_datetime(
                                                                Negotiationsend),
                                                            "planning.scheduling.plannedprocuringenteval": parse_datetime(
                                                                Negotiationappobjectstart),
                                                            "planning.scheduling.plannedprocuringentevalend": parse_datetime(
                                                                Negotiationappobjectstartend),
                                                            "planning.scheduling.plannedcertificateobj": parse_datetime(
                                                                planndcertnoobjstart),
                                                            "planning.scheduling.plannedcertificateobjend": parse_datetime(
                                                                planndcertnoobjend),
                                                            "planning.scheduling.biddingdocsstart": parse_datetime(
                                                                biddocstart),
                                                            "planning.scheduling.biddingdocsend": parse_datetime(
                                                                biddocend),

                                                            "planning.scheduling.biddingdocument": " ",

                                                            "planning.scheduling.plannedadvertprequal": parse_datetime(
                                                                preqadvertstart),
                                                            "planning.scheduling.plannedadvertprequalend": parse_datetime(
                                                                preqadvertend),
                                                            "planning.scheduling.plannedprequalopening": parse_datetime(
                                                                Prequalificationopen),
                                                            "planning.scheduling.plannedevalpreqalsubm": parse_datetime(
                                                                Prequalificationstart),
                                                            "planning.scheduling.plannedevalpreqalsubmend": parse_datetime(
                                                                Prequalificationend),
                                                            "planning.scheduling.plannedprequalapprov": parse_datetime(
                                                                Prequalificationappobjectstart),
                                                            "planning.scheduling.plannedprequalapprovend": parse_datetime(
                                                                Prequalificationappobjectend),
                                                            "planning.scheduling.plannedprequalpublish": parse_datetime(
                                                                Prequalificationpubl),
                                                            "planning.scheduling.plannedfirstbid": parse_datetime(
                                                                firstbidstart),
                                                            "planning.scheduling.plannedfirstbidend": parse_datetime(
                                                                firstbidend),
                                                            "planning.scheduling.plannedsecondbid": parse_datetime(
                                                                secondbidstart),
                                                            "planning.scheduling.plannedsecondbidend": parse_datetime(
                                                                secondbidend),
                                                            "planning.scheduling.plannedbidinvite": parse_datetime(
                                                                bidinvite),
                                                            "planning.scheduling.plannedbidclose": parse_datetime(
                                                                bidclose),
                                                            "planning.scheduling.plannedbidevaluation": parse_datetime(
                                                                bidevalrepstart),
                                                            "planning.scheduling.plannedbidevaluationend": parse_datetime(
                                                                bidevalrepend),
                                                            "planning.scheduling.plannedprocuringenteval": parse_datetime(
                                                                bidevalMDAstart),
                                                            "planning.scheduling.plannedprocuringentevalend": parse_datetime(
                                                                bidevalMDAend),
                                                            "planning.scheduling.plannedcertificateobjevalreport": parse_datetime(
                                                                certnoobjectstart),
                                                            "planning.scheduling.plannedcertificateobjevalreportend": parse_datetime(
                                                                certnoobjectend),
                                                            "planning.scheduling.plannedfecapproval": parse_datetime(
                                                                fecapprovestart),
                                                            "planning.scheduling.plannedfecapproval": parse_datetime(
                                                                fecapproveend),
                                                            "planning.scheduling.plannedcontractoffer": parse_datetime(
                                                                controfferstart),
                                                            "planning.scheduling.plannedcontractofferend": parse_datetime(
                                                                controfferend),
                                                            "planning.scheduling.plannedcontractsignature": parse_datetime(
                                                                contrsignstart),
                                                            "planning.scheduling.plannedcontractsignatureend": parse_datetime(
                                                                contrsignend),
                                                            "planning.scheduling.plannedmobilization": parse_datetime(
                                                                Mobilizationstart),
                                                            "planning.scheduling.plannedmobilizationend": parse_datetime(
                                                                Mobilizationend),
                                                            "planning.scheduling.plannedsubmissiondraftrep": parse_datetime(
                                                                draftreptstart),
                                                            "planning.scheduling.plannedsubmissionfinalrep": parse_datetime(
                                                                finalreptstart),
                                                            "planning.scheduling.plannedgoodsarrival": parse_datetime(
                                                                arrivalgoodsstart),
                                                            "planning.scheduling.plannedgoodsarrivalend": parse_datetime(
                                                                arrivalgoodsend),
                                                            "planning.scheduling.plannedsubstantialcomplete": parse_datetime(
                                                                substcomplend),
                                                            "planning.scheduling.plannedfinalaccept": parse_datetime(
                                                                finalacceptstart),
                                                            "planning.scheduling.plannedfinalacceptend": parse_datetime(
                                                                finalacceptend),
                                                            "planning.publishplan": Publishplanornot,
                                                            "planning.justification": plsjustify,
                                                            "planning.date": datetime.datetime.strptime(today,
                                                                                                        "%Y-%m-%d")
                                                            }

                                                   })

                    if query.modified_count is 1:

                        message = """Your Plan with OCID '%s' has been saved.""".replace('\n', ' ') % (ocid)
                        # return json.dumps({'message':'User created successfully !'})
                        flash(message)
                        return render_template('dashboard/planning.html')
                    else:
                        # duplicate where unique
                        # return json.dumps({'error':str(data[0])})
                        return render_template('dashboard/planning.html',
                                               error='Please review form entry, one or more entries might be in the wrong format')
                else:
                    # check required fields
                    # return json.dumps({'html':'<span>Enter the required fields</span>'})
                    return render_template('dashboard/planning.html', error='Enter the correct values in the mandatory fields')
            else:
                return render_template('dashboard/planning.html',
                                       error='OCID/Project is invalid or does not exist. Create New Release or Open Contracting Process')



        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')
    except Exception as e:
        # return render_template('dashboard/planning.html,error = 'A Plan already exists with that OCID or OCID is invalid')
        return json.dumps({'error': str(e)})
    finally:
        db.close


################################### START OF PLAN MODAL

# retrieve plan method
@app.route('/getPlans', methods=['POST'])
def getPlans():
    try:
        if session.get('user'):

            _user = session.get('user')

            _agencyName = session.get('agencyName')

            _offset = int(request.form['offset'])
            _limit = pageLimit

            releases = db.releases.find({"buyer.identifier.legalName": _agencyName}).sort([('_id', -1)]).skip(
                _offset).limit(_limit)

            res = db.releases.find({"buyer.identifier.legalName": _agencyName}).count()
            # print(res)



            response = []
            releases_dict = []

            # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON
            for release in releases:
                d = release['planning']['date']
                dString = d.strftime("%Y-%m-%d")

                release_dict = {
                    'OCID': release['ocid'],
                    'planning_Description': release['planning']['identity']['description'],

                    'planning_Package_Number': release['planning']['identity']['package'],
                    'planning_Procurement_category': release['planning']['basicdata']['procurementcategory'],
                    'planning_Contract_type': release['planning']['basicdata']['contracttype'],

                    'plan_date': dString}

                releases_dict.append(release_dict)
                response.append(releases_dict)
                response.append({'total': res})

            print(json.dumps(response))
            # convert into json after converting to dictionary
            return json.dumps(response)





        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('dashboard/error.html', error=str(e))


################################### END OF PLAN MODAL


################################### TENDER


# render tender form
@app.route('/showNewTender')
def showNewTender():
    return render_template('dashboard/tender.html')


# render tender view
@app.route('/showSavedTender')
def showSavedTender():
    if session.get('user'):
        return render_template('dashboard/mytenders.html')
    else:
        return render_template('dashboard/error.html', error='Unauthorized Access')


# add Tender
@app.route("/initiate", methods=['POST'])
def createNewTender():
    try:

        if session.get('user'):

            ocid = request.form.get('ocid', '')
            title = request.form.get('title', '')
            projdesc = request.form.get('projdesc', '')
            status = request.form.get('status', '')
            advertdate = request.form.get('advertdate', '')
            media = request.form.get('media', '')
            minvalue = int(request.form.get('minvalue', ''))
            procmethod = request.form.get('procmethod', '')
            rationale = request.form.get('rationale', '')
            bppletterofnoobj = request.form.get('bppletterofnoobj', '')
            awardCriteria = request.form.get('awardCriteria', '')
            awardCriteriadet = request.form.get('awardCriteriadet', '')
            tenderstart = request.form.get('tenderstart', '')
            tenderend = request.form.get('tenderend', '')
            submethod = request.form.get('submethod', '')
            submethoddet = request.form.get('submethoddet', '')
            hasenq = request.form.get('hasenq', '')
            enqperdstart = request.form.get('enqperdstart', '')
            enqperdstartend = request.form.get('enqperdstartend', '')
            haspet = request.form.get('haspet', '')
            petitionremark = request.form.get('petitionremark', '')
            eligcrit = request.form.get('eligcrit', '')
            nooftenderers = int(request.form.get('nooftenderers', ''))
            awardstart = request.form.get('awardstart', '')
            awardend = request.form.get('awardend', '')

            projtype = request.form.get('projtype', '')

            advertstart = request.form.get('advertstart', '')
            advertend = request.form.get('advertend', '')
            leadbefliststart = request.form.get('leadbefliststart', '')
            leadbeflistend = request.form.get('leadbeflistend', '')
            mdalistapprovestart = request.form.get('mdalistapprovestart', '')
            mdalistapproveend = request.form.get('mdalistapproveend', '')
            shortlistsubmission = request.form.get('shortlistsubmission', '')
            propinvitestart = request.form.get('propinvitestart', '')
            propinviteend = request.form.get('propinviteend', '')
            techpropopen = request.form.get('techpropopen', '')
            subtechEvreportstart = request.form.get('subtechEvreportstart', '')
            subtechEvreportend = request.form.get('subtechEvreportend', '')
            mdaapptechEvreportstart = request.form.get('mdaapptechEvreportstart', '')
            mdaapptechEvreportend = request.form.get('mdaapptechEvreportend', '')
            Openingfinancialpropstart = request.form.get('Openingfinancialpropstart', '')
            submissionevareportstart = request.form.get('submissionevareportstart', '')
            submissionevareportend = request.form.get('submissionevareportend', '')
            Negotiationsstart = request.form.get('Negotiationsstart', '')
            Negotiationsend = request.form.get('Negotiationsend', '')
            Negotiationappobjectstart = request.form.get('Negotiationappobjectstart', '')
            Negotiationappobjectstartend = request.form.get('Negotiationappobjectstartend', '')
            planndcertnoobjstart = request.form.get('planndcertnoobjstart', '')
            planndcertnoobjend = request.form.get('planndcertnoobjend', '')
            preqadvertstart = request.form.get('preqadvertstart', '')
            preqadvertend = request.form.get('preqadvertend', '')
            Prequalificationopen = request.form.get('Prequalificationopen', '')
            Prequalificationstart = request.form.get('Prequalificationstart', '')
            Prequalificationend = request.form.get('Prequalificationend', '')
            Prequalificationappobjectstart = request.form.get('Prequalificationappobjectstart', '')
            Prequalificationappobjectend = request.form.get('Prequalificationappobjectend', '')
            Prequalificationpubl = request.form.get('Prequalificationpubl', '')
            firstbidstart = request.form.get('firstbidstart', '')
            firstbidend = request.form.get('firstbidend', '')
            secondbidstart = request.form.get('secondbidstart', '')
            secondbidend = request.form.get('secondbidend', '')
            bidinvite = request.form.get('bidinvite', '')
            bidclose = request.form.get('bidclose', '')
            bidevalrepstart = request.form.get('bidevalrepstart', '')
            bidevalrepend = request.form.get('bidevalrepend', '')
            bidevalMDAstart = request.form.get('bidevalMDAstart', '')
            bidevalMDAend = request.form.get('bidevalMDAend', '')
            certnoobjectstart = request.form.get('certnoobjectstart', '')
            certnoobjectend = request.form.get('certnoobjectend', '')
            fecapprovestart = request.form.get('fecapprovestart', '')
            fecapproveend = request.form.get('fecapproveend', '')
            controfferstart = request.form.get('controfferstart', '')
            controfferend = request.form.get('controfferend', '')
            contrsignstart = request.form.get('contrsignstart', '')
            contrsignend = request.form.get('contrsignend', '')
            Mobilizationstart = request.form.get('Mobilizationstart', '')
            Mobilizationend = request.form.get('Mobilizationend', '')
            draftreptstart = request.form.get('draftreptstart', '')
            finalreptstart = request.form.get('finalreptstart', '')
            arrivalgoodsstart = request.form.get('arrivalgoodsstart', '')
            arrivalgoodsend = request.form.get('arrivalgoodsend', '')
            substcomplend = request.form.get('substcomplend', '')
            finalacceptstart = request.form.get('finalacceptstart', '')
            finalacceptend = request.form.get('finalacceptend', '')

            query = db.releases.find_one({"ocid": ocid})

            if ocid and query:

                # check ocid not null!

                if title and projdesc and projtype and nooftenderers and status and advertdate and minvalue:

                    query = db.releases.update_one({"ocid": ocid},
                                                   {
                                                       "$set":

                                                           {

                                                               "tender.title": title,
                                                               "tender.procuringEntity.additionalIdentifiers.0.legalName": session.get(
                                                                   'agencyName'),
                                                               "tender.procuringEntity.additionalIdentifiers.0.id": '',
                                                               "tender.procuringEntity.additionalIdentifiers.0.scheme": '',
                                                               "tender.procuringEntity.additionalIdentifiers.contactPoint": '',
                                                               "tender.procuringEntity.identifier.scheme": '',
                                                               "tender.procuringEntity.identifier.id": '',
                                                               "tender.procuringEntity.identifier.legalName": session.get(
                                                                   'agencyName'),
                                                               "tender.procuringEntity.identifier.address.countryName": 'Nigeria',

                                                               "tender.description": projdesc,
                                                               "tender.status": status,
                                                               "tender.advertisementdate": parse_datetime(advertdate),
                                                               "tender.advertmedia": media,
                                                               "tender.unit.value.currency": 'NGN',
                                                               "tender.unit.value.amount": minvalue,
                                                               "tender.unit.value.quantity": 1,
                                                               "tender.deliveryAddress": '',
                                                               "tender.value.currency": "NGN",
                                                               "tender.value.currency.amount": minvalue,
                                                               "tender.procurementMethod": procmethod,
                                                               "tender.rationale": rationale,
                                                               "tender.bppletterofobjection": bppletterofnoobj,
                                                               "tender.awardcriteria": awardCriteria,
                                                               "tender.awardcriteriadetails": awardCriteriadet,
                                                               "tender.tenderPeriodstart": parse_datetime(tenderstart),
                                                               "tender.tenderPeriodend": parse_datetime(tenderend),
                                                               "tender.submissionmethod": submethod,
                                                               "tender.submissionmethoddetails": submethoddet,
                                                               "tender.hasenquiries": hasenq,
                                                               "tender.enquiryPeriod.startDate": parse_datetime(
                                                                   enqperdstart),
                                                               "tender.enquiryPeriod.endDate": parse_datetime(
                                                                   enqperdstartend),
                                                               "tender.haspetition": haspet,
                                                               "tender.petitionremark": petitionremark,
                                                               "tender.eligibilitycriteria": eligcrit,
                                                               "tender.numberoftenderers": nooftenderers,
                                                               "tender.awardPeriod.startDate": parse_datetime(
                                                                   awardstart),
                                                               "tender.awardPeriod.endDate": parse_datetime(awardend),

                                                               "tender.projtype": projtype,

                                                               "tender.actualadvert": parse_datetime(advertstart),
                                                               "tender.actualadvertend": parse_datetime(advertend),
                                                               "tender.actualevaluation": parse_datetime(
                                                                   leadbefliststart),
                                                               "tender.actualevaluationend": parse_datetime(
                                                                   leadbeflistend),
                                                               "tender.actualshortlistapprove": parse_datetime(
                                                                   mdalistapprovestart),
                                                               "tender.actualshortlistapproveend": parse_datetime(
                                                                   mdalistapproveend),
                                                               "tender.actualshortlistpublish": parse_datetime(
                                                                   shortlistsubmission),
                                                               "tender.actualproposalinvite": parse_datetime(
                                                                   propinvitestart),
                                                               "tender.actualproposalinviteend": parse_datetime(
                                                                   propinviteend),
                                                               "tender.actualopeningoftechprop": parse_datetime(
                                                                   techpropopen),
                                                               "tender.actualevaluationtech": parse_datetime(
                                                                   subtechEvreportstart),
                                                               "tender.actualevaluationtechend": parse_datetime(
                                                                   subtechEvreportend),
                                                               "tender.actualevaluationtechapprov": parse_datetime(
                                                                   mdaapptechEvreportstart),
                                                               "tender.actualevaluationtechapprovend": parse_datetime(
                                                                   mdaapptechEvreportend),
                                                               "tender.actualopenfinancialprop": parse_datetime(
                                                                   Openingfinancialpropstart),
                                                               "tender.actualsubmittechreport": parse_datetime(
                                                                   submissionevareportstart),
                                                               "tender.actualsubmittechreportend": parse_datetime(
                                                                   submissionevareportend),
                                                               "tender.actualnegotiations": parse_datetime(
                                                                   Negotiationsstart),
                                                               "tender.actualnegotiationsend": parse_datetime(
                                                                   Negotiationsend),
                                                               "tender.actualprocuringenteval": parse_datetime(
                                                                   Negotiationappobjectstart),
                                                               "tender.actualprocuringentevalend": parse_datetime(
                                                                   Negotiationappobjectstartend),
                                                               "tender.actualcertificateobj": parse_datetime(
                                                                   planndcertnoobjstart),
                                                               "tender.actualcertificateobjend": parse_datetime(
                                                                   planndcertnoobjend),
                                                               "tender.actualadvertprequal": parse_datetime(
                                                                   preqadvertstart),
                                                               "tender.actualadvertprequalend": parse_datetime(
                                                                   preqadvertend),
                                                               "tender.actualprequalopening": parse_datetime(
                                                                   Prequalificationopen),
                                                               "tender.actualevalpreqalsubm": parse_datetime(
                                                                   Prequalificationstart),
                                                               "tender.actualevalpreqalsubmend": parse_datetime(
                                                                   Prequalificationend),
                                                               "tender.actualprequalapprov": parse_datetime(
                                                                   Prequalificationappobjectstart),
                                                               "tender.actualprequalapprovend": parse_datetime(
                                                                   Prequalificationappobjectend),
                                                               "tender.actualprequalpublish": parse_datetime(
                                                                   Prequalificationpubl),
                                                               "tender.actualfirstbid": parse_datetime(firstbidstart),
                                                               "tender.actualfirstbidend": parse_datetime(firstbidend),
                                                               "tender.actualsecondbid": parse_datetime(secondbidstart),
                                                               "tender.actualsecondbidend": parse_datetime(
                                                                   secondbidend),
                                                               "tender.actualbidinvite": parse_datetime(bidinvite),
                                                               "tender.actualbidclose": parse_datetime(bidclose),
                                                               "tender.actualbidevaluation": parse_datetime(
                                                                   bidevalrepstart),
                                                               "tender.actualbidevaluationend": parse_datetime(
                                                                   bidevalrepend),
                                                               "tender.actualprocuringenteval": parse_datetime(
                                                                   bidevalMDAstart),
                                                               "tender.actualprocuringentevalend": parse_datetime(
                                                                   bidevalMDAend),
                                                               "tender.actualcertificateobjevalreport": parse_datetime(
                                                                   certnoobjectstart),
                                                               "tender.actualcertificateobjevalreportend": parse_datetime(
                                                                   certnoobjectend),
                                                               "tender.actualfecapproval": parse_datetime(
                                                                   fecapprovestart),
                                                               "tender.actualfecapprovalend": parse_datetime(
                                                                   fecapproveend),
                                                               "tender.actualcontractoffer": parse_datetime(
                                                                   controfferstart),
                                                               "tender.actualcontractofferend": parse_datetime(
                                                                   controfferend),
                                                               "tender.actualcontractsignature": parse_datetime(
                                                                   contrsignstart),
                                                               "tender.actualcontractsignatureend": parse_datetime(
                                                                   contrsignend),
                                                               "tender.actualmobilization": parse_datetime(
                                                                   Mobilizationstart),
                                                               "tender.actualmobilizationend": parse_datetime(
                                                                   Mobilizationend),
                                                               "tender.actualsubmissiondraftrep": parse_datetime(
                                                                   draftreptstart),
                                                               "tender.actualsubmissionfinalrep": parse_datetime(
                                                                   finalreptstart),
                                                               "tender.actualgoodsarrival": parse_datetime(
                                                                   arrivalgoodsstart),
                                                               "tender.actualgoodsarrivalend": parse_datetime(
                                                                   arrivalgoodsend),
                                                               "tender.actualsubstantialcomplete": parse_datetime(
                                                                   substcomplend),
                                                               "tender.actualfinalaccept": parse_datetime(
                                                                   finalacceptstart),
                                                               "tender.actualfinalacceptend": parse_datetime(
                                                                   finalacceptend)

                                                           }
                                                   })

                    if query.modified_count is 1:

                        message = """Your Tender with OCID '%s' has been saved.""".replace('\n', ' ') % (ocid)
                        # return json.dumps({'message':'User created successfully !'})
                        flash(message)
                        return render_template('dashboard/tender.html')
                    else:
                        # duplicate where unique
                        # return json.dumps({'error':str(data[0])})
                        return render_template('dashboard/tender.html', error='Please review form entry')
                else:
                    # check required fields
                    # return json.dumps({'html':'<span>Enter the required fields</span>'})
                    return render_template('dashboard/tender.html',
                                           error='Enter the required values in the right format in the required fields')


            else:
                return render_template('dashboard/tender.html',
                                       error='OCID/Project is invalid or does not exist. Create New Release or Open Contracting Process')


        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')
    except Exception as e:
        # return render_template('dashboard/tender.html,error = 'A Tender already exists with that OCID or OCID is invalid')

        return json.dumps({'error': str(e)})
    finally:
        db.close


################################### START OF TENDER MODAL

# retrieve tender method
@app.route('/getTenders', methods=['POST'])
def getTenders():
    try:
        if session.get('user'):

            _user = session.get('user')

            _agencyName = session.get('agencyName')

            _offset = int(request.form['offset'])
            _limit = pageLimit

            releases = db.releases.find({"buyer.identifier.legalName": _agencyName}).sort([('_id', -1)]).skip(
                _offset).limit(_limit)

            res = db.releases.find({"buyer.identifier.legalName": _agencyName}).count()
            # print(res)



            response = []
            releases_dict = []

            # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON



            # looping through each query output
            for release in releases:
                d = release['tender']['advertisementdate']
                # collecting year, month and dat from ISO date format
                dString = d.strftime("%Y-%m-%d")

                release_dict = {
                    'OCID': release['ocid'],
                    'tender_Description': release['tender']['description'],
                    'Number_of_tenderers': release['tender']['numberoftenderers'],
                    'tender_status': release['tender']['status'],
                    'advert_date': dString,
                    'estimated_cost': release['tender']['value']['amount']}

                releases_dict.append(release_dict)
                response.append(releases_dict)
                response.append({'total': res})

            print(json.dumps(response))
            # convert into json after converting to dictionary
            return json.dumps(response)

        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('dashboard/error.html', error=str(e))


# get particular tender information
@app.route('/getTenderById', methods=['POST'])
def getTenderById():
    try:
        if session.get('user'):

            _id = request.form['id']

            # pymongo projection - fields
            releases = db.releases.find_one({"ocid": _id})

            response = []
            releases_dict = []

            for rel in releases:
                release_dict = {
                    'tender_status': rel['tender']['status']

                }
                releases_dict.append(release_dict)
                response.append(releases_dict)

            print(json.dumps(response))

            # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON

            return json.dumps(response)
        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('dashboard/error.html', error=str(e))


# update tender
@app.route('/updateTender', methods=['POST'])
def updateTender():
    try:
        if session.get('user'):
            _status = request.form['status']
            _release_id = request.form['id']

            # print(_release_id+" --------")


            #####TO DO
            ###THIS SHOULD UPDATE ALL TAGS IN ALL STAGES

            query = db.releases.update_one({"ocid": _release_id},
                                           {
                                               "$set":
                                                   {
                                                       "tender.status": _status

                                                   }

                                           })

            if query.modified_count is 1:

                return json.dumps({'status': 'OK'})
            else:
                return json.dumps({'status': 'ERROR'})
    except Exception as e:
        return json.dumps({'status': 'Unauthorized access'})
    finally:
        db.close

    # get particular contractor information
    @app.route('/getContractorById', methods=['POST'])
    def getContractorById():
        try:
            if session.get('user'):

                _id = int(request.form['id'])

                print(_id)
                # pymongo projection - fields
                contractors = db.registeredcontractors.find_one({"BPP_Contractor_ID": _id})

                # for rel in releases['releases']:
                # print(rel['tag'][0])


                response = []
                releases_dict = []

                # print(contractors['BPP_Contractor_ID'])

                release_dict = {
                    'BPP_ID': contractors['BPP_Contractor_ID'],
                    'Company_Name': contractors['Full_Registered_Company_Name'],
                    'CAC_Number': contractors['CACRegistrationNumber']
                }
                releases_dict.append(release_dict)
                response.append(releases_dict)

                print(json.dumps(response))

                # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON

                return json.dumps(response)
            else:
                return render_template('dashboard/error.html', error='Unauthorized Access')
        except Exception as e:
            return render_template('dashboard/error.html', error=str(e))

    # add tenderer to tender record

    # update tender
    @app.route('/newTenderer', methods=['POST'])
    def newTenderer():
        try:
            if session.get('user'):
                bppid = int(request.form['BPP_ID'])
                _release_id = request.form['id']

                # print(_release_id+" --------")



                query = db.releases.update_one({"ocid": _release_id},
                                               {
                                                   "$push":
                                                       {
                                                           "tender.tenderers": bppid

                                                       }

                                               })

                if query.modified_count is 1:

                    return json.dumps({'status': 'OK'})
                else:
                    return json.dumps({'status': 'ERROR'})
        except Exception as e:
            return json.dumps({'status': 'Unauthorized access'})
        finally:
            db.close



            ################################### END OF TENDER MODAL






            ################################### AWARD

            # render award form

    @app.route('/showNewAward')
    def showNewAward():
        return render_template('dashboard/award.html')

    # render award view
    @app.route('/showSavedAward')
    def showSavedAward():

        if session.get('user'):
            return render_template('dashboard/myawards.html')
        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')

    # new award
    @app.route("/addAward", methods=['POST'])
    def addAward():

        try:

            if session.get('user'):

                ocid = request.form.get('ocid', '')
                title = request.form.get('title', '')
                awardrefno = request.form.get('awardrefno', '')
                projdesc = request.form.get('projdesc', '')
                status = request.form.get('status', '')
                bppref = request.form.get('bppref', '')
                bppnodate = request.form.get('bppnodate', '')
                procappdate = request.form.get('procappdate', '')
                awarddate = request.form.get('awarddate', '')
                value = int(request.form['value'])

                Awardee = request.form.get('Awardee', '')

                bppno = int(request.form['bppno'])

                print(bppno)
                contdetails = request.form.get('contdetails', '')
                contractstart = request.form.get('contractstart', '')
                contractend = request.form.get('contractend', '')
                lowestbid = request.form.get('lowestbid', '')
                justify = request.form.get('justify', '')

                _agencyName = session.get('agencyName')

                query = db.releases.find_one({"ocid": ocid})

                if ocid and query:

                    # check ocid not null!

                    if bppref and Awardee and bppno and value and lowestbid:

                        query = db.releases.update_one({"ocid": ocid},
                                                       {
                                                           "$set":

                                                               {

                                                                   "awards": [{
                                                                       "status": status,
                                                                       "description": projdesc,
                                                                       "title": title,
                                                                       "reference": awardrefno,
                                                                       "date": parse_datetime(awarddate),
                                                                       "id": ocid,
                                                                       "items": [{"unit":
                                                                                      {"name": "Items",
                                                                                       "value": {"currency": "NGN",
                                                                                                 "amount": value}},
                                                                                  "id": ocid,
                                                                                  "classification": {"scheme": "",
                                                                                                     "id": ""},
                                                                                  "quantity": 1}],

                                                                       "suppliers": [{"additionalIdentifiers": [
                                                                           {"legalName": Awardee}],
                                                                                      "identifier": {"scheme": "",
                                                                                                     "id": "",
                                                                                                     "legalName": Awardee},
                                                                                      "name": Awardee, "bppNo": bppno}],
                                                                       "id": ocid,
                                                                       "value": {"currency": "NGN", "amount": value},
                                                                       "bppcertificateofobjectionnumber": bppref,
                                                                       "bppcertificateofobjectiondate": parse_datetime(
                                                                           bppnodate),
                                                                       "procuringentityapprovaldate": parse_datetime(
                                                                           procappdate),
                                                                       "contractdetails": contdetails,
                                                                       "contractPeriod.startDate": parse_datetime(
                                                                           contractstart),
                                                                       "contractPeriod.endDate": parse_datetime(
                                                                           contractend),
                                                                       "lowestbidder": lowestbid,
                                                                       "justification": justify
                                                                   }]

                                                               }
                                                       })

                        if query.modified_count is 1:

                            message = """Award with OCID '%s' has been saved.""".replace('\n', ' ') % (ocid)
                            # return json.dumps({'message':'User created successfully !'})
                            flash(message)
                            return render_template('dashboard/award.html')
                        else:
                            # duplicate where unique
                            # return json.dumps({'error':str(data[0])})
                            return render_template('dashboard/award.html', error='Please review form entry')
                    else:
                        # check required fields
                        # return json.dumps({'html':'<span>Enter the required fields</span>'})
                        return render_template('dashboard/award.html',
                                               error='Enter the required values in the right format in the required fields')


                else:
                    return render_template('dashboard/award.html',
                                           error='OCID/Project is invalid or does not exist. Create New Release or Open Contracting Process')


            else:
                return render_template('dashboard/error.html', error='Unauthorized Access')
        except Exception as e:
            # return render_template('dashboard/tender.html,error = 'A Tender already exists with that OCID or OCID is invalid')

            return json.dumps({'error': str(e)})
        finally:
            db.close

    ################################### START OF AWARD MODAL


    # retrieve awards method
    @app.route('/getAwards', methods=['POST'])
    def getAwards():
        try:
            if session.get('user'):

                _user = session.get('user')

                _agencyName = session.get('agencyName')

                _offset = int(request.form['offset'])
                _limit = pageLimit

                releases = db.releases.find({"buyer.identifier.legalName": _agencyName}).sort([('_id', -1)]).skip(
                    _offset).limit(_limit)

                res = db.releases.find({"buyer.identifier.legalName": _agencyName}).count()
                # print(res)




                response = []
                releases_dict = []

                # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON
                for release in releases:
                    d = release['awards']['date']
                    dString = d.strftime("%Y-%m-%d")

                    release_dict = {
                        'OCID': release['ocid'],
                        'award_Description': release['awards']['description'],
                        'reference': release['awards']['reference'],
                        'award_status': release['awards']['status'],
                        'award_date': dString,
                        'value': release['awards']['value']['amount']}

                    releases_dict.append(release_dict)
                    response.append(releases_dict)
                    response.append({'total': res})

                print(json.dumps(response))
                # convert into json after converting to dictionary
                return json.dumps(response)


            else:
                return render_template('dashboard/error.html', error='Unauthorized Access')
        except Exception as e:
            return render_template('dashboard/error.html', error=str(e))

    # get particular award information
    @app.route('/getAwardById', methods=['POST'])
    def getAwardById():
        try:
            if session.get('user'):

                _id = request.form['id']

                # pymongo projection - fields
                releases = db.releases.find_one({"ocid": _id})

                response = []
                releases_dict = []

                for rel in releases:
                    release_dict = {
                        'award_status': rel['awards']['status']

                    }
                    releases_dict.append(release_dict)
                    response.append(releases_dict)

                print(json.dumps(response))

                # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON

                return json.dumps(response)
            else:
                return render_template('dashboard/error.html', error='Unauthorized Access')
        except Exception as e:
            return render_template('dashboard/error.html', error=str(e))

    # update award
    @app.route('/updateAward', methods=['POST'])
    def updateAward():
        try:
            if session.get('user'):
                _status = request.form['status']
                _release_id = request.form['id']

                # print(_release_id+" --------")


                #####TO DO
                ###THIS SHOULD UPDATE ALL TAGS IN ALL STAGES

                query = db.releases.update_one({"ocid": _release_id},
                                               {
                                                   "$set":
                                                       {
                                                           "awards.status": _status

                                                       }

                                               })

                if query.modified_count is 1:

                    return json.dumps({'status': 'OK'})
                else:
                    return json.dumps({'status': 'ERROR'})
        except Exception as e:
            return json.dumps({'status': 'Unauthorized access'})
        finally:
            db.close








            ################################### END OF AWARD MODAL

    ################################### CONTRACT
    # render contract form
    @app.route('/showNewContract')
    def showNewContract():
        return render_template('dashboard/contract.html')

    # render contract view
    @app.route('/showSavedContract')
    def showSavedConract():

        if session.get('user'):
            return render_template('dashboard/mycontracts.html')
        else:
            return render_template('dashboard/error.html', error='Unauthorized Access')

    # new contract
    @app.route("/addContract", methods=['POST'])
    def addContract():

        try:

            if session.get('user'):

                ocid = request.form.get('ocid', '')
                contref = request.form.get('contref', '')
                title = request.form.get('title', '')
                projdesc = request.form.get('projdesc', '')
                status = request.form.get('status', '')
                signeddate = request.form.get('signeddate', '')
                contractstart = request.form.get('contractstart', '')
                contractend = request.form.get('contractend', '')

                street = request.form.get('street', '')
                city = request.form.get('city', '')
                state = request.form.get('state', '')
                Country = request.form.get('Country', '')

                stringAddress = [street, city, state, Country]

                g = geocoder.google(",".join(stringAddress))
                latitude = g.lat
                longitude = g.lng

                _agencyName = session.get('agencyName')

                query = db.releases.find_one({"ocid": ocid})

                if ocid and query:

                    # check ocid not null!

                    if contref and street and city and Country:

                        query = db.releases.update_one({"ocid": ocid},
                                                       {
                                                           "$set":

                                                               {

                                                                   "contracts": [{
                                                                       "status": status,
                                                                       "documents": [
                                                                           {"id": ocid, "language": language}],
                                                                       "description": projdesc,
                                                                       "title": title,
                                                                       "reference": contref,
                                                                       "implementation":
                                                                           {"milestones": [{"status": "",
                                                                                            "documents": [{"id": "",
                                                                                                           "language": language}],
                                                                                            "dateModified": "",
                                                                                            "id": ocid,
                                                                                            "dueDate": ""}]},
                                                                       "providerOrganization":
                                                                           {"scheme": "", "id": "",
                                                                            "legalName": _agencyName},
                                                                       "items": [{"unit": {"name": "",
                                                                                           "value": {"currency": "NGN",
                                                                                                     "amount": 0}},
                                                                                  "id": ocid,
                                                                                  "classification": {"scheme": "",
                                                                                                     "id": ""},
                                                                                  "quantity": 1}],
                                                                       "awardID": ocid,
                                                                       "id": ocid,
                                                                       "signeddate": parse_datetime(signeddate),
                                                                       "period": {
                                                                           "startDate": parse_datetime(contractstart),
                                                                           "endDate": parse_datetime(contractend)},
                                                                       "dueDate": parse_datetime(contractend),
                                                                       "projectlocation": {
                                                                           "streetaddress": street,
                                                                           "city": city,
                                                                           "state": state,
                                                                           "country": Country
                                                                       }
                                                                   }]

                                                               }
                                                       })

                        # update array
                        #####delete from array
                        # db.releases.update({"ocid":"OCDS-2016-UNIBEN2016359-22-54-45"},{"$pull":{"contracts.projectlocation.coord":6.334986}});



                        query = db.releases.update_one({"ocid": ocid},
                                                       {
                                                           "$push":
                                                               {
                                                                   "contracts.projectlocation.coord": longitude

                                                               }

                                                       })

                        query = db.releases.update_one({"ocid": ocid},
                                                       {
                                                           "$push":
                                                               {
                                                                   "contracts.projectlocation.coord": latitude

                                                               }

                                                       })

                        if query.modified_count is 1:

                            message = """Contract with OCID '%s' has been saved.""".replace('\n', ' ') % (ocid)
                            # return json.dumps({'message':'User created successfully !'})
                            flash(message)
                            return render_template('dashboard/contract.html')
                        else:
                            # duplicate where unique
                            # return json.dumps({'error':str(data[0])})
                            return render_template('dashboard/contract.html', error='Please review form entry')
                    else:
                        # check required fields
                        # return json.dumps({'html':'<span>Enter the required fields</span>'})
                        return render_template('dashboard/contract.html',
                                               error='Enter the required values in the right format in the required fields')


                else:
                    return render_template('dashboard/contract.html',
                                           error='OCID/Project is invalid or does not exist. Create New Release or Open Contracting Process')


            else:
                return render_template('dashboard/error.html', error='Unauthorized Access')
        except Exception as e:
            # return render_template('dashboard/tender.html,error = 'A Tender already exists with that OCID or OCID is invalid')

            return json.dumps({'error': str(e)})
        finally:
            db.close

    ################################### START OF CONTRACT MODAL


    # retrieve contracts method
    @app.route('/getContracts', methods=['POST'])
    def getContracts():
        try:
            if session.get('user'):

                _user = session.get('user')

                _agencyName = session.get('agencyName')

                _offset = int(request.form['offset'])
                _limit = pageLimit

                releases = db.releases.find({"buyer.identifier.legalName": _agencyName}).sort([('_id', -1)]).skip(
                    _offset).limit(_limit)

                res = db.releases.find({"buyer.identifier.legalName": _agencyName}).count()
                # print(res)




                response = []
                releases_dict = []

                # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON
                for release in releases:
                    sd = release['contracts']['signeddate']
                    dString = sd.strftime("%Y-%m-%d")

                    startd = release['contracts']['period']['startDate']
                    startString = startd.strftime("%Y-%m-%d")

                    endd = release['contracts']['period']['endDate']
                    endString = endd.strftime("%Y-%m-%d")

                    # THE ARRAY IS A LIST
                    coord = release['contracts']['projectlocation']['coord']

                    # for rev in inrel['contracts']['projectlocation']['coord']:
                    #    print rev
                    release_dict = {
                        'OCID': release['ocid'],
                        'contract_Description': release['contracts']['description'],
                        'reference': release['contracts']['reference'],
                        'contract_status': release['contracts']['status'],
                        'contract_date': dString,
                        'start_date': startString,
                        'end_date': endString,
                        'street': release['contracts']['projectlocation']['streetaddress'],
                        'city': release['contracts']['projectlocation']['city'],
                        'state': release['contracts']['projectlocation']['state'],
                        'country': release['contracts']['projectlocation']['country'],
                        'longit': coord[0],
                        'latitude': coord[1]
                    }

                    releases_dict.append(release_dict)
                    response.append(releases_dict)
                    response.append({'total': res})

                print(json.dumps(response))
                # convert into json after converting to dictionary
                return json.dumps(response)


            else:
                return render_template('dashboard/error.html', error='Unauthorized Access')
        except Exception as e:
            return render_template('dashboard/error.html', error=str(e))

    # get particular contract information
    @app.route('/getContractById', methods=['POST'])
    def getContractById():
        try:
            if session.get('user'):

                _id = request.form['id']

                # pymongo projection - fields
                releases = db.releases.find_one({"ocid": _id})

                response = []
                releases_dict = []

                release_dict = {
                    'award_status': releases['contracts']['status']

                }
                releases_dict.append(release_dict)
                response.append(releases_dict)

                # print(json.dumps(response

                # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON

                return json.dumps(response)
            else:
                return render_template('dashboard/error.html', error='Unauthorized Access')
        except Exception as e:
            return render_template('dashboard/error.html', error=str(e))

    #############################################End of DATA FETCHING METHODS



    # update contract
    @app.route('/updateContract', methods=['POST'])
    def updateContract():
        try:
            if session.get('user'):
                _status = request.form['status']
                _release_id = request.form['id']

                # print(_release_id+" --------")


                #####TO DO
                ###THIS SHOULD UPDATE ALL TAGS IN ALL STAGES

                query = db.releases.update_one({"ocid": _release_id},
                                               {
                                                   "$set":
                                                       {
                                                           "contracts.status": _status

                                                       }

                                               })

                if query.modified_count is 1:

                    return json.dumps({'status': 'OK'})
                else:
                    return json.dumps({'status': 'ERROR'})
        except Exception as e:
            return json.dumps({'status': 'Unauthorized access'})
        finally:
            db.close

    ################################### END OF CONTRACT MODAL



    # begin contract implementation
    @app.route('/newImplementation', methods=['POST'])
    def newImplementation():
        try:
            if session.get('user'):
                _release_id = request.form['id']
                variationYesOrNo = request.form.get('variationYesOrNo', '')
                bppapprovalNumber = request.form.get('bppapprovalNumber', '')
                variationamountt = int(request.form.get('variationamountt', ''))
                totalValue = int(request.form.get('totalValue', ''))
                print(variationYesOrNo)

                query = db.releases.update_one({"ocid": _release_id},
                                               {
                                                   "$set":
                                                       {
                                                           "contracts.implementation.variation": variationYesOrNo,
                                                           "contracts.implementation.variationamount": variationamountt,
                                                           "contracts.implementation.revisedcontractamount": totalValue,
                                                           "contracts.implementation.bppapproval": bppapprovalNumber
                                                       }

                                               })

                if query.modified_count is 1:

                    return json.dumps({'status': 'OK'})
                else:
                    return json.dumps({'status': 'ERROR'})
        except Exception as e:
            return json.dumps({'status': 'Unauthorized access'})
        finally:
            db.close

    # update contract completion
    @app.route('/updateImplementation', methods=['POST'])
    def updateImplementation():
        try:
            if session.get('user'):
                _release_id = request.form['id']
                finalcost = int(request.form.get('finalcost', ''))
                status = request.form.get('status', '')
                completiontilldate = request.form.get('projcompletion', '')
                amount = int(request.form.get('amount', ''))

                query = db.releases.update_one({"ocid": _release_id},
                                               {
                                                   "$set":
                                                       {
                                                           "contracts.implementation.finalcost": finalcost,
                                                           "contracts.implementation.projectstatus": status,
                                                           "contracts.implementation.tilldate": completiontilldate
                                                       }

                                               })

                query = db.releases.update_one({"ocid": _release_id},
                                               {
                                                   "$push":
                                                       {
                                                           "contracts.implementation.amountspaid": amount

                                                       }

                                               })

                if query.modified_count is 1:

                    return json.dumps({'status': 'OK'})
                else:
                    return json.dumps({'status': 'ERROR'})
        except Exception as e:
            return json.dumps({'status': 'Unauthorized access'})
        finally:
            db.close

    ##################################CONTRACTS PAGE SEARCH

    # https://code.tutsplus.com/tutorials/full-text-search-in-mongodb--cms-24835
    # create search index on collection during config as specified above
    # db.releases.createIndex({"$**":"text"})
    # db.releases.getIndexes()
    # db.releases.dropIndex("$**_text")


    # testing date
    # createIndex({"releases.contracts.period.startDate":1, "releases.contracts.period.endDate":1,"$**":"text"})



    # retrieve contracts method
    @app.route('/contractSearch', methods=['POST'])
    def contractSearch():
        try:
            _offset = int(request.form['offset'])
            searchString = request.form['searchString']

            # startDate = request.form['startDate']
            # endDate = request.form['endDate']

            # print(startDate)
            # print(endDate)
            print(searchString)

            _limit = pageLimit

            releases = db.releases.find({"$text": {"$search": searchString}})

            res = db.releases.find({"$text": {"$search": searchString}}).count()

            print(res)
            # releases = db.releases.find({"releases.buyer.identifier.legalName":_agencyName}).sort([('_id', -1)]).skip(_offset).limit(_limit)

            # res = db.releases.find({"releases.buyer.identifier.legalName":_agencyName}).count()
            # print(res)



            if res > 0:

                response = []
                releases_dict = []

                # parse the data (python list) and convert it into a dictionary so that it's easy to return as JSON
                for release in releases:
                    sd = release['contracts']['signeddate']
                    dString = sd.strftime("%Y-%m-%d")

                    startd = release['contracts']['period']['startDate']
                    startString = startd.strftime("%Y-%m-%d")

                    endd = release['contracts']['period']['endDate']
                    endString = endd.strftime("%Y-%m-%d")

                    # THE ARRAY IS A LIST
                    coord = release['contracts']['projectlocation']['coord']

                    # for rev in inrel['contracts']['projectlocation']['coord']:
                    # print rev
                    release_dict = {
                        'OCID': release['ocid'],
                        'contract_Description': release['contracts']['description'],
                        'reference': release['contracts']['reference'],
                        'contract_status': release['contracts']['status'],
                        'contract_date': dString,
                        'start_date': startString,
                        'end_date': endString,
                        'street': release['contracts']['projectlocation']['streetaddress'],
                        'city': release['contracts']['projectlocation']['city'],
                        'state': release['contracts']['projectlocation']['state'],
                        'country': release['contracts']['projectlocation']['country'],
                        'longit': coord[0],
                        'latitude': coord[1]
                    }

                    releases_dict.append(release_dict)
                    response.append(releases_dict)
                    response.append({'total': res})

                print(json.dumps(response))
                # convert into json after converting to dictionary
                return json.dumps(response)


            else:
                print('no result')
                return render_template('dashboard/mycontracts.html', error='No results found')

        except Exception as e:
            return render_template('dashboard/error.html', error=str(e))



            ###################################END CONTRACTS PAGE SEARCH


##############################################################################################Dashboard#####################################################################################################


##############################################################################################Releases#####################################################################################################







################################################################################################




if __name__ == "__main__":
    app.run(host='0.0.0.0')
