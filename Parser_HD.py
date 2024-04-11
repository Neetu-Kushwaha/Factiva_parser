# import Python libraries required to run code below
import re
import csv
import glob
import os
from logs import logger
from argparse import ArgumentParser

'''
Python code to parse Text downloads from Factiva into a single CSV for relation extraction.
'''


#sep is a variable we will use to separate each article.
#In the .rtf downloads there is a hexadecimal character 0x0C between each article (which skips to the next page))
# we can represent that character here with the escape character \f
sep = '\f'

# field names of factiva
fieldnames = ['SE', 'HD', 'WC', 'PD', 'SN', 'SC', 'LA', 'CY', 'LP', 'CO', 'TD', 'NS', 'RE', 'PUB', 'AN']


def factiva_to_csv(path: str, csv_filename: str):
    """ function processes the text files and takes the path to a folder full of .txt files you want to process as its argument

    Args:
        path (str): filepath of the folder which contains factiva text files.
        csv_filename (str): csv file name to store processed meta-data
    Returns:
        csv: Returns CSV file contains processed data from factiva text files
    """

    if not os.path.isdir(path):
        logger.info("File path not found")
        return ""

    # create a new csv
    # with open('factiva_metadata_new1.csv', 'w', newline='', encoding='utf-8') as csvfile:
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:

        # write the fieldnames defined above as the headers of your csv
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # cycle through every text file in the path given in the function's argument
        files_all = glob.iglob(path + "*.txt")
        ll = []
        for k, filename in enumerate(files_all):
            # remove the path, whitespace, and '.txt' from filename to later use when printing output
            ll.append((k, filename))
            file_id = filename[:-4].strip(path)
            print(file_id)
            logger.info("Starting file-number " + str(k) + " and filename is " + str(filename))

            # open the files
            with open(filename, 'r', encoding='utf-8') as in_file:
                # text var for string of all docs
                text = in_file.read()

                # remove the "Search Summary" from the end of each document
                search_sum = '\nSearch Summary\n'
                drop_search_sum = re.split(search_sum, text)
                text = drop_search_sum[0]

                # split string by separator into single articles
                docs = re.split(sep, text)

                # loop through every doc to collect metadata and full text
                for i, doc in enumerate(docs):

                    # remove white space from beginning and end of each article
                    doc = doc.strip()

                    # skip any empty docs
                    if doc == "":
                        continue

                    # create an empty dictionary that will later contain metadata keys (fieldnames) and the content for each metadata field
                    metadata_dict = {}

                    # this regular expression looks for the 2 or 3 character field codes in the document
                    regex = '(\s\s\s[A-Z]{2,3})'

                    # split up each document based on the 2-3 char metadata field codes
                    splits = re.split(regex, doc)

                    # create variables to hold metadata and content
                    key, value = '', ''

                    # cycle through each metadata element
                    for k, split in enumerate(splits):

                        # check for the SE field, which doesn't follow the same syntax as other fields
                        if re.match('^SE', split):
                            key = 'SE'
                            # print("SE")
                            value = split.strip('SE\n')

                        elif re.match('^HD', split):
                            key = 'HD'
                            value = re.search(r'HD\s*(.*)', split).group(1).strip()

                        # if we match a 2-3 char code, assign it to key
                        elif re.match(regex, split):
                            key = split.strip()
                            # print('key=', key)

                        # if we don't match a 2-3 char code assign it to value
                        else:
                            value = split.strip()
                            # print('value=',value)

                        # only add keys and values to our dictionary if they match the fieldnames we chose above

                        if key in fieldnames:
                            metadata_dict[key] = value
                    # print(metadata_dict)
                    # write each row to the csv containing all of the values that match existing fieldnames/keys
                    writer.writerow(metadata_dict)
                # output to let us know the .txt files that are being processed
                #                 print("neetu")
                print("Writing", file_id)


if __name__ == "__main__":
    #convert rtf file to txt file
    # run the following command to create a .txt file copy of each .rtf file:
    # textutil -convert txt *.rtf
    # You can also choose the path to your rtf downloads folder from your working directory
    # textutil -convert txt *.rtf

    # Construct the argument parser and parse the arguments
    parser = ArgumentParser()
    # file path of the factiva text data

    parser.add_argument("--filepath", type=str, default="./factiva/", help="factiva text data file path")

    # # CSV file name

    parser.add_argument("--processed_filename", type=str, default="factiva_metadata.csv",
                        help="csv file for processed factiva data")
    # parse arguments
    args = parser.parse_args()
    # store filepath in variable
    filepath = args.filepath
    # store filepath in variable
    csv_filename = args.processed_filename
    # call factiva_to_csv function
    factiva_to_csv(filepath, csv_filename)




