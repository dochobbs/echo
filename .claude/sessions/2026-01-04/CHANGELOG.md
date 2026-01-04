# Changelog - 2026-01-04

## Features

### Teaching Frameworks (100 conditions)
Created comprehensive teaching frameworks for the complete pediatric primary care curriculum:

**Newborn/Infant (15):**
- hyperbilirubinemia, febrile_infant, breastfeeding_nutrition, early_onset_sepsis
- safe_sleep_sids, ddh, colic, neonatal_hypoglycemia, umbilical_issues
- torticollis_plagiocephaly, cmpi, benign_neonatal_rashes, tongue_tie
- failure_to_thrive, pyloric_stenosis

**Infectious Disease (17):**
- otitis_media, bronchiolitis, pneumonia, croup, strep_pharyngitis
- uti, influenza, gastroenteritis, lyme_disease, mononucleosis
- hsv_gingivostomatitis, impetigo_mrsa, periorbital_orbital_cellulitis
- pinworms, recurrent_infections, cervical_lymphadenopathy, meningitis
- pertussis, varicella

**Respiratory/Allergy (5):**
- asthma, anaphylaxis, food_allergy_prevention, atopic_dermatitis, acne

**Dermatology (11):**
- tinea, scabies_lice, contact_dermatitis, pityriasis_rosea, alopecia
- warts_molluscum, infantile_hemangiomas, diaper_dermatitis, seborrheic_dermatitis

**Behavioral/Developmental (12):**
- adhd, autism, depression, anxiety, eating_disorders, tics_tourette
- screen_time, sleep_disorders, headache_migraine, speech_delay, learning_disabilities

**GI (6):**
- constipation, appendicitis, gerd, celiac, ibd, intussusception

**Emergency/Trauma (10):**
- head_injury, febrile_seizures, ingestions, nursemaids_elbow, kawasaki
- drowning, burns, child_abuse, animal_bites, chest_pain

**MSK (6):**
- apophysitis, scoliosis, jia, lower_extremity_alignment, limping_child, hsp

**Endocrine (7):**
- obesity, type2_diabetes, type1_diabetes_sick_day, puberty_disorders
- thyroid, short_stature, adrenal_insufficiency

**Nephrology/Urology (7):**
- hypertension, hematuria_proteinuria, enuresis, cryptorchidism
- phimosis, acute_scrotum, inguinal_hernia_hydrocele

**Hematology/Oncology (2):**
- iron_deficiency_anemia, oncologic_emergencies

**Adolescent/GYN (3):**
- stis, contraception, dysmenorrhea

### Framework Loader Module
- `src/knowledge/framework_loader.py` - Python module with:
  - Singleton pattern for efficient loading
  - Query by key, name, or alias
  - Category filtering
  - Age-appropriate filtering
  - Teaching context extraction
  - Case prompt building

### Deployment Package
- `REPLIT_HANDOFF.md` - Complete integration guide
- `frameworks_bundle.tar.gz` - All files bundled for deployment

## Documentation
- `knowledge/frameworks/_schema.yaml` - Enhanced schema with all field definitions
