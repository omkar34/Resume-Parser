# -*- coding: utf-8 -*-
"""
Created on Sat Aug 28 11:07:12 2021

@author: Omkar.Thopate
"""

import pandas as pd
import numpy as np
import nltk
import spacy
import pdfminer
spacy.load('en_core_web_sm')
from pdfminer.high_level import extract_text
from pyresparser import ResumeParser
from nltk.stem import WordNetLemmatizer
import re
import json
import warnings
warnings.filterwarnings('ignore')



def extract_linkedIn(resume_text):
    LINKEDIN_REG= re.compile(r'(([a-zA-Z0-9\-])*\.|[linkedin])[linkedin/\-]+\.[a-zA-Z0-9/\-_,&=\?\.;]+[^\.,\s<]')

    new_text = resume_text.split(' ')
    for i in new_text:
        if 'linkedin' in i:
            linkedin = i
            return linkedin
    else:
        return "Not detected"

def extract_phone_number(resume_text):
    PHONE_REG = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phones = re.findall(PHONE_REG, resume_text)

    if phones:
        for phone in phones:
            if len(phone)>=10:
                number = ''.join(phone)
                return number
    return "Not detected"

def extract_emails(resume_text):
    EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
    if re.findall(EMAIL_REG, resume_text):
        email = re.findall(EMAIL_REG, resume_text)
        return email[0]
    else:
        return "Not detected"

def extract_skills(parsed_text, resume_text):
    parsed_skills = parsed_text['skills']

    nlp = spacy.load('en_core_web_sm')
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks

    tokens = [token.text for token in nlp_text if not token.is_stop]
 
    data = pd.read_csv("Files/skills.csv") 
    
    skills = list(data.columns.values)
    
    skillset = []

    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
 
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    skills_from_csv = [i for i in set([i.lower() for i in skillset])]

    if len(parsed_skills)>len(skills_from_csv):
        return parsed_skills
    else:
        return skills_from_csv

def extract_experience(parsed_text):
    experience = parsed_text['experience']
    if experience!=None:
        return experience
    else:
        return 'Not detected'

def extract_degree(parsed_text):
    degree = parsed_text['degree']
    if degree != None:
        return degree
    else:
        return 'Not detected'

def extra_curricular(resume_text):
    extra = ['leader','leadership','managed','manage','organize', 'organized','organizer','head','marketing',
             'foreign languages','council','sports','clubs','organization','societies', 'society','volunteering',
             'Tutoring','Teamwork','Fundraising','volenteer']
    extra_curricular = []
    for i in extra:
        if i in resume_text:
            extra_curricular.append(i)
    if len(extra_curricular)>=1:
        return extra_curricular
    else:
        return 'Not detected'

def remove_bias(resume_text):
    gender_spec = ['strong','lead','analysis','individual','decisions','driven','competitive','expert',
    'objectives','principles','analyze','analytical','analysis','individuals','volunteering']

    resume_text = resume_text.split()
    for i in gender_spec:
        if resume_text.count(i)>0:
            resume_text.remove(i)

    location_file = pd.read_csv("Files/Location.csv")
    city = list(location_file['Name of City'].str.lower())
    state = list(location_file['State'].str.lower())
    loc = city+state
    for i in loc:
        if resume_text.count(i)>0:
            resume_text.remove(i)
    res = ' '.join(resume_text)
    return res

path_to_resume = "Sample_Resumes/Resume3.pdf"      #Link to resume in pdf format

text = extract_text(path_to_resume)      
text = re.sub('\n',' ',text)
text = text.lower()
lemmatizer = WordNetLemmatizer()
word_list = nltk.word_tokenize(text)
resume_text_lem = ' '.join([lemmatizer.lemmatize(w) for w in word_list])
resume_text = remove_bias(resume_text_lem)

parsed_text = ResumeParser(path_to_resume).get_extracted_data()

data = {}

data['linkedin'] = extract_linkedIn(resume_text)
data['phone'] = extract_phone_number(resume_text)
data['email'] = extract_emails(text)
data['skills'] = extract_skills(parsed_text, resume_text)
data['experience'] = extract_experience(parsed_text)
data['degree'] = extract_degree(parsed_text)
data['extra_curricular'] = extra_curricular(resume_text)

for i in data:
    elem = data[i]
    if isinstance(elem, list) == True:
        elem = ', '.join(elem)
        data[i] = elem

print(json.dumps(data, indent = 4))

# linkedin = data['linkedin']
# phone = data['phone']
# email = data['email'] 
# skills = data['skills']
# experience = data['experience']
# degree = data['degree']
# extra_curricular = data['extra_curricular']

# print(linkedin)
# print(phone)
# print(email)
# print(skills)
# print(experience)
# print(degree)
# print(extra_curricular)