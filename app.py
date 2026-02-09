import streamlit as st
st.markdown("""
<meta name="google-site-verification" content="RL50Ymf_K5HFmDukgYPEKxwVD-UHlvx659nLZLlsGQ4" />
""", unsafe_allow_html=True)
import pandas as pd
import difflib
import numpy as np

st.set_page_config(page_title="Excel Difference ULTRA", layout="wide")

st.title("📊 Excel Difference & Reconciliation ULTRA")

# =====================
# Upload
# =====================

file1 = st.file_uploader("Upload Excel File 1", type=["xlsx"])
file2 = st.file_uploader("Upload Excel File 2", type=["xlsx"])

if not file1 or not file2:
    st.stop()

xls1 = pd.ExcelFile(file1)
xls2 = pd.ExcelFile(file2)

# =====================
# Smart Sheet Handling
# =====================

if len(xls1.sheet_names) == 1:
    df1 = xls1.parse(xls1.sheet_names[0])
else:
    s1 = st.multiselect("Select sheet(s) from File1", xls1.sheet_names)
    if not s1:
        st.stop()
    df1 = pd.concat([xls1.parse(s) for s in s1], ignore_index=True)

if len(xls2.sheet_names) == 1:
    df2 = xls2.parse(xls2.sheet_names[0])
else:
    s2 = st.selectbox("Select sheet from File2", xls2.sheet_names)
    df2 = xls2.parse(s2)

st.success("Sheets loaded ✅")

common_cols = list(set(df1.columns) & set(df2.columns))

# =====================
# Mode
# =====================

mode = st.radio(
    "Compare Mode",
    ["⚡ Basic Column", "🧠 Pro Record"]
)

# =====================================================
# BASIC MODE
# =====================================================

if mode.startswith("⚡"):

    col = st.selectbox("Select column", common_cols)

    if st.button("Run Basic Compare"):

        s1 = df1[col].astype(str)
        s2 = df2[col].astype(str)

        set1 = set(s1)
        set2 = set(s2)

        only1 = df1[s1.isin(set1 - set2)]
        only2 = df2[s2.isin(set2 - set1)]

        dup = pd.concat([
            df1[df1[col].duplicated()],
            df2[df2[col].duplicated()]
        ])

        a,b,c = st.columns(3)
        a.metric("Only File1", len(only1))
        b.metric("Only File2", len(only2))
        c.metric("Duplicates", len(dup))

        st.dataframe(only1)
        st.dataframe(only2)

        st.download_button("Download File1 Diff", only1.to_csv(index=False), "file1_diff.csv")
        st.download_button("Download File2 Diff", only2.to_csv(index=False), "file2_diff.csv")
        st.download_button("Download Duplicates", dup.to_csv(index=False), "duplicates.csv")

# =====================================================
# PRO MODE
# =====================================================

else:

    keys = st.multiselect("Match columns (Invoice + Party + etc.)", common_cols)

    fuzzy_on = st.checkbox("Enable fuzzy text match")
    tol = st.number_input("Amount tolerance (numeric)", 0.0, 1000000.0, 0.0)

    if st.button("Run Pro Compare") and keys:

        k1 = df1[keys].copy()
        k2 = df2[keys].copy()

        # ---------- FUZZY NORMALIZE ----------
        if fuzzy_on:
            for c in keys:
                k1[c] = k1[c].astype(str).str.lower().str.replace(r'\W+', '', regex=True)
                k2[c] = k2[c].astype(str).str.lower().str.replace(r'\W+', '', regex=True)

        # ---------- NUMERIC TOLERANCE ----------
        for c in keys:
            try:
                k1[c] = pd.to_numeric(k1[c])
                k2[c] = pd.to_numeric(k2[c])
                if tol > 0:
                    k1[c] = (k1[c] / tol).round() * tol
                    k2[c] = (k2[c] / tol).round() * tol
            except:
                pass

        dup1 = k1[k1.duplicated()]
        dup2 = k2[k2.duplicated()]

        k1 = k1.drop_duplicates().astype(str)
        k2 = k2.drop_duplicates().astype(str)

        merged = k1.merge(k2, how="outer", indicator=True)

        only1 = merged[merged["_merge"] == "left_only"]
        only2 = merged[merged["_merge"] == "right_only"]
        both = merged[merged["_merge"] == "both"]

        # ---------- DASHBOARD ----------

        st.subheader("📊 Dashboard")

        a,b,c = st.columns(3)
        a.metric("File1 Records", len(k1))
        b.metric("File2 Records", len(k2))
        c.metric("Matched", len(both))

        d,e = st.columns(2)
        d.metric("Only File1", len(only1))
        e.metric("Only File2", len(only2))

        # ---------- SHOW CLEAN ----------

        st.subheader("Only in File1")
        st.dataframe(only1[keys])

        st.subheader("Only in File2")
        st.dataframe(only2[keys])

        # ---------- VALUE MISMATCH ----------

        st.subheader("🟡 Value Mismatch Check")

        cmp = df1.merge(df2, on=keys, suffixes=("_f1","_f2"))

        for c in keys:
            c1 = c + "_f1"
            c2 = c + "_f2"
            if c1 in cmp.columns and c2 in cmp.columns:
                bad = cmp[cmp[c1] != cmp[c2]]
                if len(bad):
                    st.write("Mismatch:", c)
                    st.dataframe(bad[[*keys, c1, c2]])

        # ---------- DOWNLOADS ----------

        st.download_button(
            "Download Pro Diff",
            pd.concat([only1[keys], only2[keys]]).to_csv(index=False),
            "pro_diff.csv"
        )

        st.download_button(
            "Download Duplicates",
            pd.concat([dup1, dup2]).to_csv(index=False),
            "duplicates.csv"
        )
