import streamlit as st
import pandas as pd
import os
import jdatetime
from datetime import datetime
from babel.numbers import format_currency

# مسیر فایل و پوشه‌ها
DATA_FILE = "data.xlsx"
FACTOR_FOLDER = "factors"

if not os.path.exists(FACTOR_FOLDER):
    os.makedirs(FACTOR_FOLDER)

# اگر فایل اکسل وجود ندارد، ایجادش کن
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "پروژه", "تاریخ", "نوع", "شرح", "استادکار/فروشگاه", 
        "مبلغ", "وضعیت پرداخت", "نوع پرداخت", "شماره", "فاکتور"
    ])
    df_init.to_excel(DATA_FILE, index=False)

# بارگذاری داده‌ها
df = pd.read_excel(DATA_FILE)

st.set_page_config(layout="wide")
st.title("🔢 سیستم مدیریت مالی پروژه‌های معماری")

# نمایش پروژه‌ها
projects = df["پروژه"].dropna().unique().tolist()
selected_project = st.selectbox("🔍 انتخاب پروژه برای مشاهده گزارش:", options=[""] + projects)

if selected_project:
    st.subheader(f"📊 گزارش پروژه: {selected_project}")
    filtered = df[df["پروژه"] == selected_project]

    # استادکارها
    names = filtered["استادکار/فروشگاه"].dropna().unique()

    for name in names:
        sub = filtered[filtered["استادکار/فروشگاه"] == name]
        total = sub[sub["نوع"] == "هزینه"]["مبلغ"].sum()
        paid = sub[sub["نوع"] == "دریافتی"]["مبلغ"].sum()
        remain = total - paid
        with st.expander(f"🧱 {name}"):
            st.dataframe(sub[["تاریخ", "نوع", "شرح", "مبلغ", "نوع پرداخت", "شماره"]])
            st.markdown(f"""
                💰 مجموع هزینه‌ها: {format_currency(total, 'IRR', locale='fa_IR')}  
                💵 مجموع پرداختی‌ها: {format_currency(paid, 'IRR', locale='fa_IR')}  
                🧾 مانده: **{format_currency(remain, 'IRR', locale='fa_IR')}**
            """)

    # مجموع کل پروژه
    cost_all = filtered[filtered["نوع"] == "هزینه"]["مبلغ"].sum()
    paid_all = filtered[filtered["نوع"] == "دریافتی"]["مبلغ"].sum()
    remain_all = cost_all - paid_all
    st.divider()
    st.subheader("📌 جمع کل پروژه")
    st.markdown(f"""
        💰 مجموع هزینه‌ها: {format_currency(cost_all, 'IRR', locale='fa_IR')}  
        💵 مجموع پرداختی‌ها: {format_currency(paid_all, 'IRR', locale='fa_IR')}  
        🔻 مانده کل: **{format_currency(remain_all, 'IRR', locale='fa_IR')}**
    """)

st.divider()
st.subheader("➕ ثبت تراکنش جدید")

with st.form("form"):
    project = st.text_input("📁 نام پروژه")
    now = jdatetime.date.today()
    date = st.text_input("📅 تاریخ (به‌صورت 1403/05/01)", value=str(now))
    type_ = st.radio("نوع تراکنش:", ["هزینه", "دریافتی"])
    description = st.text_input("📝 شرح")
    name = st.text_input("👷‍♂️ استادکار / فروشگاه")
    amount = st.number_input("💸 مبلغ (تومان)", min_value=0)
    payment_status = st.selectbox("وضعیت پرداخت از سمت کارفرما:", ["نقد", "چک"])
    payment_type = st.text_input("نوع پرداخت / توضیح", placeholder="مثلاً بابت طراحی، خرید آهن، دستمزد گچ‌کار و ...")
    ref_number = st.text_input("🔢 شماره کارت / چک / ارجاع")
    factor_file = st.file_uploader("🧾 آپلود فاکتور", type=["jpg", "jpeg", "png", "pdf"])
    submitted = st.form_submit_button("✅ ثبت")

    if submitted:
        filename = ""
        if factor_file:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{factor_file.name}"
            with open(os.path.join(FACTOR_FOLDER, filename), "wb") as f:
                f.write(factor_file.read())

        new_data = pd.DataFrame([{
            "پروژه": project,
            "تاریخ": date,
            "نوع": type_,
            "شرح": description,
            "استادکار/فروشگاه": name,
            "مبلغ": amount,
            "وضعیت پرداخت": payment_status,
            "نوع پرداخت": payment_type,
            "شماره": ref_number,
            "فاکتور": filename
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("✅ تراکنش با موفقیت ثبت شد. صفحه را رفرش کنید.")

