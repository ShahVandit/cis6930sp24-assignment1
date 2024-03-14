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
    phone_patterns = [
            r'\(\d{3}\)\s?\d{3}-\d{4}',  # (123) 456-7890
            r'\(\d{3}\)-\d{3}-\d{4}',  # (123)-456-7890
            r'\d{3}-\d{3}-\d{4}',  # 123-456-7890
            r'\d{3}\.\d{3}\.\d{4}',  # 123.456.7890
    ]
    input_text = "Jasun's birthday is on August 5th. Lasun's birthday is on June 25th and contact is 123.456.7890"
    dir='temp/'

    if not os.path.exists(dir):
        os.makedirs(dir)
    input_dir=os.path.join(dir, 'input_phone.txt') 
    with open(input_dir,'w', encoding='utf-8') as f:
        f.write(input_text)
    output_dir=os.path.join(dir, 'test_phone.censored')
    with open(input_dir,'r', encoding='utf-8') as f:
        text=f.read()
        for pattern in phone_patterns:
            op_text = re.sub(pattern,lambda x: '█' * len(x.group()), text)
        print(op_text)
        with open(output_dir,'w', encoding='utf-8') as f:
            f.write(op_text)

    with open(output_dir,'r', encoding='utf-8') as f:
        optext=f.read()
        assert "(123)-456-7890" not in str(optext)