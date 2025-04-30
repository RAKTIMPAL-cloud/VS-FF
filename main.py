import streamlit as st
import requests
import base64
import xml.etree.ElementTree as ET
import pandas as pd
import csv
import io

# Streamlit UI
st.set_page_config(page_title="IntelliScan Report Search", layout="centered")
st.title("🧠 Oracle BIP – IntelliScan Report")

# Input fields
env_url_input = st.text_input("🌐 Oracle Environment URL (e.g. https://iavnqy-test.fa.ocs.oraclecloud.com)")
username = st.text_input("👤 Oracle Username")
password = st.text_input("🔑 Oracle Password", type="password")
keyword = st.text_input("🔍 Search IntelliScan using Keyword (p_key_word):")

# Validate inputs
if env_url_input and username and password and keyword:

    # Build full URL
    full_url = env_url_input.rstrip("/") + "/xmlpserver/services/ExternalReportWSSService"

    # Encode credentials
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    # Set SOAP headers
    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
        "Authorization": f"Basic {encoded_credentials}"
    }

    # Build SOAP payload with parameter
    soap_request = f"""
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:pub="http://xmlns.oracle.com/oxp/service/PublicReportService">
       <soap:Header/>
       <soap:Body>
          <pub:runReport>
             <pub:reportRequest>
                <pub:reportAbsolutePath>/Custom/Human Capital Management/Sample Reports/INTELLISCAN REPORT.xdo</pub:reportAbsolutePath>
                <pub:attributeFormat>csv</pub:attributeFormat>
                <pub:flattenXML>false</pub:flattenXML>
                <pub:sizeOfDataChunkDownload>-1</pub:sizeOfDataChunkDownload>
                <pub:parameterNameValues>
                   <pub:item>
                      <pub:name>p_key_word</pub:name>
                      <pub:values>
                         <pub:item>{keyword}</pub:item>
                      </pub:values>
                   </pub:item>
                </pub:parameterNameValues>
             </pub:reportRequest>
          </pub:runReport>
       </soap:Body>
    </soap:Envelope>
    """

    # Fetch report
    @st.cache_data(show_spinner="📥 Fetching IntelliScan Report...")
    def fetch_report():
        response = requests.post(full_url, data=soap_request, headers=headers)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            report_bytes_elem = root.find('.//{http://xmlns.oracle.com/oxp/service/PublicReportService}reportBytes')
            if report_bytes_elem is not None and report_bytes_elem.text:
                decoded_csv = base64.b64decode(report_bytes_elem.text).decode("utf-8")
                return decoded_csv
        return None

    csv_data = fetch_report()
    if csv_data:
        df = pd.read_csv(io.StringIO(csv_data))
        if {"OBJ_TYPE", "OBJ_NAME"}.issubset(df.columns):
            st.subheader("📄 IntelliScan Report Results")
            st.dataframe(df, use_container_width=True)
        else:
            st.error("Expected columns OBJ_TYPE and OBJ_NAME not found in the report output.")
    else:
        st.error("❌ Could not fetch or decode the report.")
        st.text("Raw Response:")
        st.code(response.content.decode('utf-8'), language='xml')
else:
    st.info("Enter Oracle URL, credentials, and keyword to run the IntelliScan search.")
