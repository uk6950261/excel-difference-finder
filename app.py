import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel Difference Finder", layout="wide")

st.title("📊 Excel Difference Finder (Universal)")
st.write("Upload two Excel files and compare any column you want.")

# -------- FILE UPLOAD --------

file1 = st.file_uploader("Upload First Excel File", type=["xlsx"])
file2 = st.file_uploader("Upload Second Excel File", type=["xlsx"])

if file1 and file2:

    try:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)
    except Exception as e:
        st.error("Excel read error — check file format")
        st.stop()

    st.success("Files loaded successfully ✅")

    st.subheader("Preview")

    colA, colB = st.columns(2)
    with colA:
        st.write("File 1 Preview")
        st.dataframe(df1.head())

    with colB:
        st.write("File 2 Preview")
        st.dataframe(df2.head())

    # -------- COLUMN SELECT MODE --------

    st.subheader("Select Compare Column")

    mode = st.radio(
        "Choose how to select column:",
        ["Select from dropdown", "Type column name"]
    )

    if mode == "Select from dropdown":
        col1 = st.selectbox("Column from File 1", df1.columns)
        col2 = st.selectbox("Column from File 2", df2.columns)
    else:
        col1 = st.text_input("Column name in File 1")
        col2 = st.text_input("Column name in File 2")

    # -------- RUN COMPARE --------

    if st.button("🚀 Run Compare"):

        if col1 not in df1.columns:
            st.error("Column not found in File 1")
            st.stop()

        if col2 not in df2.columns:
            st.error("Column not found in File 2")
            st.stop()

        s1 = set(df1[col1].astype(str))
        s2 = set(df2[col2].astype(str))

        only1 = sorted(list(s1 - s2))
        only2 = sorted(list(s2 - s1))
        common = sorted(list(s1 & s2))

        st.subheader("Results")

        c1, c2, c3 = st.columns(3)
        c1.metric("Only in File 1", len(only1))
        c2.metric("Only in File 2", len(only2))
        c3.metric("Common Values", len(common))

        # -------- SHOW TABLES --------

        tab1, tab2, tab3 = st.tabs([
            "Only File 1",
            "Only File 2",
            "Common"
        ])

        with tab1:
            d1 = pd.DataFrame({col1: only1})
            st.dataframe(d1)

        with tab2:
            d2 = pd.DataFrame({col2: only2})
            st.dataframe(d2)

        with tab3:
            d3 = pd.DataFrame({"Common": common})
            st.dataframe(d3)

        # -------- DOWNLOAD --------

        out = pd.concat([
            pd.DataFrame({"Only_File1": only1}),
            pd.DataFrame({"Only_File2": only2})
        ], axis=1)

        st.download_button(
            "⬇ Download Difference Excel",
            out.to_csv(index=False),
            file_name="difference.csv"
        )

else:
    st.info("Upload both Excel files to begin.")

