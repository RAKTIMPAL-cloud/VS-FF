import streamlit as st
import requests
import base64
import xml.etree.ElementTree as ET
import csv
import io
import pandas as pd

# Set Streamlit page config
st.set_page_config(page_title="Oracle HCM Person Search", layout="centered")

st.title("🔍 Oracle HCM Fusion – Person Search")

# Text input for user to enter a Person Number
search_input = st.text_input("Enter Person Number to search:")

# Hide credentials in production!
username = "kishore.nand@ibm.com"
password = "welcome123"

# Encode credentials
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

# SOAP API Endpoint and Headers
url = "https://iavnqy-test.fa.ocs.oraclecloud.com:443/xmlpserver/services/ExternalReportWSSService"
headers = {
    "Content-Type": "application/soap+xml; charset=utf-8",
    "Authorization": f"Basic {encoded_credentials}"
}

# SOAP Envelope
soap_request = """
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:pub="http://xmlns.oracle.com/oxp/service/PublicReportService">
   <soap:Header/>
   <soap:Body>
      <pub:runReport>
         <pub:reportRequest>
            <pub:attributeFormat>csv</pub:attributeFormat>
            <pub:flattenXML>false</pub:flattenXML>
            <pub:reportAbsolutePath>/Custom/Human Capital Management/Sample Reports/PERSON REPORT.xdo</pub:reportAbsolutePath>
            <pub:sizeOfDataChunkDownload>-1</pub:sizeOfDataChunkDownload>
         </pub:reportRequest>
      </pub:runReport>
   </soap:Body>
</soap:Envelope>
"""

@st.cache_data(show_spinner="Fetching report from Oracle Fusion...")
def fetch_report():
    response = requests.post(url, data=soap_request, headers=headers)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        report_bytes_elem = root.find('.//{http://xmlns.oracle.com/oxp/service/PublicReportService}reportBytes')
        if report_bytes_elem is not None and report_bytes_elem.text:
            decoded_csv = base64.b64decode(report_bytes_elem.text).decode("utf-8")
            return decoded_csv
    return None

# Fetch and process data
csv_data = fetch_report()
if csv_data:
    df = pd.read_csv(io.StringIO(csv_data))

    if "Person Number" in df.columns:
        # Filter by user input
        if search_input:
            filtered_df = df[df["Person Number"].astype(str).str.contains(search_input, case=False, na=False)]
            st.subheader("🔎 Search Results")
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning("No matching Person Number found.")
        else:
            st.info("Please enter a Person Number above to search.")
    else:
        st.error("The report does not contain a 'Person Number' column.")
else:
    st.error("Failed to fetch or decode the report.")

