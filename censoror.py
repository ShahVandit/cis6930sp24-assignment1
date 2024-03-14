import argparse
import glob
import os
import re
import sys
import spacy
from collections import Counter, defaultdict

nlp = spacy.load("en_core_web_md")

def censor(text, censor_names, censor_dates, censor_phones, censor_address, stats):
    # Initialize a local counter for this function
    local_stats = Counter()
    if censor_dates:
        date_patterns = [
            r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} -\d{4} \(PST\)', # e.g., Mon, 27 Nov 2000 08:56:00 -0800 (PST)
            r'\b\d{1,2}/\d{1,2}/\d{2} \d{1,2}:\d{2} [AP]M', # e.g., 11/27/00 08:44 AM
            r'\b\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [AP]M', # e.g., 11/27/2000 08:41 AM
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:th|st|nd|rd),?', # e.g., January 9th, 10th,
            r'\b\d{1,2}/\d{1,2} or \d{2}/\d{2} of (?:January|February|March|April|May|June|July|August|September|October|November|December)', # e.g., 19/20 or 20/21 of December
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}-\d{1,2}', # e.g., Jan 8-9
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:th)?', # e.g., December 13th
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            local_stats['DATE'] += len(matches)
            text = re.sub(pattern, lambda x: '█' * len(x.group()), text)
    if censor_phones:
        phone_patterns = [
            r'\(\d{3}\)\s?\d{3}-\d{4}',  # (123) 456-7890
            r'\(\d{3}\)-\d{3}-\d{4}',  # (123)-456-7890
            r'\d{3}-\d{3}-\d{4}',  # 123-456-7890
            r'\d{3}\.\d{3}\.\d{4}',  # 123.456.7890
    ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            local_stats["PHONES"] += len(matches)
            text = re.sub(pattern, lambda x: '█' * len(x.group()), text)
    if censor_address:
        address_pattern = r'''
        \b\d{1,5}\s(?:[A-Za-z0-9]+\s){0,3}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Parkway|Pkwy|Square|Sq|Trail|Trl|Circle|Cir)\b
        (?:,\s?\d{1,2}(th|nd|rd|st)\sFloor)?
        (?:,?\s(?:[A-Za-z]+(?:\s[A-Za-z]+){0,2}),?\s(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY))
        (?:,?\s\d{5}(?:-\d{4})?)?|
        \b(?:[A-Za-z]+(?:\s[A-Za-z]+){0,2}),?\s(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\s\d{5}(?:-\d{4})?
    '''
    matches = re.findall(address_pattern, text, flags=re.VERBOSE)
    local_stats["ADDRESS"] += len(matches)
    text = re.sub(address_pattern, '██████████', text, flags=re.VERBOSE)

    if censor_names:
        count=0
        doc=nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["PERSON"]:
                entity_length = ent.end_char - ent.start_char
                text = text[:ent.start_char] + ('█' * entity_length) + text[ent.end_char:]
                local_stats['NAMES']+=1
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = len(re.findall(email_regex, text))
        text = re.sub(email_regex, "█@███.███", text)
        local_stats["EMAIL_NAME"] += matches
   
    # Update the global stats with this file's stats
    for key, count in local_stats.items():
        stats[key] += count

    return text, local_stats

def process_files(input_patterns, output_dir, censor_flags, stats_output):
    stats = Counter()
    detailed_stats = defaultdict(Counter)

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for pattern in input_patterns:
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                censored_content, file_stats = censor(content, 
                                       censor_flags['censor_names'],
                                       censor_flags['censor_dates'],
                                       censor_flags['censor_phones'],
                                       censor_flags['censor_address'], 
                                       stats)

                print(censored_content)
                detailed_stats[os.path.basename(file_path)] = file_stats
                stats["files_processed"] += 1
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                output_path = os.path.join(output_dir, file_path + ".censored")

                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(censored_content)

            except Exception as e:
                print(f"Error processing {file_path}: {e}", file=sys.stderr)

    # Print or write stats based on the stats_output parameter
    if stats_output == "stderr":
        print_stats(stats, detailed_stats, sys.stderr)
    elif stats_output == "stdout":
        print_stats(stats, detailed_stats, sys.stdout)
    else:
        with open(stats_output, 'w', encoding='utf-8') as f:
            print_stats(stats, detailed_stats, f)

def print_stats(stats, detailed_stats, output_stream):
    print(f"Processed {stats['files_processed']} files.", file=output_stream)
    for key, value in stats.items():
        if key != "files_processed":
            print(f"Total {key}: {value}", file=output_stream)
    print("Detailed stats:", dict(detailed_stats), file=output_stream)

def main():
    parser = argparse.ArgumentParser(description="Censor sensitive information from text files.")
    parser.add_argument('--input', type=str, nargs='+', required=True, help='Glob pattern(s) for input files.')
    parser.add_argument('--names', action='store_true', help='Censor names')
    parser.add_argument('--dates', action='store_true', help='Censor dates')
    parser.add_argument('--phones', action='store_true', help='Censor phone numbers')
    parser.add_argument('--address', action='store_true', help='Censor addresses')
    parser.add_argument('--output', type=str, required=True, help='Directory to store censored files.')
    parser.add_argument('--stats', type=str, help='Where to output stats. Supports stderr, stdout, or a file path.')
    args = parser.parse_args()

    censor_flags = {
        "censor_names": args.names,
        "censor_dates": args.dates,
        "censor_phones": args.phones,
        "censor_address": args.address
    }

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    process_files(args.input, args.output, censor_flags, args.stats)

# if '_name_' == "_main_":
main()