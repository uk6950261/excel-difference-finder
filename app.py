import streamlit as st
import pandas as pd
import difflib
import string

st.set_page_config(page_title="Smart Excel Difference Finder", layout="wide")

st.title("📊 Smart Excel Difference Finder")
st.write("Upload 2 Excel files → Type column letter/name/keyword → Get differences")

# -------- Upload --------

f1 = st.file_uploader("Upload First Excel", type=["xlsx"])
f2 = st.file_uploader("Upload Second Excel", type=["xlsx"])

if not (f1 and f2):
    st.stop()

df1 = pd.read_excel(f1)
df2 = pd.read_excel(f2)

st.success("Files loaded ✅")

st.write("File1 columns:", list(df1.columns))
st.write("File2 columns:", list(df2.columns))

# -------- Smart Column Finder --------

user_key = st.text_input("Type column letter OR name OR keyword")

def col_from_letter(letter, cols):
    i = string.ascii_uppercase.find(letter.upper())
    if 0 <= i < len(cols):
        return cols[i]
    return None

def fuzzy(keyword, cols):
    m = difflib.get_close_matches(
        keyword.lower(),
        [c.lower() for c in cols],
        n=1,
        cutoff=0.4
    )
    if m:
        for c in cols:
            if c.lower() == m[0]:
                return c
    return None

def smart_find(key, cols):
    return (
        col_from_letter(key, cols)
        or (key if key in cols else None)
        or fuzzy(key, cols)
    )

# -------- Run Compare --------

if st.button("🚀 Compare") and user_key:

    c1 = smart_find(user_key, df1.columns)
    c2 = smart_find(user_key, df2.columns)

    if not c1 or not c2:
        st.error("No matching column found")
        st.stop()

    st.success(f"Matched → {c1}  |  {c2}")

    s1 = set(df1[c1].astype(str))
    s2 = set(df2[c2].astype(str))

    only1 = sorted(list(s1 - s2))
    only2 = sorted(list(s2 - s1))
    common = sorted(list(s1 & s2))

    a,b,c = st.columns(3)
    a.metric("Only File1", len(only1))
    b.metric("Only File2", len(only2))
    c.metric("Common", len(common))

    st.subheader("Only in File1")
    st.dataframe(pd.DataFrame({c1: only1}))

    st.subheader("Only in File2")
    st.dataframe(pd.DataFrame({c2: only2}))

# -------- Row Compare (auto) --------

st.subheader("🧾 Row Difference (Auto All Common Columns)")

common_cols = list(set(df1.columns) & set(df2.columns))

if st.button("Compare Full Rows"):

    r1 = df1[common_cols].astype(str)
    r2 = df2[common_cols].astype(str)

    merged = r1.merge(r2, how="outer", indicator=True)
    diff = merged[merged["_merge"] != "both"]

    st.metric("Row Differences", len(diff))
    st.dataframe(diff)

