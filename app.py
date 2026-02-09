import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel Difference Finder", layout="wide")

st.title("📊 Excel Difference Finder Tool")

file1 = st.file_uploader("Upload First Excel File", type=["xlsx"])
file2 = st.file_uploader("Upload Second Excel File", type=["xlsx"])

def normalize_cols(df):
    df.columns = df.columns.str.strip()
    return df

if file1 and file2:
    try:
        df1 = normalize_cols(pd.read_excel(file1))
        df2 = normalize_cols(pd.read_excel(file2))
    except Exception as e:
        st.error(f"File read error: {e}")
        st.stop()

    st.success("Files loaded successfully")

    st.subheader("Preview File 1")
    st.dataframe(df1.head())

    st.subheader("Preview File 2")
    st.dataframe(df2.head())

    common_cols = sorted(list(set(df1.columns) & set(df2.columns)))

    mode = st.selectbox("Select Compare Mode", [
        "Invoice Difference",
        "GSTIN Difference",
        "Column Difference",
        "Full Row Difference",
        "Duplicate Finder"
    ])

    # ---------- INVOICE ----------
    if mode == "Invoice Difference":
        col = st.selectbox("Select Invoice Column", common_cols)
        only1 = df1[~df1[col].isin(df2[col])]
        only2 = df2[~df2[col].isin(df1[col])]

        st.write("Only in File 1")
        st.dataframe(only1)

        st.write("Only in File 2")
        st.dataframe(only2)

    # ---------- GSTIN ----------
    if mode == "GSTIN Difference":
        gst_cols = [c for c in common_cols if "gst" in c.lower()]
        if not gst_cols:
            st.warning("No GST column found")
        else:
            col = st.selectbox("Select GST Column", gst_cols)
            only1 = df1[~df1[col].isin(df2[col])]
            only2 = df2[~df2[col].isin(df1[col])]
            st.dataframe(only1)
            st.dataframe(only2)

    # ---------- COLUMN ----------
    if mode == "Column Difference":
        col = st.selectbox("Select Column", common_cols)
        only1 = df1[~df1[col].isin(df2[col])]
        only2 = df2[~df2[col].isin(df1[col])]
        st.write("Only in File 1")
        st.dataframe(only1)
        st.write("Only in File 2")
        st.dataframe(only2)

    # ---------- FULL ROW ----------
    if mode == "Full Row Difference":
        merged = df1.merge(df2, how="outer", indicator=True)
        st.dataframe(merged[merged["_merge"] != "both"])

    # ---------- DUPLICATE ----------
    if mode == "Duplicate Finder":
        col = st.selectbox("Select Column for Duplicate Check", df1.columns)
        dups = df1[df1.duplicated(col, keep=False)]
        st.dataframe(dups)

else:
    st.info("Upload both Excel files to begin")
