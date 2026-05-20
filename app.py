from flask import Flask,render_template,request,jsonify,session,redirect,url_for,flash
import pandas as pd, numpy as np, joblib, os, csv, hashlib, math, uuid
from datetime import datetime
from functools import wraps

app=Flask(__name__)
app.secret_key="fyd_blue_2024"
BASE=os.path.dirname(os.path.abspath(__file__))
DATA=os.path.join(BASE,"data")
MODELS=os.path.join(BASE,"ml_models")

rf=joblib.load(os.path.join(MODELS,"rf_model.pkl"))
le=joblib.load(os.path.join(MODELS,"label_encoder.pkl"))
fc=joblib.load(os.path.join(MODELS,"feature_columns.pkl"))
print(f"✅ Model ready | {len(fc)} features | {len(le.classes_)} classes")

def rcsv(fn):
    p=os.path.join(DATA,fn)
    if not os.path.exists(p): return []
    with open(p,newline='',encoding='utf-8') as f: return list(csv.DictReader(f))

def wcsv(fn,rows,fns=None):
    if not rows: return
    p=os.path.join(DATA,fn); fns=fns or list(rows[0].keys())
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fns); w.writeheader(); w.writerows(rows)

def acsv(fn,row,fns=None):
    p=os.path.join(DATA,fn); exists=os.path.exists(p); fns=fns or list(row.keys())
    with open(p,'a',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fns)
        if not exists: w.writeheader()
        w.writerow(row)

def hp(pw): return hashlib.sha256(pw.encode()).hexdigest()

def haversine(a,b,c,d):
    R=6371; a,b,c,d=map(math.radians,[float(a),float(b),float(c),float(d)])
    return R*2*math.asin(math.sqrt(math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2))

def login_req(f):
    @wraps(f)
    def dec(*a,**k):
        if 'uid' not in session: return redirect(url_for('login'))
        return f(*a,**k)
    return dec

def doc_req(f):
    @wraps(f)
    def dec(*a,**k):
        if session.get('role') not in ('doctor','admin'): return redirect(url_for('login'))
        return f(*a,**k)
    return dec

