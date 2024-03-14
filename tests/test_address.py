import os
import re
import pytest

@pytest.fixture
def input_dir(tmpdir):
    return str(tmpdir)

@pytest.fixture
def output_dir(tmpdir):
    return str(tmpdir)

@pytest.fixture
def stats(tmpdir):
    return str(tmpdir)


def test_adress_censored(output_dir, stats):
    address_pattern = r'''
        \b\d{1,5}\s(?:[A-Za-z0-9]+\s){0,3}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Parkway|Pkwy|Square|Sq|Trail|Trl|Circle|Cir)\b
        (?:,\s?\d{1,2}(th|nd|rd|st)\sFloor)?
        (?:,?\s(?:[A-Za-z]+(?:\s[A-Za-z]+){0,2}),?\s(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY))
        (?:,?\s\d{5}(?:-\d{4})?)?|
        \b(?:[A-Za-z]+(?:\s[A-Za-z]+){0,2}),?\s(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\s\d{5}(?:-\d{4})?
    '''
    input_text = "Jasun lives in TX 77002."
    dir='temp/'

    if not os.path.exists(dir):
        os.makedirs(dir)
    input_dir=os.path.join(dir, 'input_address.txt') 
    with open(input_dir,'w', encoding='utf-8') as f:
        f.write(input_text)

    output_dir=os.path.join(dir, 'test_address.censored')
    with open(input_dir,'r', encoding='utf-8') as f:
        text=f.read()
        op_text = re.sub(address_pattern,'█', text)
        with open(output_dir,'w', encoding='utf-8') as f:
            f.write(op_text)

    with open(output_dir,'r', encoding='utf-8') as f:
        optext=f.read()
        assert "333 Clay Street, 11th Floor." not in str(optext)


    
