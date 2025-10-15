import csv
import os

def read_csv(file_path, as_dict=False):
    """
    Reads a CSV file and returns its content as a list of lists or a list of dictionaries.
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', encoding='utf-8') as file:
        if as_dict:
            reader = csv.DictReader(file)
        else:
            reader = csv.reader(file)
        return list(reader)

def write_csv(file_path, data, header=None):
    """
    Writes data to a CSV file. Data should be a list of lists.
    """
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if header:
            writer.writerow(header)
        writer.writerows(data)

def append_csv(file_path, data, header=None):
    """
    Appends data to a CSV file. Data should be a list of lists.
    """
    file_exists = os.path.exists(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists and header:
            writer.writerow(header)
        writer.writerows(data)
