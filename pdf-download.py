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
excelPath = 'GRI_2017_2020.xlsx'

# Here, specify path for folder for downloads
outputPath = 'output'
downloadsPath = 'output/dwn'

# Here, specify the name of the column with file IDs
ID = 'BRnum'

# Here, specify how many threads you want running at the same time
maxThreads = 3

# Here, specify how many files you'd want to attempt to download before the program stops
# If you want it to download all files, set the value to None
maxDownloads = 10

# Here, specify how much time to give a thread to attempt to download the file before stopping
# Time is in seconds (1 minute by default)
timeoutLimit = 60
### DO NOT EDIT BEYOND THIS POINT ###


# Program checks for already-downloaded files
existingFiles = [os.path.basename(x) for x in (glob(os.path.join(downloadsPath, '*.pdf')))]
# print(existingFiles)


### THE ACTUAL WORK ###

# Separate function for validating PDFs
def validatePDF(path):
    try:
        reader = pypdf.PdfReader(path)
        test = len(reader.pages)
        return True
    except:
        return False

# Separate function for downloading PDFs, for easier troubleshooting
def downloadPDF(downloadLink, fileID):
    try:
        if pd.isna(downloadLink) or pd.isna(fileID):
            return f"File {fileID}, no data found, skipping"

        filePath = os.path.join(downloadsPath, f"{fileID}.pdf")
        
        if os.path.exists(filePath):
            return f"File {fileID}, already exists, skipping"

        with urllib.request.urlopen(downloadLink, timeout = timeoutLimit) as reponse:
            with open(filePath, "wb") as x:
                x.write(reponse.read())

        if not validatePDF(filePath):
            os.remove(filePath)
            return f"File {fileID}, Error: not a PDF, deleting"

        return f"File {fileID} downloaded without issue"

    except Exception as e:
        return f"File {fileID}, Error: {str(e)}"


# Open the file
file = pd.read_excel(excelPath, sheet_name = 0)
# ignore rows without URLs
# fileCopy = file[file.Pdf_URL.notnull() == True]

# Check how many downloads the program is allowed to make
if maxDownloads != None:
    file = file.head(maxDownloads)

# Organize the program's tasks neatly, we only need the ID and urls
tasks = [
    (row["Pdf_URL"], row[ID])
    for _, row in file.iterrows()
]

# Fetch current DateTime to name the output textfile with
currentDateTime = datetime.now().strftime("%B %d %Y, %H.%M.%S")
textName = f"LOG - {currentDateTime}.txt"
textOutput = open(f"{outputPath}/{textName}", "x")

# Send it
with concurrent.futures.ThreadPoolExecutor(max_workers = maxThreads) as executor:
    futures = [
        executor.submit(downloadPDF, url, ID)
        for url, ID in tasks
    ]

    # Print logs in console, while also writing said logs into the output folder
    for future in concurrent.futures.as_completed(futures):
        print(future.result())

        with open(f"{outputPath}/{textName}", "a") as f:
            f.write(f"{future.result()}\n")
        

# Close program