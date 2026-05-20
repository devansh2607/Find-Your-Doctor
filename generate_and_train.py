import csv
import random
import hashlib
import os
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE, "data")
MODEL_DIR = os.path.join(BASE, "ml_models")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# SPECIALIZATIONS
# ─────────────────────────────────────────────────────────────

specializations = [
    "Cardiologist",
    "Dermatologist",
    "Neurologist",
    "Orthopedist",
    "Gastroenterologist",
    "Pulmonologist",
    "Endocrinologist",
    "Ophthalmologist",
    "ENT Specialist",
    "Psychiatrist",
    "Urologist",
    "Gynecologist",
    "Oncologist",
    "Rheumatologist",
    "Nephrologist",
    "Hematologist",
    "Infectious Disease",
    "Allergist",
    "General Physician",
    "Dentist"
]

# ─────────────────────────────────────────────────────────────
# SYMPTOMS
# ─────────────────────────────────────────────────────────────

symptoms_by_spec = {

    "Cardiologist": [
        "chest_pain",
        "palpitations",
        "shortness_of_breath",
        "dizziness",
        "fatigue",
        "swollen_ankles",
        "high_blood_pressure",
        "irregular_heartbeat",
        "chest_tightness",
        "jaw_pain"
    ],

    "Dermatologist": [
        "skin_rash",
        "itching",
        "acne",
        "hair_loss",
        "nail_changes",
        "skin_discoloration",
        "dry_skin",
        "eczema",
        "psoriasis",
        "hives",
        "warts",
        "skin_lesions"
    ],

    "Neurologist": [
        "headache",
        "migraine",
        "seizures",
        "memory_loss",
        "numbness",
        "tremors",
        "dizziness",
        "blurred_vision",
        "speech_difficulty",
        "balance_problems",
        "weakness",
        "tingling"
    ],

    "Orthopedist": [
        "joint_pain",
        "back_pain",
        "muscle_pain",
        "swollen_joints",
        "stiffness",
        "reduced_mobility",
        "knee_pain",
        "hip_pain",
        "shoulder_pain",
        "neck_pain",
        "bone_pain"
    ],

    "Gastroenterologist": [
        "stomach_pain",
        "nausea",
        "vomiting",
        "diarrhea",
        "constipation",
        "bloating",
        "heartburn",
        "blood_in_stool",
        "difficulty_swallowing",
        "abdominal_cramps",
        "jaundice"
    ],

    "Pulmonologist": [
        "cough",
        "wheezing",
        "shortness_of_breath",
        "chest_tightness",
        "breathing_difficulty",
        "chronic_cough",
        "coughing_blood",
        "night_sweats",
        "rapid_breathing"
    ],

    "Endocrinologist": [
        "weight_gain",
        "weight_loss",
        "fatigue",
        "excessive_thirst",
        "frequent_urination",
        "hair_thinning",
        "mood_swings",
        "heat_intolerance",
        "cold_intolerance",
        "swollen_neck"
    ],

    "Ophthalmologist": [
        "blurred_vision",
        "eye_pain",
        "red_eyes",
        "watery_eyes",
        "double_vision",
        "light_sensitivity",
        "flashes_of_light",
        "floaters",
        "eye_discharge",
        "dry_eyes"
    ],

    "ENT Specialist": [
        "ear_pain",
        "hearing_loss",
        "tinnitus",
        "sore_throat",
        "hoarseness",
        "nasal_congestion",
        "sneezing",
        "sinus_pain",
        "nosebleed",
        "ear_discharge"
    ],

    "Psychiatrist": [
        "anxiety",
        "depression",
        "mood_swings",
        "insomnia",
        "panic_attacks",
        "hallucinations",
        "irritability",
        "memory_loss",
        "concentration_problems",
        "phobias"
    ],

    "Urologist": [
        "frequent_urination",
        "painful_urination",
        "blood_in_urine",
        "kidney_pain",
        "urinary_incontinence",
        "difficulty_urinating",
        "lower_back_pain",
        "testicular_pain",
        "pelvic_pain"
    ],

    "Gynecologist": [
        "irregular_periods",
        "pelvic_pain",
        "vaginal_discharge",
        "menstrual_cramps",
        "breast_pain",
        "fertility_issues",
        "heavy_bleeding",
        "hot_flashes",
        "missed_period"
    ],

    "Dentist": [
        "tooth_pain",
        "gum_bleeding",
        "jaw_pain",
        "mouth_ulcer",
        "bad_breath",
        "sensitive_teeth",
        "tooth_swelling",
        "cavity",
        "tooth_decay",
        "bleeding_gums"
    ],

    "Oncologist": [
        "unexplained_weight_loss",
        "fatigue",
        "lump",
        "night_sweats",
        "persistent_fever",
        "bleeding",
        "pain",
        "skin_changes",
        "appetite_loss"
    ],

    "Rheumatologist": [
        "joint_swelling",
        "joint_pain",
        "morning_stiffness",
        "muscle_weakness",
        "fatigue",
        "dry_eyes",
        "dry_mouth",
        "raynauds",
        "muscle_aches"
    ],

    "Nephrologist": [
        "swollen_ankles",
        "decreased_urine",
        "fatigue",
        "nausea",
        "blood_in_urine",
        "high_blood_pressure",
        "muscle_cramps",
        "itchy_skin",
        "foamy_urine"
    ],

    "Hematologist": [
        "fatigue",
        "pale_skin",
        "easy_bruising",
        "frequent_infections",
        "prolonged_bleeding",
        "blood_in_urine",
        "night_sweats",
        "bone_pain",
        "enlarged_lymph_nodes"
    ],

    "Infectious Disease": [
        "fever",
        "chills",
        "fatigue",
        "body_aches",
        "night_sweats",
        "swollen_lymph_nodes",
        "skin_rash",
        "diarrhea",
        "weight_loss",
        "persistent_infection"
    ],

    "Allergist": [
        "sneezing",
        "runny_nose",
        "itchy_eyes",
        "skin_rash",
        "hives",
        "asthma",
        "food_allergy",
        "eczema",
        "nasal_congestion",
        "breathing_difficulty",
        "swelling"
    ],

    "General Physician": [
        "fever",
        "fatigue",
        "cold",
        "flu",
        "headache",
        "body_aches",
        "sore_throat",
        "cough",
        "nausea",
        "dizziness",
        "weakness",
        "loss_of_appetite"
    ]
}

