import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel Reconciliation PRO", layout="wide")

st.title("📊 Excel Reconciliation PRO Tool")

# -------- Upload --------

file1 = st.file_uploader("Upload Excel File 1", type=["xlsx"])
file2 = st.file_uploader("Upload Excel File 2", type=["xlsx"])

if not file1:
    st.stop()

xls1 = pd.ExcelFile(file1)

# -------- MULTI SHEET SELECT (FILE 1) --------

sheets1 = st.multiselect(
    "Select one or more sheets from File 1",
    xls1.sheet_names
)

if not sheets1:
    st.stop()

df1_list = [xls1.parse(s) for s in sheets1]
df1 = pd.concat(df1_list, ignore_index=True)

# -------- FILE 2 SHEET --------

if file2:
    xls2 = pd.ExcelFile(file2)
    sheet2 = st.selectbox("Select sheet from File 2", xls2.sheet_names)
    df2 = xls2.parse(sheet2)
else:
    sheet2 = st.selectbox("Or select compare sheet from File 1", xls1.sheet_names)
    df2 = xls1.parse(sheet2)

st.success("Sheets loaded and combined ✅")

st.write("Combined File1 Rows:", len(df1))
st.write("Compare Sheet Rows:", len(df2))

# -------- COMMON COLUMNS --------

common_cols = list(set(df1.columns) & set(df2.columns))

st.write("Common columns available:", common_cols)

# -------- MULTI COLUMN MATCH --------

keys = st.multiselect(
    "Select match columns (Invoice + Party + Amount etc.)",
    common_cols
)

# -------- COMPARE --------

if st.button("🚀 Compare Records") and keys:

    k1 = df1[keys].astype(str)
    k2 = df2[keys].astype(str)
# ---- Remove duplicate records before compare ----
    k1 = k1.drop_duplicates()
    k2 = k2.drop_duplicates()   
    merged = k1.merge(k2, how="outer", indicator=True)

    only1 = merged[merged["_merge"] == "left_only"]
    only2 = merged[merged["_merge"] == "right_only"]

    st.subheader("Results")

    c1, c2 = st.columns(2)
    c1.metric("Only in File1 Sheets", len(only1))
    c2.metric("Only in Compare Sheet", len(only2))

    st.subheader("Missing in Compare Sheet")
    st.dataframe(only1)

    st.subheader("Missing in File1 Sheets")
    st.dataframe(only2)

    # -------- DOWNLOAD --------

    out = pd.concat([
        only1.assign(Source="Only_File1"),
        only2.assign(Source="Only_File2")
    ])

    st.download_button(
        "⬇ Download Difference Report",
        out.to_csv(index=False),
        file_name="multi_sheet_diff.csv"
    )
