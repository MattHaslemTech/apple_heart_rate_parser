from bs4 import BeautifulSoup
from datetime import datetime

import os 
import csv 
import zipfile

def main():

    # Get file locations

    # Zipped file to extract
    zipped_file_exists = False 
    while not zipped_file_exists:
        print("\nEnter zipped file location:")

        zipped_file_loc = input()
        # zipped_file_loc = "export2.zip"

        if os.path.exists(zipped_file_loc): 
            if zipped_file_loc.split('.')[-1] == "zip":
                print("Found folder: " + zipped_file_loc)
                zipped_folder_name = os.path.basename(zipped_file_loc).split('/')[-1].split('.zip')[0]
                zipped_file_exists = True
            else:
                print("Please enter a .zip file.")
        else: 
            print("File doesn't exist")


    # Where to print CSV results
    csv_file_exists = True 
    while csv_file_exists:
        print("\nEnter name of CSV results file:")

        csv_file_loc = input()

        if not os.path.exists(csv_file_loc): 
            
            # Make sure it's a csv file 
            if csv_file_loc.split('.')[-1] == "csv":
                csv_file_exists = False
            else:
                print("Please enter a CSV file.")

        # If the file already exists
        else: 
            print("That file already exists.")

    unzipped_folder_loc = "res/" + zipped_folder_name

    print("Folder location : " + unzipped_folder_loc)
    # Extract the files
    with zipfile.ZipFile(zipped_file_loc, 'r') as zip_ref:
        zip_ref.extractall(unzipped_folder_loc)

    

    # Find the xml file in the unzipped folder
    xml_file = unzipped_folder_loc + "/" + os.listdir(unzipped_folder_loc)[0] + "/export_cda.xml"
    print("XML FILE : " + xml_file)
    if not os.path.exists(xml_file):
        print("export_cda file not found!")
        return


    # Reading the data inside the xml
    print("Reading file...")
    with open(xml_file, 'r') as f:
        data = f.read()
    
    print("Parsing XML file...")

    Bs_data = BeautifulSoup(data, "xml")

    # find first element that has heart rate type
    initial_tag = Bs_data.find('type', string="HKQuantityTypeIdentifierHeartRate")

    # Get the entry element that holds all the heart rate observations 
    parent_entry = initial_tag.find_parent("entry")

    # Grab all the observations 
    observations = parent_entry.find_all('observation')


    print("Gathering data from " + str(len(observations)) + " observations...")    

    data_res = []

    # Get observation data
    for obs in observations:

        # Get the time
        time_el = obs.findChild('effectiveTime')
        low_time = time_el.findChild('low')
        time_val = datetime.strptime(low_time.get('value'), '%Y%m%d%H%M%S%z')
        time_val = time_val.strftime("%m/%d/%Y %H:%M:%S")

        # Get the heartrate value
        text_el = obs.findChild('text')
        val = text_el.findChild('value').text

        temp_val = [time_val, val]

        data_res.append(temp_val)



    # Generate csv file
    fields = ["Time", "Heartrate"]
    with open(csv_file_loc, 'w', newline='') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(data_res)

    print("\n Results Complete!")
    print("\n Results can be found in " + csv_file_loc)

if __name__ == "__main__":
    main()