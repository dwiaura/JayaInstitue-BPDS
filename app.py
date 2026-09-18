import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Prediksi Dropout Mahasiswa - Jaya Jaya Institut", page_icon="🎓", layout="wide")


@st.cache_resource
def load_artifacts():
    model = joblib.load("model/dropout_model.joblib")
    scaler = joblib.load("model/scaler.joblib")
    feature_columns = joblib.load("model/feature_columns.joblib")
    threshold = joblib.load("model/decision_threshold.joblib")
    return model, scaler, feature_columns, threshold


model, scaler, feature_columns, threshold = load_artifacts()

MARITAL_STATUS = {
    "Single": 1, "Married": 2, "Widower": 3, "Divorced": 4,
    "Facto Union": 5, "Legally Separated": 6,
}

APPLICATION_MODE = {
    "1st phase - general contingent": 1, "Ordinance No. 612/93": 2,
    "1st phase - special contingent (Azores Island)": 5,
    "Holders of other higher courses": 7, "Ordinance No. 854-B/99": 10,
    "International student (bachelor)": 15,
    "1st phase - special contingent (Madeira Island)": 16,
    "2nd phase - general contingent": 17, "3rd phase - general contingent": 18,
    "Ordinance No. 533-A/99, item b2) (Different Plan)": 26,
    "Ordinance No. 533-A/99, item b3 (Other Institution)": 27,
    "Over 23 years old": 39, "Transfer": 42, "Change of course": 43,
    "Technological specialization diploma holders": 44,
    "Change of institution/course": 51, "Short cycle diploma holders": 53,
    "Change of institution/course (International)": 57,
}

COURSE = {
    "Biofuel Production Technologies": 33, "Animation and Multimedia Design": 171,
    "Social Service (evening attendance)": 8014, "Agronomy": 9003,
    "Communication Design": 9070, "Veterinary Nursing": 9085,
    "Informatics Engineering": 9119, "Equinculture": 9130, "Management": 9147,
    "Social Service": 9238, "Tourism": 9254, "Nursing": 9500, "Oral Hygiene": 9556,
    "Advertising and Marketing Management": 9670, "Journalism and Communication": 9773,
    "Basic Education": 9853, "Management (evening attendance)": 9991,
}

QUALIFICATION = {
    "Secondary education": 1, "Higher education - bachelor's degree": 2,
    "Higher education - degree": 3, "Higher education - master's": 4,
    "Higher education - doctorate": 5, "Frequency of higher education": 6,
    "12th year of schooling - not completed": 9,
    "11th year of schooling - not completed": 10,
    "Other - 11th year of schooling": 12, "10th year of schooling": 14,
    "10th year of schooling - not completed": 15,
    "Basic education 3rd cycle (9th/10th/11th year)": 19,
    "Basic education 2nd cycle (6th/7th/8th year)": 38,
    "Technological specialization course": 39,
    "Higher education - degree (1st cycle)": 40,
    "Professional higher technical course": 42,
    "Higher education - master (2nd cycle)": 43,
}

NACIONALITY = {
    "Portuguese": 1, "German": 2, "Spanish": 6, "Italian": 11, "Dutch": 13,
    "English": 14, "Lithuanian": 17, "Angolan": 21, "Cape Verdean": 22,
    "Guinean": 24, "Mozambican": 25, "Santomean": 26, "Turkish": 32,
    "Brazilian": 41, "Romanian": 62, "Moldova (Republic of)": 100,
    "Mexican": 101, "Ukrainian": 103, "Russian": 105, "Cuban": 108, "Colombian": 109,
}

YES_NO = {"Ya": 1, "Tidak": 0}


def selectbox_code(label, options_dict, default=None, help_text=None):
    keys = list(options_dict.keys())
    idx = keys.index(default) if default in keys else 0
    choice = st.selectbox(label, keys, index=idx, help=help_text)
    return options_dict[choice]


st.title("🎓 Prediksi Risiko Dropout Mahasiswa")
st.markdown("""
Prototype ini membantu **Jaya Jaya Institut** mengidentifikasi mahasiswa yang berisiko
melakukan dropout, berdasarkan data akademik, finansial, dan demografis mahasiswa,
agar bimbingan khusus dapat diberikan sedini mungkin.
""")

st.divider()

tab1, tab2 = st.tabs(["📝 Input Manual", "📁 Upload File CSV (Batch)"])

