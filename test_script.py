# TH: My own way of making unit tests:


import pdf_download as pdf

# ### UNIT TESTS ###
def test_excel_row():
    print(pdf.downloadPDF("BR50056", "http://www.bseindia.com/bseplus/AnnualReport/500002/5000021216.pdf", None, ""))

def test_validatePDF():
    print(pdf.validatePDF("output\dwn\BR52437.pdf"))

# ### CHANGE WHICH TEST THIS TEST_SCRIPT SHOULD RUN HERE ###
if __name__ == "__main__": 
    test_excel_row()



