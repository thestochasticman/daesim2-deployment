from PIL import Image
import streamlit as st
import pandas as pd
import requests
import base64
import io

def handle_nans(df: pd.DataFrame) -> pd.DataFrame:
  for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
      df[col] = df[col].fillna(0)
    elif pd.api.types.is_bool_dtype(df[col]):
      df[col] = df[col].fillna(False)
    elif pd.api.types.is_datetime64_any_dtype(df[col]):
      df[col] = df[col].fillna("1970-01-01")
    else:
      df[col] = df[col].fillna("missing")
  return df

API_BASE = "http://localhost:8000"

st.title("DAESIM File Upload & Job Submission")

# --- Upload CSV Section ---
st.header("Upload CSV to Gadi")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
param1 = st.number_input("Parameter 1", value=1.0)
param2 = st.number_input("Parameter 2", value=0.0)

if uploaded_file:
  df = pd.read_csv(uploaded_file)
  df = handle_nans(df)
  st.write("Preview of uploaded file:", df)

  if st.button("Upload to Gadi"):
    json_data = {
      "params": {"param1": param1, "param2": param2},
      "filename": uploaded_file.name,
      "dataframe": df.to_dict(orient="records")
    }
    response = requests.post(f"{API_BASE}/upload-to-gadi", json=json_data)

    if response.status_code == 200:
      st.success(response.json().get("message"))
    else:
      st.error("Upload failed.")
      st.json(response.json())

# --- Submit PBS Job Section ---
st.header("🚀 Submit PBS Job for Uploaded File")

job_filename = st.text_input("Enter the exact filename to process (e.g., `my_data.csv`)")

if st.button("Submit Job"):
  if not job_filename:
    st.warning("Please enter a filename.")
  else:
    response = requests.post(f"{API_BASE}/submit-job", json={"filename": job_filename})

    if response.status_code == 200:
      st.success(f"PBS job submitted for `{job_filename}`")
      st.json(response.json())
    else:
      st.error("Failed to submit job.")
      st.json(response.json())



# Fetch and Plot Section
st.header("📊 View Processed Results and Plot")
filename_input = st.text_input("Enter result filename (e.g. `myfile.csv`)")
if st.button("Fetch and Plot Result"):
	if filename_input:
		resp = requests.get(f"{API_BASE}/get-result-and-plot", params={"filename": filename_input})
		data = resp.json()
		if "plot_image_base64" in data:
			st.success(data["message"])
			df_result = pd.DataFrame(data["data"])
			st.dataframe(df_result)
			img_data = base64.b64decode(data["plot_image_base64"])
			image = Image.open(io.BytesIO(img_data))
			st.image(image, caption="📈 Simulation Output")
		else:
			st.error("❌ Failed to load result.")
			st.json(data)