# ─────────────────────────────────────────────────────────────
# CREATE DATASET
# ─────────────────────────────────────────────────────────────

all_symptoms = sorted(
    set(s for v in symptoms_by_spec.values() for s in v)
)

rows = []

for spec, primary in symptoms_by_spec.items():

    for _ in range(60):

        row = {s: 0 for s in all_symptoms}

        selected = random.sample(
            primary,
            min(random.randint(2, 5), len(primary))
        )

        for s in selected:
            row[s] = 1

        row['specialization'] = spec

        rows.append(row)

random.shuffle(rows)

dataset_path = os.path.join(DATA_DIR, 'symptoms_dataset.csv')

with open(dataset_path, 'w', newline='') as f:

    writer = csv.DictWriter(
        f,
        fieldnames=all_symptoms + ['specialization']
    )

    writer.writeheader()
    writer.writerows(rows)

print(f"Dataset created with {len(rows)} rows")

# ─────────────────────────────────────────────────────────────
# TRAIN MODEL
# ─────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv(dataset_path)

X = df.drop(columns=['specialization'])
y = df['specialization']

le = LabelEncoder()

y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

clf.fit(X_train, y_train)

preds = clf.predict(X_test)

acc = accuracy_score(y_test, preds)

# SAVE MODELS

joblib.dump(
    clf,
    os.path.join(MODEL_DIR, 'rf_model.pkl')
)

joblib.dump(
    le,
    os.path.join(MODEL_DIR, 'label_encoder.pkl')
)

joblib.dump(
    list(X.columns),
    os.path.join(MODEL_DIR, 'feature_columns.pkl')
)

print("\n✅ MODELS SAVED SUCCESSFULLY")
print(f"📁 Model Folder: {MODEL_DIR}")
print(f"🧠 Features: {len(X.columns)}")
print(f"🏷 Classes: {len(le.classes_)}")
print(f"🎯 Accuracy: {acc:.2%}")