import streamlit as st
import pandas as pd
import requests

API_URL = 'http://localhost:8000/process-data'


st.title('Upload Data and Process')

uploaded_file = st.file_uploader('Upload CSV', type=['csv'])
param1 = st.number_input('Parameter 1', value=1.0)
param2 = st.number_input('Parameter 2', value=0.0)

if uploaded_file is not None:
  df = pd.read_csv(uploaded_file).fillna(0)
  st.write('Uploaded Data:', df)

  if st.button('Submit'):
    json_data = {
      'params': {'param1': param1, 'param2': param2},
      'filename': uploaded_file.name,
      'dataframe': df.to_dict(orient='records')
    }
    response = requests.post(API_URL, json=json_data)
    print(response.json())
    if response.status_code == 200:
      st.write('message:', response.json()['message'])
    else:
      st.success(response.json().get("message"))
