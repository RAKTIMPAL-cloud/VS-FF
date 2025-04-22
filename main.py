import streamlit as st
import requests
import base64
import xml.etree.ElementTree as ET
import csv
import io
import pandas as pd

# Streamlit config
st.set_page_config(page_title="Oracle HCM Person Search", layout="centered")
st.title("🔐 Oracle HCM Fusion – Person Search")

st.markdown("Search for employees by **PERSON_NUMBER** from a BIP report.")

# --- Step 1: Get input from user ---
env_url_input = st.text_input("🌐 Oracle Environment URL (e.g. https://iavnqy-test.fa.ocs.oraclecloud.com)")
username = st.text_input("👤 Oracle Username")
password = st.text_input("🔑 Oracle Password", type="password")
search_input = st.text_input("🔍 Search by full or partial PERSON_NUMBER:")

# Proceed only if all required fields are filled
if env_url_input and username and password:

    # Construct full SOAP service endpoint URL
    full_url = env_url_input.rstrip("/") + "/xmlpserver/services/ExternalReportWSSService"

    # Encode credentials
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    # Set headers
    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
        "Authorization": f"Basic {encoded_credentials}"
    }

    # SOAP request
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

    # Fetch and cache report
    @st.cache_data(show_spinner="📥 Fetching Oracle HCM Report...")
    def fetch_report():
        response = requests.post(full_url, data=soap_request, headers=headers)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            report_bytes_elem = root.find('.//{http://xmlns.oracle.com/oxp/service/PublicReportService}reportBytes')
            if report_bytes_elem is not None and report_bytes_elem.text:
                decoded_csv = base64.b64decode(report_bytes_elem.text).decode("utf-8")
                return decoded_csv
        return None

    # Load data
    csv_data = fetch_report()
    if csv_data:
        df = pd.read_csv(io.StringIO(csv_data))

        # Check required columns
        if {"PERSON_ID", "PERSON_NUMBER"}.issubset(df.columns):
            if search_input:
                filtered_df = df[df["PERSON_NUMBER"].astype(str).str.startswith(search_input.strip())]
                st.subheader("🔎 Matching Records")
                if not filtered_df.empty:
                    st.dataframe(filtered_df, use_container_width=True)
                else:
                    st.warning("No matching PERSON_NUMBER found.")
            else:
                st.info("Enter a PERSON_NUMBER to begin search.")
        else:
            st.error("Expected columns PERSON_ID and PERSON_NUMBER not found in the report.")
    else:
        st.error("❌ Failed to retrieve or decode report from Oracle.")
else:
    st.info("Please enter the Oracle Environment URL, Username, and Password to continue.")
