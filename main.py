import sys
import os
import json
import csv
import xlrd
from arg_parser import parse_argments


def create_metadata_file(path):
    '''
    Create new metadata file base on the user input.
    User will input medatada fields in comma separated.
    At last it will prompt to confirm user typed correctly,
        if the user press 'Y' or 'y' key, typed medatada would be accepted.
        if the user press any other keys, user can retype metadata header.
    :param path: metadata directory path
    :return: None
    '''
    print("Creating matadata file...")
    headers = []
    while True:
        header_string = input("Please input headers separating comma:")
        str = "["
        headers = header_string.replace(" ", "").split(',')
        if "" in headers:
            print("Empty header found, try again please.\n")
        else:
            for header in headers:
                if header != headers[-1]:
                    str = str + header + ", "
                else:
                    str = str + header + "]"
            answer = input("Would you save header{}?[Y]".format(str))
            if answer == 'y' or answer == 'Y' or answer == "":
                break

    metadata = {}
    for header in headers:
        metadata[header] = [header, ]

    with open(path, 'w') as metadata_file:
        json.dump(metadata, metadata_file, indent=4)
    print("metadata file created: {}".format(path))


def mapping_header2metadata(directory_path, header):
    '''
    It will check the csv/xlsx header and map the header fields to the metadata.
    :param directory_path: metadata file directory path
    :param header: csv/xlsx header from a specific file
    :return: dictionary data, key: csv header field, value: metadata field
    '''
    metadata = {}
    metadata_updated = False
    with open(directory_path + '/metadata.json') as medatada_file:
        metadata = json.load(medatada_file)

    header_mapping = {}
    for field in header:
        header_mapping[field] = ''
        for meta_field, meta_alternatives in metadata.items():
            if field in meta_alternatives:
                header_mapping[field] = meta_field
                break
        if header_mapping[field] == '':
            while True:
                mapping_list = ["Ignore", ]
                print_string = "[0]: Ignore\n"
                count = 1
                for meta_field in metadata:
                    print_string += "[{}]: {}\n".format(count, meta_field)
                    mapping_list.append(meta_field)
                    count += 1
                print_string += "[a]: Add new metadata"
                print(print_string)

                option = 'a'
                while True:
                    try:
                        option = input("{}: New header found. Select a mapping options:".format(field))
                        option = int(option)
                        break
                    except ValueError:
                        if option == 'a':
                            break
                        print("Invalid input. Try again.")
                        continue

                if option == 0:
                    header_mapping[field] = "--ignore--"
                    break
                elif option == 'a':
                    header_mapping[field] = field
                    metadata[field] = [field, ]
                    metadata_updated = True
                    break
                elif count > option > 0:
                    header_mapping[field] = mapping_list[option]
                    metadata[mapping_list[option]].append(field)
                    metadata_updated = True
                    break
                else:
                    print("Please input correct number[0~{}]".format(count))

    if metadata_updated:
        print(metadata)
        with open(directory_path + '/metadata.json', 'w') as metadata_file:
            json.dump(metadata, metadata_file, indent=4)

    print(header_mapping)
    return header_mapping


def mapping_row2medatada(header_mapping, row):
    '''
    map each rows to [mapdata key: row value] pair
    :param header_mapping: [csv/xlsx header: mapdata]
    :param row: csv/xlsx row
    :return:
    '''
    header = list(header_mapping.values())
    mapped_data = dict(zip(header, row))
    print(mapped_data)
    return mapped_data


def parse_csv_file(directory_path, file):
    '''

    :param directory_path:
    :param file:
    :return:
    '''
    path = '{}/{}'.format(directory_path, file)
    print("parsing {}".format(path))

    header_mapping = {}
    mapped_data_list = []
    with open(path, 'r') as csvFile:
        reader = csv.reader(csvFile)
        line_count = 0
        for row in reader:
            if line_count == 0:
                header_mapping = mapping_header2metadata(directory_path, row)
            else:
                mapped_data = mapping_row2medatada(header_mapping, row)
                mapped_data_list.append(mapped_data)
            line_count += 1
    csvFile.close()

    return mapped_data_list


def parse_xlsx_file(directory_path, file):
    '''

    :param directory_path:
    :param file:
    :return:
    '''
    path = '{}/{}'.format(directory_path, file)
    print("parsing {}".format(path))

    header_mapping = {}
    mapped_data_list = []
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    print(sheet.cell_value(0, 0))
    for i in range(sheet.nrows):
        print(sheet.row_values(i))
        if i == 0:
            header_mapping = mapping_header2metadata(directory_path, sheet.row_values(i))
        else:
            mapped_data = mapping_row2medatada(header_mapping, sheet.row_values(i))
            mapped_data_list.append(mapped_data)

    return mapped_data_list


def join_files(directory_path, output_path):
    '''

    :param directory_path:
    :param output_path:
    :return:
    '''
    print("Joining files from {}, to {}".format(directory_path, output_path))
    files = os.listdir(directory_path)

    joined_list = []
    parsed_list = []
    for file in files:
        if file.split('.')[-1] == 'csv':
            parsed_list = parse_csv_file(directory_path, file)
        elif file.split('.')[-1] == 'xlsx':
            parsed_list = parse_xlsx_file(directory_path, file)
        else:
            continue
        joined_list.extend(parsed_list)

    metadata = {}
    with open(directory_path + '/metadata.json') as medatada_file:
        metadata = json.load(medatada_file)

    with open(output_path, 'w') as f:
        w = csv.DictWriter(f, metadata.keys())
        w.writeheader()
        for item in joined_list:
            if '--ignore--' in item: del item['--ignore--']
            w.writerow(item)

    print(joined_list)


def main():
    print("***Checking commandline options***")
    opt_values = parse_argments()

    data_directory = ""
    try:
        data_directory = opt_values['dir'].strip("/")
        if not os.path.isdir(data_directory):
            print("Directory not exists: path={}".format(data_directory))
            sys.exit()
    except KeyError:
        print("Directory option not found: dir=<path>")
        sys.exit()
    print("Start joining files from {}".format(data_directory))

    output_file = ""
    if 'output' not in opt_values:
        output_file = "{}/{}.csv".format(data_directory, data_directory.split('/')[-1])
        print("Output option not found. Result will saved in {}".format(output_file))
    else:
        output_file = opt_values['output']
        filename = output_file.split("/")[-1]
        output_directory = output_file.replace(filename, "")
        if not os.path.isdir(output_directory):
            print("Output directory {} not found.".format(output_directory))
            sys.exit()
        if filename.split('.')[-1] != 'csv':
            print("Invalid output file name: {}".format(filename))
            sys.exit()

    print("\n***Checking matadata file***")
    medatada_path = data_directory + "/metadata.json"
    if not os.path.exists(medatada_path):
        answer = input("matadata file not found. Create now?[Y]:")
        if answer == 'y' or answer == 'Y' or answer == "":
            create_metadata_file(medatada_path)
        else:
            metadata = {}
            with open(medatada_path, 'w') as metadata_file:
                json.dump(metadata, metadata_file, indent=4)
            print("Skip adding metadata.")
    else:
        print("matadata file found: {}".format(medatada_path))

    print("\n***Joining files ***")
    join_files(data_directory, output_file)
    print("Finished joining files!!!")


if __name__ == '__main__':
    main()
