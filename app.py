import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import random
import pandas as pd

st.set_page_config(page_title="Human Evaluation", layout="centered")

st.title("🧠 Human Evaluation of Translations")

# --- Google Sheets Setup ---
SHEET_NAME = "xnli_human_evaluation"  # Replace with your Google Sheet name
SCOPE = ["https://spreadsheets.google.com/feeds", 
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

# Load service account key
credentials = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open(SHEET_NAME).sheet1

# --- User Input ---
st.sidebar.title("Evaluator Info")
username = st.sidebar.text_input("Enter your name (required):")
if not username:
    st.warning("Please enter your name to start.")
    st.stop()

# --- Load Data from Sheet ---
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Ensure required columns exist
if "evaluated_by" not in df.columns:
    df["evaluated_by"] = ""
if "best_translation" not in df.columns:
    df["best_translation"] = ""

# --- Select Unevaluated Sample ---
unevaluated = df[df["evaluated_by"] == ""]
if len(unevaluated) == 0:
    st.success("✅ All sentences have been evaluated. Thank you!")
    st.stop()

sample = unevaluated.sample(1).iloc[0]

# --- Display the Content ---
st.subheader("🗣 Original (Gujarati):")
st.write(sample["guj"])

# st.subheader("💬 English (Reference):")
# st.write(sample["eng_Latn"])

st.markdown("---")
st.subheader("🔁 Translations to Evaluate:")

# Maintain fixed order (model → google → devnagri)
translations = [
    sample["model_output"],
    sample["Google Translate output"],
    sample["devnagri_output"]
]

# Display translations anonymously
for i, t in enumerate(translations, start=1):
    st.write(f"**Option {i}:** {t}")

# Radio buttons (only one can be selected)
choice = st.radio("Select the best translation:", ["Option 1", "Option 2", "Option 3"])

# --- Submission ---
if st.button("✅ Submit Evaluation"):
    row_index = df.index[df["id"] == sample["id"]].tolist()[0] + 2  # Google Sheets index offset

    # Update Google Sheet with evaluator name and choice
    sheet.update_cell(row_index, df.columns.get_loc("evaluated_by") + 1, username)
    sheet.update_cell(row_index, df.columns.get_loc("best_translation") + 1, choice)

    st.success("✅ Response submitted successfully!")
    st.info("You can refresh the page to evaluate another sentence.")