import os
import csv
import json


# Check if the file is a CSV file
def check_csv_file(file_path):
    if not os.path.isfile(file_path) and filename.lower().endswith('.csv'):
        return False
    else:
        return True


# Get all CSV files in a directory
def get_csvs(directory):
    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return []

    csv_file_paths = []

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if check_csv_file(file_path):
            csv_file_paths.append(file_path)

    return csv_file_paths


# get all lines in csv file ignoring header
def process_csv_file(file_path):
    if not check_csv_file(file_path):
        print(f"File '{file_path}' is not a CSV file.")
        return []

    items = []

    # Open the CSV file
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)

        # Skip the header line
        next(csv_reader)

        # Append each item to the list
        for line in csv_reader:
            items.append(line[0])

    return items


# get file name without extension
def get_file_name(file_path):
    if not check_csv_file(file_path):
        print(f"File '{file_path}' is not a CSV file.")
        return []

    file_name = file_path.split('/')[-1]
    return file_name[:-4]


# import settings json file
def import_settings(json_file):
    with open(json_file) as json_file:
        data = json.load(json_file)
        return data


# parse domain from email
def parse_domain(email):
    domain = email.split('@')[-1]
    return domain


# check if email is part of the company
def drop_email(email, domain_drop_list, email_drop_list):
    domain = parse_domain(email)
    if domain in domain_drop_list:
        return True
    else:
        if email in email_drop_list:
            return True
        else:
            return False


# get domains for a company
def get_domains(settings, companies):
    domains = []

    for company in companies:
        if company in settings['companies']:
            domains.extend(settings['companies'][company])

    return domains


# delete all files in a directory
def clean_dir(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)


# write dictionary to csv
def write_dict_to_csv(dictionary, file_path, headers=[]):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)

        if headers.__len__() > 0:
            writer.writerow(headers)
        writer.writerows(dictionary.items())


# write list to csv
def write_list_to_csv(list, file_path, headers=[]):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)

        if headers.__len__() > 0:
            writer.writerow(headers)
        for item in list:
            writer.writerows([[item]])


def print_title(file):
    if os.path.isfile(file):
        f= open (file,'r')
        print(''.join([line for line in f]))
        f.close()
    else:
        print('Toil Reducer 3000')

if __name__ == "__main__":
    input_path = './input'
    output_path = './output'

    print('\n-------\n')
    print_title('title.txt')
    clean_dir(output_path)

    csvs = get_csvs(input_path)
    settings = import_settings('settings.json')
    domain_drop_list = settings['domain_drop_list']
    email_drop_list = settings['email_drop_list']
    companies = list(settings['companies'].keys())
    totals = {}

    print('\n-------\n')
    print(f"Found {len(csvs)} CSV files.")
    for csv_file in csvs:
        print(f" - {get_file_name(csv_file)}.csv")
    print(f"\nFound {len(companies)} companies.")
    for company in companies:
        print(f" - {company}")

    print('\n-------\n')

    for csv_file in csvs:
        filename = get_file_name(csv_file)
        emails = process_csv_file(csv_file)
        clean_emails = []
        dropped_emails = []

        print(f"Processing {filename}.csv ...")
        print(f" - {emails.__len__()} emails found.")

        for email in emails:
            if not drop_email(email, domain_drop_list, email_drop_list):
                clean_emails.append(email)
            else:
                dropped_emails.append(email)

            drop_count = dropped_emails.__len__()
            processed_count = clean_emails.__len__()

            write_list_to_csv(
                dropped_emails,
                f"{output_path}/{filename}_dropped.csv",
                ['email']
            )

        for company in companies:
            output_file = f"{output_path}/{filename}_{company}.csv"
            domains = get_domains(settings, [company])
            emails = []
            count = 0

            for email in clean_emails:
                if parse_domain(email) in domains:
                    count += 1
                    emails.append(email)

            totals[f"{filename}_{company}"] = count
            write_list_to_csv(emails, output_file, ['email'])

        print(f" - {processed_count} emails processed.")
        print(f" - {drop_count} emails dropped.")

    write_dict_to_csv(totals, f"{output_path}/totals.csv", ['item', 'count'])
    print('\n-------\n')
    print('Totals:')
    print(json.dumps(totals, indent=1)[1:-1])
    print('-------\n')
    print(f'Output files written to {output_path}\n')