@app.route('/')
def index(): return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email','').strip()
        pw=request.form.get('password','')
        role=request.form.get('role','patient')
        if role=='doctor':
            docs=rcsv('doctors.csv')
            u=next((d for d in docs if d.get('email')==email and d.get('password_hash')==hp(pw)),None)
            if u:
                session.update({'uid':u['doctor_id'],'name':u['name'],'role':'doctor','email':email})
                return redirect(url_for('doctor_dashboard'))
        else:
            users=rcsv('users.csv')
            u=next((x for x in users if x.get('email')==email and x.get('password_hash')==hp(pw)),None)
            if u:
                session.update({'uid':u['user_id'],'name':u['name'],'role':u['role'],'email':email})
                return redirect(url_for('patient_dashboard'))
        flash('Invalid credentials.','error')
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        role=request.form.get('role','patient'); name=request.form.get('name','').strip()
        email=request.form.get('email','').strip(); pw=request.form.get('password','')
        if role=='patient':
            users=rcsv('users.csv')
            if any(u['email']==email for u in users):
                flash('Email already registered.','error'); return render_template('register.html')
            uid=f"USR{len(users)+1:04d}"
            users.append({"user_id":uid,"name":name,"email":email,"password_hash":hp(pw),
                "role":"patient","city":request.form.get('city',''),"created_at":datetime.now().isoformat()})
            wcsv('users.csv',users); flash('Registered! Please login.','success')
            return redirect(url_for('login'))
        else:
            docs=rcsv('doctors.csv')
            if any(d['email']==email for d in docs):
                flash('Email already registered.','error'); return render_template('register.html')
            did=f"DOC{len(docs)+1:04d}"
            docs.append({"doctor_id":did,"name":name,"email":email,"password_hash":hp(pw),
                "specialization":request.form.get('specialization',''),"experience":request.form.get('experience',''),
                "fees":request.form.get('fees',''),"hospital":request.form.get('hospital',''),
                "area":request.form.get('area',''),"city":request.form.get('city',''),
                "latitude":request.form.get('latitude',''),"longitude":request.form.get('longitude',''),
                "phone":request.form.get('phone',''),"availability":request.form.get('availability',''),
                "rating":"4.0","reviews":"0","profile_pic":"default.png",
                "bio":request.form.get('bio',''),"approved":"True"})
            wcsv('doctors.csv',docs); flash('Doctor registered! Please login.','success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

@app.route('/patient/dashboard')
@login_req
def patient_dashboard(): return render_template('patient_dashboard.html')

@app.route('/doctor/dashboard')
@doc_req
def doctor_dashboard():
    docs=rcsv('doctors.csv'); did=session.get('uid')
    doc=next((d for d in docs if d['doctor_id']==did),None)
    appts=[a for a in rcsv('appointments.csv') if a.get('doctor_id')==did]
    return render_template('doctor_dashboard.html',doctor=doc,appointments=appts)

@app.route('/find-doctors')
def find_doctors(): return render_template('find_doctors.html')

@app.route('/doctor/<did>')
def doctor_profile(did):
    doc=next((d for d in rcsv('doctors.csv') if d['doctor_id']==did),None)
    if not doc: return "Not found",404
    return render_template('doctor_profile.html',doctor=doc)

@app.route('/doctor/edit-profile',methods=['GET','POST'])
@doc_req
def edit_doctor_profile():
    did=session.get('uid'); docs=rcsv('doctors.csv')
    doc=next((d for d in docs if d['doctor_id']==did),None)
    if request.method=='POST':
        for k in ['specialization','experience','fees','hospital','area','city','latitude','longitude','phone','availability','bio']:
            if request.form.get(k): doc[k]=request.form[k]
        wcsv('doctors.csv',docs); flash('Profile updated!','success')
        return redirect(url_for('doctor_dashboard'))
    return render_template('edit_profile.html',doctor=doc)

# ── APIs ──────────────────────────────────────────────────────────────────────
@app.route('/api/predict', methods=['POST'])
def predict():

    syms = request.get_json().get('symptoms', [])

    if not syms:
        return jsonify({'error': 'No symptoms'}), 400

    vec = {c: 0 for c in fc}

    matched = []

    # normalize symptoms
    for s in syms:

        clean = (
            str(s)
            .strip()
            .lower()
            .replace(' ', '_')
            .replace('-', '_')
        )

        if clean in fc:
            matched.append(clean)

    # fill vector
    for s in matched:
        vec[s] = 1

    if not matched:
        return jsonify({'error': 'No recognizable symptoms'}), 400

    # vague/common symptoms
    vague_symptoms = [
        "fever",
        "headache",
        "fatigue",
        "weakness",
        "pain",
        "body_pain",
        "dizziness",
        "cough",
        "cold"
    ]

    # single symptom -> GP
    if len(matched) <= 1:
        return jsonify({
            "primary_specialization": "General Physician",
            "confidence": 85,
            "matched_symptoms": matched
        })

    # all vague symptoms -> GP
    if all(s in vague_symptoms for s in matched):
        return jsonify({
            "primary_specialization": "General Physician",
            "confidence": 82,
            "matched_symptoms": matched
        })

    # ML prediction
    X = pd.DataFrame([vec])[fc]

    pred = rf.predict(X)[0]
    prob = rf.predict_proba(X)[0]

    raw_conf = float(np.max(prob)) * 100

    conf = max(raw_conf, 80)
    conf = min(conf, 97)

    return jsonify({
        "primary_specialization": le.classes_[pred],
        "confidence": round(conf, 1),
        "matched_symptoms": matched
    })

   

@app.route('/api/symptoms')
def get_symptoms():
    return jsonify({"symptoms":[s.replace('_',' ').title() for s in fc]})

@app.route('/api/doctors')
def get_doctors():
    docs=[d for d in rcsv('doctors.csv') if d.get('approved')=='True']
    spec=request.args.get('specialization',''); city=request.args.get('city','')
    mf=request.args.get('max_fees',type=float); me=request.args.get('min_exp',type=int)
    ult=request.args.get('lat',type=float); ulg=request.args.get('lng',type=float)
    md=request.args.get('max_distance',type=float); sb=request.args.get('sort_by','rating')
    if spec: docs=[d for d in docs if d.get('specialization','').lower()==spec.lower()]
    if city: docs=[d for d in docs if d.get('city','').lower()==city.lower()]
    if mf: docs=[d for d in docs if float(d.get('fees',0))<=mf]
    if me: docs=[d for d in docs if int(d.get('experience',0))>=me]
    for d in docs:
        d['distance_km']=round(haversine(ult,ulg,d['latitude'],d['longitude']),2) if ult and d.get('latitude') else None
    if md and ult: docs=[d for d in docs if d.get('distance_km') is not None and d['distance_km']<=md]
    docs.sort(key=lambda x:(float(x.get('rating',0)) if sb=='rating' else
        float(x.get('fees',0)) if sb=='fees_asc' else
        int(x.get('experience',0)) if sb=='experience' else
        (x.get('distance_km') or 999)),reverse=sb not in ('fees_asc','distance'))
    safe=[{k:v for k,v in d.items() if k!='password_hash'} for d in docs]
    return jsonify({"doctors":safe,"total":len(safe)})

@app.route('/api/doctors/<did>')
def get_doctor(did):
    doc=next((d for d in rcsv('doctors.csv') if d['doctor_id']==did),None)
    if not doc: return jsonify({'error':'Not found'}),404
    return jsonify({k:v for k,v in doc.items() if k!='password_hash'})

@app.route('/api/appointments',methods=['POST'])
@login_req
def book_appt():
    d=request.get_json()
    row={"appointment_id":f"APT{uuid.uuid4().hex[:8].upper()}","patient_id":session['uid'],
        "patient_name":session['name'],"doctor_id":d.get('doctor_id'),
        "date":d.get('date'),"time":d.get('time'),"status":"pending",
        "symptoms":d.get('symptoms',''),"notes":d.get('notes',''),"created_at":datetime.now().isoformat()}
    acsv('appointments.csv',row,list(row.keys()))
    return jsonify({"success":True,"appointment_id":row['appointment_id']})

@app.route('/api/appointments/<uid>')
@login_req
def get_appts(uid):
    appts=rcsv('appointments.csv')
    key='patient_id' if session.get('role')=='patient' else 'doctor_id'
    return jsonify({"appointments":[a for a in appts if a.get(key)==uid]})

@app.route('/api/appointments/<aid>/status',methods=['PUT'])
@doc_req
def upd_appt(aid):
    appts=rcsv('appointments.csv'); st=request.get_json().get('status')
    for a in appts:
        if a['appointment_id']==aid: a['status']=st
    wcsv('appointments.csv',appts); return jsonify({"success":True})

@app.route('/api/doctors/<did>/rate',methods=['POST'])
@login_req
def rate_doc(did):
    rating=float(request.get_json().get('rating',0)); docs=rcsv('doctors.csv')
    for d in docs:
        if d['doctor_id']==did:
            cr=float(d.get('rating',4)); rv=int(d.get('reviews',0))
            d['rating']=round((cr*rv+rating)/(rv+1),1); d['reviews']=rv+1
    wcsv('doctors.csv',docs); return jsonify({"success":True})

if __name__=='__main__': app.run(debug=True,port=5000)
