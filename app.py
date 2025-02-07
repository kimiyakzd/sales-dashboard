import streamlit as st
import pandas as pd
import time
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

# 📂 کش کردن داده‌ها برای افزایش سرعت
@st.cache_data
def load_data():
    return pd.read_excel("test.xlsx")  # نام فایل اکسل را تغییر دهید

# 🖥 تنظیم صفحه
st.set_page_config(layout="wide", page_title="📊 داشبورد فروش و پورسانت")

# 🎨 استایل سفارشی برای افزایش خوانایی جدول
st.markdown("""
    <style>
        .big-font { font-size:50px !important; text-align: center; color: #222; font-weight: bold; }
        .stApp { background-color: #f8f9fa; }
        .ag-theme-streamlit {
            --ag-header-background-color: #007bff !important;
            --ag-header-text-color: white !important;
            --ag-odd-row-background-color: #f0f8ff !important;
            --ag-even-row-background-color: #e6f7ff !important;
            --ag-font-size: 20px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# 📂 خواندن داده‌ها
data = load_data()

# 📍 انتخاب شعبه
branches = data["Branch"].unique()
selected_branch = st.selectbox("🏢 لطفاً شعبه مورد نظر را انتخاب کنید:", branches)

# 🔍 فیلتر کردن داده‌ها بر اساس شعبه
filtered_data = data[data["Branch"] == selected_branch]

# 📋 گرفتن لیست فروشندگان
sellers = filtered_data["Name"].unique()

# ❗ بررسی اینکه آیا فروشنده‌ای در داده‌ها وجود دارد یا نه
if len(sellers) == 0:
    st.warning("⚠ هیچ فروشنده‌ای در این شعبه یافت نشد!")
    st.stop()

# 🔄 مقدار اولیه session_state برای نمایش فروشنده‌ها
if "seller_index" not in st.session_state:
    st.session_state.seller_index = 0

# 🎯 دریافت فروشنده فعلی
current_seller = sellers[st.session_state.seller_index]

# 📊 فیلتر داده‌های فروشنده انتخاب‌شده
seller_data = filtered_data[filtered_data["Name"] == current_seller].copy()

# 🛑 بررسی اینکه داده‌های فروشنده خالی نباشد
if seller_data.empty:
    st.warning("⚠ هیچ داده‌ای برای این فروشنده موجود نیست!")
    st.stop()

# ✅ بررسی وجود ستون‌های لازم
required_columns = {"Ctg", "Sale", "Tgt", "%Achivement", "commesion"}
if not required_columns.issubset(seller_data.columns):
    st.error("🚨 برخی از ستون‌های موردنیاز در داده‌ها وجود ندارند!")
    st.stop()

# 🔢 تبدیل درصد تحقق هدف به مقدار درصدی ایمن و گرد کردن اعداد
seller_data["%Achivement"] = pd.to_numeric(
    seller_data["%Achivement"], errors="coerce"
) * 100  # تبدیل درصد از مقدار اعشاری
seller_data["%Achivement"] = seller_data["%Achivement"].round(2).astype(str) + " %"

# 🔢 اضافه کردن جداکننده هزارگان به `Sale`، `Tgt` و `commesion`
for col in ["Sale", "Tgt", "commesion"]:
    seller_data[col] = seller_data[col].apply(lambda x: f"{x:,.0f}")

# 🏷 نمایش نام فروشنده
st.markdown(f"<p class='big-font'>📌 فروشنده: {current_seller}</p>", unsafe_allow_html=True)

# 📌 نمایش جدول اطلاعات با رنگ‌بندی زیبا
gb = GridOptionsBuilder.from_dataframe(seller_data[["Ctg", "Sale", "Tgt", "%Achivement", "commesion"]])
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True)
gb.configure_grid_options(domLayout='autoHeight')  # نمایش کل داده‌ها بدون اسکرول
grid_options = gb.build()

st.write("📋 **جدول اطلاعات فروشنده:**")
AgGrid(
    seller_data[["Ctg", "Sale", "Tgt", "%Achivement", "commesion"]],
    gridOptions=grid_options,
    fit_columns_on_grid_load=True,  # تنظیم خودکار عرض ستون‌ها
    height=min(800, len(seller_data) * 40),  # افزایش ارتفاع جدول
    theme="streamlit",  # 🎨 تم رنگی جذاب
)

# 📊 نمودار درصد تحقق هدف
y_values = pd.to_numeric(seller_data["%Achivement"].str.replace(" %", ""), errors="coerce")

fig = px.bar(
    seller_data,
    x="Ctg",
    y=y_values,
    title="📈 درصد تحقق هدف برای هر کتگوری",
    labels={"y": "درصد تحقق هدف", "Ctg": "دسته‌بندی"},
    color=y_values,
    color_continuous_scale="Blues"
)
st.plotly_chart(fig, use_container_width=True)

# 🔄 ایجاد دکمه برای تغییر دستی فروشنده
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("⏭ فروشنده بعدی"):
        st.session_state.seller_index = (st.session_state.seller_index + 1) % len(sellers)
        st.rerun()

# 🔄 به‌روزرسانی خودکار هر ۱۰ ثانیه
time.sleep(10)
st.session_state.seller_index = (st.session_state.seller_index + 1) % len(sellers)
st.rerun()
