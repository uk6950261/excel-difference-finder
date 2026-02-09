import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel Difference Tool", layout="wide")

st.title("📊 Excel Difference Finder")

# -------- Upload --------

file1 = st.file_uploader("Upload Excel File 1", type=["xlsx"])
file2 = st.file_uploader("Upload Excel File 2", type=["xlsx"])

if not file1 or not file2:
    st.stop()

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

st.success("Files loaded ✅")

# -------- Mode --------

mode = st.radio(
    "Select Compare Mode",
    ["⚡ Basic (Single Column)", "🧠 Pro (Full Record Merge)"]
)

common_cols = list(set(df1.columns) & set(df2.columns))

# =====================================================
# ⚡ BASIC MODE
# =====================================================

if mode.startswith("⚡"):

    key = st.selectbox("Select column to compare", common_cols)

    if st.button("Find Difference"):

        s1 = df1[key].astype(str)
        s2 = df2[key].astype(str)

        dup = pd.concat([
            df1[df1[key].duplicated()],
            df2[df2[key].duplicated()]
        ])

        set1 = set(s1)
        set2 = set(s2)

        only1 = sorted(list(set1 - set2))
        only2 = sorted(list(set2 - set1))

        df_only1 = df1[df1[key].astype(str).isin(only1)]
        df_only2 = df2[df2[key].astype(str).isin(only2)]

        c1,c2,c3 = st.columns(3)
        c1.metric("Only File1", len(df_only1))
        c2.metric("Only File2", len(df_only2))
        c3.metric("Duplicates", len(dup))

        st.subheader("Only in File1")
        st.dataframe(df_only1)

        st.subheader("Only in File2")
        st.dataframe(df_only2)

        st.subheader("Duplicates")
        st.dataframe(dup)

# =====================================================
# 🧠 PRO MERGE MODE
# =====================================================

else:

    keys = st.multiselect(
        "Select columns to match records",
        common_cols
    )

    if st.button("Run Pro Compare") and keys:

        k1 = df1[keys].astype(str).drop_duplicates()
        k2 = df2[keys].astype(str).drop_duplicates()

        merged = k1.merge(k2, how="outer", indicator=True)

        only1 = merged[merged["_merge"] == "left_only"]
        only2 = merged[merged["_merge"] == "right_only"]

        c1,c2 = st.columns(2)
        c1.metric("Only File1 Records", len(only1))
        c2.metric("Only File2 Records", len(only2))

        st.subheader("Missing in File2")
        st.dataframe(only1)

        st.subheader("Missing in File1")
        st.dataframe(only2)

        st.download_button(
            "⬇ Download Pro Difference",
            pd.concat([only1, only2]).to_csv(index=False),
            "pro_diff.csv"
        )
