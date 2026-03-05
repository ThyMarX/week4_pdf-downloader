# TH: 

import pytest
from pdf_download import downloadPDF

def test_downloadPDF(mocker):
    # Mock request.get
    mock_get = mocker.patch("pdf_download.urllib.request.urlopen")

    # Set return values
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = True

    # Call function
    result = downloadPDF("BR50056", "http://www.bseindia.com/bseplus/AnnualReport/500002/5000021216.pdf", None, "")

    # Assertions
    assert result == True
    mock_get.assert_called_once_with("http://www.bseindia.com/bseplus/AnnualReport/500002/5000021216.pdf")