with tab1:
    st.subheader("Data Pendaftaran & Demografis")
    col1, col2, col3 = st.columns(3)
    with col1:
        marital_status = selectbox_code("Status Pernikahan", MARITAL_STATUS, "Single")
        gender_label = st.selectbox("Jenis Kelamin", ["Perempuan", "Laki-laki"])
        gender = 1 if gender_label == "Laki-laki" else 0
        age = st.number_input("Usia saat Mendaftar", min_value=16, max_value=70, value=20)
    with col2:
        application_mode = selectbox_code("Jalur Pendaftaran", APPLICATION_MODE, "1st phase - general contingent")
        application_order = st.number_input("Urutan Pilihan (0=pilihan pertama)", min_value=0, max_value=9, value=0)
        course = selectbox_code("Program Studi", COURSE, "Informatics Engineering")
    with col3:
        daytime_label = st.selectbox("Waktu Kuliah", ["Pagi/Siang (Daytime)", "Malam (Evening)"])
        daytime_evening_attendance = 1 if daytime_label.startswith("Pagi") else 0
        nacionality = selectbox_code("Kewarganegaraan", NACIONALITY, "Portuguese")
        international = YES_NO[st.selectbox("Mahasiswa Internasional?", list(YES_NO.keys()), index=1)]

    st.subheader("Latar Belakang Pendidikan & Keluarga")
    col1, col2, col3 = st.columns(3)
    with col1:
        previous_qualification = selectbox_code("Kualifikasi Sebelumnya", QUALIFICATION, "Secondary education")
        previous_qualification_grade = st.number_input("Nilai Kualifikasi Sebelumnya (0-200)", 0.0, 200.0, 130.0)
        admission_grade = st.number_input("Nilai Ujian Masuk (0-200)", 0.0, 200.0, 130.0)
    with col2:
        mothers_qualification = st.number_input("Kode Kualifikasi Ibu (1-44)", 1, 44, 1,
                                                  help="Kode kualifikasi pendidikan ibu sesuai kamus data UCI")
        fathers_qualification = st.number_input("Kode Kualifikasi Ayah (1-44)", 1, 44, 1,
                                                  help="Kode kualifikasi pendidikan ayah sesuai kamus data UCI")
    with col3:
        mothers_occupation = st.number_input("Kode Pekerjaan Ibu", 0, 200, 5)
        fathers_occupation = st.number_input("Kode Pekerjaan Ayah", 0, 200, 5)

    st.subheader("Status Khusus & Finansial")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        displaced = YES_NO[st.selectbox("Displaced (pindah domisili)?", list(YES_NO.keys()), index=1)]
    with col2:
        educational_special_needs = YES_NO[st.selectbox("Kebutuhan Pendidikan Khusus?", list(YES_NO.keys()), index=1)]
    with col3:
        debtor = YES_NO[st.selectbox("Status Debtor (menunggak)?", list(YES_NO.keys()), index=1)]
    with col4:
        tuition_fees_up_to_date = YES_NO[st.selectbox("Uang Kuliah Lunas Tepat Waktu?", list(YES_NO.keys()), index=0)]
    scholarship_holder = YES_NO[st.selectbox("Penerima Beasiswa?", list(YES_NO.keys()), index=1)]

    st.subheader("Performa Akademik Semester 1")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        cu1_credited = st.number_input("Credited (S1)", 0, 30, 0)
    with col2:
        cu1_enrolled = st.number_input("Enrolled (S1)", 0, 30, 6)
    with col3:
        cu1_evaluations = st.number_input("Evaluations (S1)", 0, 30, 6)
    with col4:
        cu1_approved = st.number_input("Approved (S1)", 0, 30, 5)
    with col5:
        cu1_grade = st.number_input("Grade Rata-rata (S1)", 0.0, 20.0, 12.0)
    with col6:
        cu1_without_eval = st.number_input("Without Evaluations (S1)", 0, 30, 0)

    st.subheader("Performa Akademik Semester 2")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        cu2_credited = st.number_input("Credited (S2)", 0, 30, 0)
    with col2:
        cu2_enrolled = st.number_input("Enrolled (S2)", 0, 30, 6)
    with col3:
        cu2_evaluations = st.number_input("Evaluations (S2)", 0, 30, 6)
    with col4:
        cu2_approved = st.number_input("Approved (S2)", 0, 30, 5)
    with col5:
        cu2_grade = st.number_input("Grade Rata-rata (S2)", 0.0, 20.0, 12.0)
    with col6:
        cu2_without_eval = st.number_input("Without Evaluations (S2)", 0, 30, 0)

    st.subheader("Indikator Makroekonomi")
    col1, col2, col3 = st.columns(3)
    with col1:
        unemployment_rate = st.number_input("Unemployment Rate (%)", 0.0, 30.0, 10.0)
    with col2:
        inflation_rate = st.number_input("Inflation Rate (%)", -5.0, 10.0, 1.0)
    with col3:
        gdp = st.number_input("GDP", -10.0, 10.0, 0.0)

    st.divider()

    if st.button("🔍 Prediksi Risiko Dropout", type="primary", use_container_width=True):
        input_data = pd.DataFrame([{
            "Marital_status": marital_status,
            "Application_mode": application_mode,
            "Application_order": application_order,
            "Course": course,
            "Daytime_evening_attendance": daytime_evening_attendance,
            "Previous_qualification": previous_qualification,
            "Previous_qualification_grade": previous_qualification_grade,
            "Nacionality": nacionality,
            "Mothers_qualification": mothers_qualification,
            "Fathers_qualification": fathers_qualification,
            "Mothers_occupation": mothers_occupation,
            "Fathers_occupation": fathers_occupation,
            "Admission_grade": admission_grade,
            "Displaced": displaced,
            "Educational_special_needs": educational_special_needs,
            "Debtor": debtor,
            "Tuition_fees_up_to_date": tuition_fees_up_to_date,
            "Gender": gender,
            "Scholarship_holder": scholarship_holder,
            "Age_at_enrollment": age,
            "International": international,
            "Curricular_units_1st_sem_credited": cu1_credited,
            "Curricular_units_1st_sem_enrolled": cu1_enrolled,
            "Curricular_units_1st_sem_evaluations": cu1_evaluations,
            "Curricular_units_1st_sem_approved": cu1_approved,
            "Curricular_units_1st_sem_grade": cu1_grade,
            "Curricular_units_1st_sem_without_evaluations": cu1_without_eval,
            "Curricular_units_2nd_sem_credited": cu2_credited,
            "Curricular_units_2nd_sem_enrolled": cu2_enrolled,
            "Curricular_units_2nd_sem_evaluations": cu2_evaluations,
            "Curricular_units_2nd_sem_approved": cu2_approved,
            "Curricular_units_2nd_sem_grade": cu2_grade,
            "Curricular_units_2nd_sem_without_evaluations": cu2_without_eval,
            "Unemployment_rate": unemployment_rate,
            "Inflation_rate": inflation_rate,
            "GDP": gdp,
        }])

        input_data = input_data.reindex(columns=feature_columns, fill_value=0)
        input_scaled = pd.DataFrame(scaler.transform(input_data), columns=input_data.columns)

        risk_score = model.predict_proba(input_scaled)[0, 1]
        prediction = int(risk_score >= threshold)

        st.divider()
        res_col1, res_col2 = st.columns([1, 2])
        with res_col1:
            st.metric("Skor Risiko Dropout", f"{risk_score * 100:.1f}%")
        with res_col2:
            if prediction == 1:
                st.error("⚠️ **Berisiko Dropout** — mahasiswa ini disarankan mendapat bimbingan akademik/finansial segera.")
            else:
                st.success("✅ **Risiko Rendah** — mahasiswa ini tampak berada pada jalur yang baik.")

        if risk_score < 0.3:
            category = "Low"
        elif risk_score < 0.6:
            category = "Medium"
        else:
            category = "High"
        st.info(f"Kategori risiko: **{category}**")

