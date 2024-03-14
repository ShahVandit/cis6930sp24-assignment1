import os
import re
import pytest
import spacy
@pytest.fixture
def input_dir(tmpdir):
    return str(tmpdir)

@pytest.fixture
def output_dir(tmpdir):
    return str(tmpdir)

@pytest.fixture
def stats(tmpdir):
    return str(tmpdir)


def test_name_censored(output_dir, stats):
    nlp=spacy.load('en_core_web_md')
    input_text = "Jason lives in TX 77002."
    doc=nlp(input_text)
    for ent in doc.ents:
        if ent.label_ in ["PERSON"]:
            entity_length = ent.end_char - ent.start_char
            input_text = input_text[:ent.start_char] + ('█' * entity_length) + input_text[ent.end_char:]
    dir='temp/'

    if not os.path.exists(dir):
        os.makedirs(dir)
    input_dir=os.path.join(dir, 'input_name.txt') 
    with open(input_dir,'w', encoding='utf-8') as f:
        f.write(input_text)

    output_dir=os.path.join(dir, 'test_name.censored')
    with open(input_dir,'r', encoding='utf-8') as f:
        text=f.read()
        for ent in doc.ents:
            if ent.label_ in ["PERSON"]:
                entity_length = ent.end_char - ent.start_char
                text = text[:ent.start_char] + ('█' * entity_length) + text[ent.end_char:]
        with open(output_dir,'w', encoding='utf-8') as f:
            f.write(text)

    with open(output_dir,'r', encoding='utf-8') as f:
        optext=f.read()
        assert "Jason" not in str(optext)


    
