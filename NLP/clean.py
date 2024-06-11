import re
import csv

def clean_multiline_quotes(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        content = infile.read()

    # Regular expression to match quoted text with newlines
    pattern = re.compile(r'\"(.*?)\"', re.DOTALL)

    def replace_newlines(match):
        return match.group(0).replace('\n', ' ').replace('\r', '').replace(';','')

    # Clean the content
    cleaned_content = pattern.sub(replace_newlines, content)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(cleaned_content)

    # Reopen cleaned content as CSV and reformat it properly
    with open(output_file, 'r', encoding='utf-8') as cleaned_file, open('temp_' + output_file, 'w', newline='', encoding='utf-8') as final_file:
        reader = csv.reader(cleaned_file)
        writer = csv.writer(final_file)
        for row in reader:
            writer.writerow(row)

input_csv = 'output.csv'
output_csv = 'cleaned_output.csv'
clean_multiline_quotes(input_csv, output_csv)