with tab2:
    st.subheader("Prediksi Batch dari File CSV")
    st.markdown("Upload file CSV dengan kolom yang sama seperti `data.csv` (36 fitur, tanpa kolom `Status`/`Dropout`).")
    uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

    if uploaded_file is not None:
        raw = pd.read_csv(uploaded_file, sep=None, engine="python")
        st.write("Preview data:", raw.head())

        if st.button("🔍 Prediksi untuk Seluruh Data", type="primary"):
            X = raw.reindex(columns=feature_columns, fill_value=0)
            X_scaled = pd.DataFrame(scaler.transform(X), columns=X.columns)

            risk_scores = model.predict_proba(X_scaled)[:, 1]
            result = raw.copy()
            result["DropoutRiskScore"] = risk_scores
            result["DropoutRiskCategory"] = pd.cut(
                risk_scores, bins=[-0.01, 0.3, 0.6, 1.0], labels=["Low", "Medium", "High"]
            )
            result["PredictedDropout"] = (risk_scores >= threshold).astype(int)

            st.write("Hasil Prediksi:", result)
            st.download_button(
                "⬇️ Download Hasil Prediksi (CSV)",
                result.to_csv(index=False).encode("utf-8"),
                "hasil_prediksi_dropout.csv",
                "text/csv",
            )

st.divider()
st.caption("Prototype Machine Learning — Prediksi Dropout Mahasiswa — Jaya Jaya Institut")
