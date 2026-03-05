### PREP WORK ###

# Install any tools you don't have
# To do so, these following commands can be run on a command prompt
# pip install pandas
# pip install pypdf
# pip install openpyxl

# Import all necessary tools
import pandas as pd
import pypdf
import os
import urllib.request
import concurrent.futures
from datetime import datetime
from glob import glob

# Column with the links MUST be called 'Pdf_URL'
# Files will take on the name of their ID, eg. 'BR50041.pdf'


### EDIT FROM HERE ###
# Here, specify path for file with URLs
excelPath = 'GRI_2017_2020.xlsx'    # TH: changed a little

# Here, specify path for folder for downloads 
outputPath = 'output'               # TH: changed a little
downloadsPath = 'output/dwn'        # TH: changed a little
# If the excel file and the output folder AREN'T in the same folder as pdf-download.py script, and the dwn folder isn't also inside of the output folder, 
# then you need to specify their direct path from the C drive, for example: '''excelPath = "C:\Min Mappe\Kode Stuff\PDF-downloader\Test og report\week4_pdf-downloader\GRI_2017_2020.xlsx"'''

# Here, specify the name of the column with file ID, link1 and link2
ID = 'BRnum'
link1 = 'Pdf_URL'                   # TH: added
link2 = 'Report Html Address'       # TH: added

# Here, specify how many threads you want running at the same time
maxThreads = 3

# Here, specify how many files you'd want to attempt to download before the program stops
# If you want it to download all files, set the value to None
maxDownloads = 20

# Here, specify how much time to give a thread to attempt to download the file before stopping
# Time is in seconds (1 minute by default)
timeoutLimit = 60
### DO NOT EDIT BEYOND THIS POINT ###


# Program checks for already-downloaded files       TH: Isn't used
#existingFiles = [os.path.basename(x) for x in (glob(os.path.join(downloadsPath, '*.pdf')))]

# TH: Counters that'll tell you how many of each happened during the program
testCntr1 = 0       # File was downloaded from link1
testCntr2 = 0       # File was downloaded from link2
testCntr3 = 0       # File already existed
testCntr4 = 0       # Link1 had an error and link2 is empty
testCntr5 = 0       # Both link1 and link2 had an error

### THE ACTUAL WORK ###

# Separate function for validating PDFs
def validatePDF(path):
    try:
        reader = pypdf.PdfReader(path)
        #test = len(reader.pages)
        return True
    except:
        return False

# Separate function for downloading PDFs, for easier troubleshooting
def downloadPDF(fileID, link1, link2, erMsg1):      # TH: add functionality so it checks link2 if link1 doesn't work
    global testCntr1
    global testCntr2
    global testCntr3
    global testCntr4
    global testCntr5

    # # TH: Test time to see how long it takes (remember to note maxThreads and such first)
    # if testCntr1+testCntr2+testCntr3+testCntr4+testCntr5 % 1000 == 0:
    #     print(f'\n\{testCntr1+testCntr2+testCntr3+testCntr4+testCntr5} rows proccessed so far at: {datetime.now()}.\n')

    try:
        if pd.isna(link1) or pd.isna(fileID):
            raise Exception(f"1: No data found: Skipping")      # TH: made it a raise Exception

        filePath = os.path.join(downloadsPath, f"{fileID}.pdf")
        
        if os.path.exists(filePath):
            testCntr3 += 1
            return f"File {fileID}, IAD, Is already downloaded: Skipping"  # TH: we don't need to check link2 if the file already exists

        with urllib.request.urlopen(link1, timeout = timeoutLimit) as reponse:
            with open(filePath, "wb") as x:
                x.write(reponse.read())

        if not validatePDF(filePath):
            os.remove(filePath)
            raise Exception(f"3: Not a PDF: Deleting")          # TH: made it a raise Exception
        
        if link2 == 'Testing link2':
            testCntr2 += 1
            return f"File {fileID}, YES, Downloaded without issue through link2, Link1 error: {str(erMsg1)}"
        else:
            testCntr1 += 1
            return f"File {fileID}, YES, Downloaded without issue through link1"

    except Exception as e:                # TH: the following now happens ALSO when the other errors occurs
        if pd.isna(link2):                # TH: If link1 failed and there's no link2
            testCntr4 += 1
            return f"File {fileID}, no, Link 1 Error: {str(e),}. Link 2 Error: No data found: Skipping"
        elif link2 == "Testing link2":                           # TH: If we've just tried link2
            testCntr5 += 1
            return f"File {fileID}, no, Link 1 Error: {str(erMsg1)}, Link 2 Error: {str(e)}"            
        else:                                                   # TH: If link1 failed and there IS a link2
            return downloadPDF(fileID, link2, "Testing link2", e)


# Open the file         MAKE THIS AND BELOW INTO ONE HANDLE_LIST() FUNCTION?? 
file = pd.read_excel(excelPath, sheet_name = 0)
# implement functionality to ignore the unwanted rows to save time?

# Check how many downloads the program is allowed to make
if maxDownloads != None:
    file = file.head(maxDownloads)

# Organize the program's tasks neatly, we only need the ID and urls
tasks = [
    (row[ID], row[link1], row[link2])       # TH: added link2 and changed structure
    for _, row in file.iterrows()
]                     # MAKE THIS AND ABOVE INTO ONE FUCNTION??

# Fetch current DateTime to name the output textfile with
currentDateTime = datetime.now().strftime("%B %d %Y, %H.%M.%S")
textName = f"LOG - {currentDateTime}.csv"           # TH: changed to cvs, so it can be opened in excel
textOutput = open(f"{outputPath}/{textName}", "x")

# Send it
if __name__ == "__main__": 
    with concurrent.futures.ThreadPoolExecutor(max_workers = maxThreads) as executor:
        futures = [
            executor.submit(downloadPDF, ID, link1, link2, "")
            for ID, link1, link2 in tasks
        ]

        # Print logs in console, while also writing said logs into the output folder
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

            with open(f"{outputPath}/{textName}", "a") as f:
                f.write(f"{future.result()}\n")
    
    # # TH: Test how long it takes (remember to note maxThreads and such first)
    # print(f'\nScript finished at: {datetime.now()}.\n')

    # TH: Counters to check everything happens as expected
    print(f'\nDownloaded from link1: {testCntr1}, Downloaded from link2: {testCntr2}, Already exists: {testCntr3}. Total files in dwn folder: {testCntr1+testCntr2+testCntr3}')
    print(f'Link1 error and no link2: {testCntr4}, Link1 and link2 error: {testCntr5}. Total rows from the excel file handled: {testCntr1+testCntr2+testCntr3+testCntr4+testCntr5}\n')
# Close program

# TH Notes:
# Since i included link2 funktionality, the following error message shows up in the terminal:
#   invalid pdf header: b'<!DOC'
#   EOF marker not found
# The terminal message does not come from the "print(future.result())" line.
#    