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


def test_dates_censored(output_dir, stats):
    date_patterns = [
            r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} -\d{4} \(PST\)', # e.g., Mon, 27 Nov 2000 08:56:00 -0800 (PST)
            r'\b\d{1,2}/\d{1,2}/\d{2} \d{1,2}:\d{2} [AP]M', # e.g., 11/27/00 08:44 AM
            r'\b\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [AP]M', # e.g., 11/27/2000 08:41 AM
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:th|st|nd|rd),?', # e.g., January 9th, 10th,
            r'\b\d{1,2}/\d{1,2} or \d{2}/\d{2} of (?:January|February|March|April|May|June|July|August|September|October|November|December)', # e.g., 19/20 or 20/21 of December
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}-\d{1,2}', # e.g., Jan 8-9
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:th)?', # e.g., December 13th
        ]
    input_text = "Jasun's birthday is on August 5th. Lasun's birthday is on June 25th."
    dir='temp/'

    if not os.path.exists(dir):
        os.makedirs(dir)
    input_dir=os.path.join(dir, 'input_date.txt') 
    with open(input_dir,'w', encoding='utf-8') as f:
        f.write(input_text)
    output_dir=os.path.join(dir, 'test_date.censored')
    with open(input_dir,'r', encoding='utf-8') as f:
        text=f.read()
        for pattern in date_patterns:
            op_text = re.sub(pattern, lambda x: '█' * len(x.group()), text)
        with open(output_dir,'w', encoding='utf-8') as f:
            f.write(op_text)

    with open(output_dir,'r', encoding='utf-8') as f:
        optext=f.read()
        assert "August 5th" not in str(optext)
        print("redacted text", optext)
        assert "June 25th" not in str(optext)


    
