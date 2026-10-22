from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from fugu_logic import filter_programs, load_json, score_programs, validate_records

st.set_page_config(
    page_title="FuGu — your personal college partner",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent

# ---------- Visual system inspired by the supplied Canva screens ----------
st.markdown(
    """
    <style>
    :root {
      --fugu-bg: #F1F6FB;
      --fugu-card: #FFFFFF;
      --fugu-blue: #075DDD;
      --fugu-blue-dark: #17365A;
      --fugu-muted: #5F7288;
      --fugu-line: #D6E2EE;
      --fugu-green: #00B894;
    }
    [data-testid="stAppViewContainer"] { background: var(--fugu-bg); }
    [data-testid="stHeader"] { background: rgba(241,246,251,.96); }
    [data-testid="stMainBlockContainer"] { max-width: 1200px; padding-top: 1.2rem; padding-bottom: 3rem; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { animation: fuguFadeIn .34s ease-out both; }
    @keyframes fuguFadeIn { from {opacity:0; transform:translateY(7px)} to {opacity:1; transform:translateY(0)} }
    .fugu-brand { color: var(--fugu-blue-dark); font-size: 1.42rem; font-weight: 800; letter-spacing: -.04em; line-height: 1.2; }
    .fugu-tagline { color: var(--fugu-muted); font-size: .83rem; margin-top: .15rem; }
    .eyebrow { color: var(--fugu-blue); font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; margin: .2rem 0 .45rem 0; }
    .hero-title { font-size: clamp(2rem, 4vw, 3.4rem); line-height: 1.13; letter-spacing: -.045em; color: var(--fugu-blue-dark); font-weight: 800; max-width: 760px; margin: .4rem 0 .8rem 0; }
    .hero-copy { font-size: 1.03rem; line-height: 1.65; color: var(--fugu-muted); max-width: 760px; }
    .section-title { font-size: 1.45rem; line-height: 1.3; letter-spacing: -.025em; color: var(--fugu-blue-dark); font-weight: 760; margin: .2rem 0 .45rem 0; }
    .section-copy { color: var(--fugu-muted); margin-bottom: .9rem; }
    .fugu-card { background: var(--fugu-card); border: 1px solid var(--fugu-line); border-radius: 13px; padding: 1.12rem 1.16rem; box-shadow: 0 2px 8px rgba(24, 58, 91, .025); height: 100%; transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease; }
    .fugu-card:hover { transform: translateY(-3px); border-color: #A8C5E5; box-shadow: 0 8px 22px rgba(30, 73, 116, .07); }
    .fugu-card h3 { color: var(--fugu-blue-dark); font-size: 1.04rem; margin: .25rem 0 .45rem 0; font-weight: 750; }
    .fugu-card p { color: var(--fugu-muted); font-size: .88rem; line-height: 1.55; margin: .25rem 0; }
    .fugu-card .kicker { color: var(--fugu-blue); font-size: .72rem; letter-spacing: .06em; font-weight: 800; text-transform: uppercase; }
    .fugu-meta { color: var(--fugu-muted); font-size: .8rem; }
    .fugu-pill { display: inline-block; padding: .24rem .62rem; margin: .12rem .18rem .12rem 0; background: #F1F7FE; border: 1px solid #D9E8F8; border-radius: 999px; color: #36577B; font-size: .76rem; }
    .fugu-note { background: #F8FBFF; border-left: 3px solid var(--fugu-blue); border-radius: 8px; padding: .85rem 1rem; color: #46627F; font-size: .88rem; }
    .fugu-footer { border-top: 1px solid var(--fugu-line); margin-top: 2rem; padding-top: 1rem; color: var(--fugu-muted); font-size: .78rem; }
    div.stButton > button, div.stLinkButton > a { border-radius: 9px; font-weight: 700; transition: transform .15s ease, box-shadow .15s ease, background-color .15s ease; }
    div.stButton > button:hover, div.stLinkButton > a:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(7,93,221,.14); }
    div[data-testid="stForm"] { background: #fff; border: 1px solid var(--fugu-line); border-radius: 14px; padding: 1rem; }
    div[data-testid="stProgress"] > div > div { background: var(--fugu-blue); }
    [data-testid="stMetric"] { background:#fff; border:1px solid var(--fugu-line); padding:.85rem; border-radius:12px; }
    a { color: var(--fugu-blue); }
    @media (prefers-reduced-motion: reduce) { .block-container, .fugu-card, div.stButton > button { animation: none !important; transition: none !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Data ----------
@st.cache_data(show_spinner=False)
def get_data():
    programs = load_json("programs.json")
    universities = load_json("universities.json")
    scholarships = load_json("scholarships.json")
    references = load_json("references.json")
    return programs, universities, scholarships, references

programs, universities, scholarships, references = get_data()

INTERESTS = [
    "Teknologi & Komputer",
    "Bisnis & Ekonomi",
    "Kesehatan & Biologi",
    "Desain & Kreativitas",
    "Sosial & Humaniora",
    "Sains & Matematika",
    "Pendidikan",
    "Komunikasi",
]
SKILLS = ["Analitis", "Pemecahan masalah", "Kreativitas", "Komunikasi", "Kepemimpinan", "Empati", "Eksperimen", "Riset", "Praktik"]
CATEGORIES = sorted({p["category"] for p in programs})
PROVINCES = sorted({p["province"] for p in programs})

for key, default in {
    "page": "Home",
    "survey_step": 1,
    "survey_interests": [],
    "survey_skills": [],
    "survey_strengths_text": "",
    "survey_experience_text": "",
    "survey_region": "Semua wilayah",
    "survey_universities": [],
    "survey_scholarship_names": [],
    "selected_program_id": programs[0]["program_id"],
    "selected_university": universities[0]["university"],
    "selected_scholarship_id": scholarships[0]["scholarship_id"],
    "saved_scholarships": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Keep survey answers separate from widget keys. This preserves answers when
# a step is hidden, because Streamlit cleans up keys for widgets not rendered.
SURVEY_WIDGET_BINDINGS = {
    "survey_interests_widget": "survey_interests",
    "survey_skills_widget": "survey_skills",
    "survey_strengths_text_widget": "survey_strengths_text",
    "survey_experience_text_widget": "survey_experience_text",
    "survey_region_widget": "survey_region",
    "survey_universities_widget": "survey_universities",
    "survey_scholarship_names_widget": "survey_scholarship_names",
}
for widget_key, stored_key in SURVEY_WIDGET_BINDINGS.items():
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state[stored_key]


def sync_survey_value(widget_key: str, stored_key: str):
    st.session_state[stored_key] = st.session_state.get(widget_key)


def sync_survey_interests():
    sync_survey_value("survey_interests_widget", "survey_interests")


def sync_survey_skills():
    sync_survey_value("survey_skills_widget", "survey_skills")


def sync_survey_strengths():
    sync_survey_value("survey_strengths_text_widget", "survey_strengths_text")


def sync_survey_experience():
    sync_survey_value("survey_experience_text_widget", "survey_experience_text")


def sync_survey_region():
    sync_survey_value("survey_region_widget", "survey_region")


def sync_survey_universities():
    sync_survey_value("survey_universities_widget", "survey_universities")


def sync_survey_scholarships():
    sync_survey_value("survey_scholarship_names_widget", "survey_scholarship_names")


def goto(page: str):
    st.session_state.page = page


def safe(value) -> str:
    return html.escape(str(value or ""))


def card(title: str, description: str, kicker: str = "", meta: str = ""):
    st.markdown(
        f"""<div class="fugu-card">
        <div class="kicker">{safe(kicker)}</div>
        <h3>{safe(title)}</h3>
        <p>{safe(description)}</p>
        <div class="fugu-meta">{safe(meta)}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def program_card(program: dict, score: float | None = None, key_prefix: str = "program"):
    score_html = f'<span class="fugu-pill">Kecocokan preferensi: {score:.1f}/100</span>' if score is not None else ""
    tags = "".join(f'<span class="fugu-pill">{safe(t)}</span>' for t in program.get("interests", [])[:3])
    st.markdown(
        f"""<div class="fugu-card">
          <div class="kicker">{safe(program.get('category'))} · {safe(program.get('degree'))}</div>
          <h3>{safe(program.get('program_name'))}</h3>
          <p><strong>{safe(program.get('university'))}</strong></p>
          <p>{safe(program.get('summary'))}</p>
          <p class="fugu-meta">⌖ {safe(program.get('city'))}, {safe(program.get('province'))}</p>
          {tags}{score_html}
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Lihat Detail →", key=f"{key_prefix}_{program['program_id']}", use_container_width=True):
        st.session_state.selected_program_id = program["program_id"]
        goto("Detail Program")
        st.rerun()


def university_card(university: dict, key_prefix: str = "university"):
    offerings = [p for p in programs if p["university"] == university["university"]]
    st.markdown(
        f"""<div class="fugu-card">
        <div class="kicker">{safe(university.get('type'))} · {safe(university.get('province'))}</div>
        <h3>{safe(university.get('university'))}</h3>
        <p>Lokasi: {safe(university.get('city'))}, {safe(university.get('province'))}</p>
        <p>{len(offerings)} program studi tersedia dalam katalog prototipe FuGu.</p>
        <p class="fugu-meta">{safe(university.get('note'))}</p>
        </div>""",
        unsafe_allow_html=True,
    )
    a, b = st.columns(2)
    with a:
        if st.button("Lihat Profil →", key=f"{key_prefix}_{safe(university['university'])}", use_container_width=True):
            st.session_state.selected_university = university["university"]
            goto("Detail Universitas")
            st.rerun()
    with b:
        st.link_button("Situs Resmi ↗", university["official_url"], use_container_width=True)


def scholarship_card(scholarship: dict):
    saved = scholarship["scholarship_id"] in st.session_state.saved_scholarships
    st.markdown(
        f"""<div class="fugu-card">
        <div class="kicker">{safe(scholarship.get('provider'))}</div>
        <h3>{safe(scholarship.get('name'))}</h3>
        <p>{safe(scholarship.get('summary'))}</p>
        <p><strong>Sasaran umum:</strong> {safe(scholarship.get('audience'))}</p>
        <p class="fugu-meta">{safe(scholarship.get('status_note'))}</p>
        </div>""",
        unsafe_allow_html=True,
    )
    a, b = st.columns(2)
    with a:
        st.link_button("Buka Sumber Resmi ↗", scholarship["official_url"], use_container_width=True)
    with b:
        label = "Tersimpan ✓" if saved else "Simpan untuk dibandingkan"
        if st.button(label, key=f"save_{scholarship['scholarship_id']}", use_container_width=True):
            selected = list(st.session_state.saved_scholarships)
            if saved:
                selected.remove(scholarship["scholarship_id"])
            else:
                selected.append(scholarship["scholarship_id"])
            st.session_state.saved_scholarships = selected
            st.rerun()


def render_header():
    c_brand, c_home, c_explore, c_scholar = st.columns([5, 1, 1.35, 1.15], vertical_alignment="center")
    with c_brand:
        st.markdown('<div class="fugu-brand">FuGu <span style="font-weight:500;font-size:.8rem;color:#5F7288">· Future Guidance · your personal college partner</span></div>', unsafe_allow_html=True)
    nav_items = [(c_home, "Home", "HOME"), (c_explore, "Eksplorasi", "EKSPLORASI"), (c_scholar, "Beasiswa", "BEASISWA")]
    for col, page, label in nav_items:
        with col:
            if st.button(label, key=f"nav_{page}", type="primary" if st.session_state.page == page else "secondary", use_container_width=True):
                goto(page)
                st.rerun()
    st.divider()


def render_footer():
    st.markdown(
        """<div class="fugu-footer">FuGu · Future Guidance · Prototipe untuk eksplorasi pendidikan. Skor merupakan kecocokan preferensi yang dinyatakan pengguna, bukan ukuran bakat atau prediksi kelulusan.</div>""",
        unsafe_allow_html=True,
    )
    if st.button("Metode & Sumber Data", key="footer_methods"):
        goto("Metode & Sumber")
        st.rerun()


def render_home():
    left, right = st.columns([1.5, 1], gap="large", vertical_alignment="center")
    with left:
        st.markdown('<div class="eyebrow">TEMUKAN ARAH MASA DEPANMU</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-title">Temukan jalanmu menuju kampus impian.</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-copy">Kenali minatmu, bandingkan pilihan kuliah, dan temukan peluang beasiswa dalam satu tempat.</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Mulai Eksplorasi  →", type="primary", key="home_start"):
            st.session_state.survey_step = 1
            goto("Kenali Dirimu")
            st.rerun()
    with right:
        st.markdown(
            """<div class="fugu-card" style="padding:1.45rem">
            <div class="kicker">CARA KERJA FUGU</div>
            <h3>Mulai dari dirimu.</h3>
            <p>1. Pilih bidang yang menarik perhatianmu.</p>
            <p>2. Tentukan preferensi dan wilayah pilihan.</p>
            <p>3. Bandingkan program berdasarkan alasan yang terlihat.</p>
            <p class="fugu-meta">Tanpa akun, dan jawaban survei tidak disimpan ke file.</p>
            </div>""",
            unsafe_allow_html=True,
        )
    st.write("")
    st.markdown('<div class="eyebrow">JELAJAHI FUGU</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    cards = [
        ("⌘", "Eksplorasi Jurusan", "Temukan dan bandingkan program studi berdasarkan minat dan preferensimu.", "Eksplorasi"),
        ("↗", "Cari Beasiswa", "Jelajahi peluang beasiswa dan buka sumber resmi untuk memeriksa syaratnya.", "Beasiswa"),
        ("♡", "Kenali Dirimu", "Pilih minat dan preferensi melalui survei singkat untuk melihat daftar eksplorasi.", "Kenali Dirimu"),
    ]
    for col, (symbol, title, desc, target) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="fugu-card"><div style="font-size:1.5rem;color:#075DDD;margin-bottom:.5rem">{symbol}</div><h3>{safe(title)}</h3><p>{safe(desc)}</p></div>', unsafe_allow_html=True)
            if st.button("Buka halaman →", key=f"home_card_{target}", use_container_width=True):
                if target == "Kenali Dirimu":
                    st.session_state.survey_step = 1
                goto(target)
                st.rerun()
    st.write("")
    if st.button("Temukan Universitas Pilihanmu →", key="home_universities", use_container_width=True):
        goto("Universitas")
        st.rerun()
    st.write("")
    st.markdown('<div class="section-title">Masa depanmu dimulai dari pilihan hari ini.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Jelajahi pilihan kuliah dan persiapkan langkahmu mulai sekarang.</div>', unsafe_allow_html=True)
    st.info("Dataset saat ini adalah katalog awal yang dikurasi dari halaman resmi. Ini belum mencakup seluruh kampus dan seluruh program studi di Indonesia.")


def render_survey():
    step = int(st.session_state.survey_step)
    step = max(1, min(6, step))
    st.markdown('<div class="eyebrow">KENALI DIRIMU</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Temukan pilihan yang ingin kamu jelajahi.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Survei enam langkah ini memetakan minat dan preferensi yang kamu nyatakan. Ini bukan tes bakat atau tes psikologi.</div>', unsafe_allow_html=True)
    st.progress(step / 6, text=f"Langkah {step} dari 6")

    if step == 1:
        st.markdown('<div class="section-title">Apa yang paling menarik buatmu?</div>', unsafe_allow_html=True)
        st.caption("Pilih satu atau beberapa bidang. Kamu bisa mengubah pilihan ini kapan saja.")
        with st.container(border=True):
            st.multiselect("Bidang minat", options=INTERESTS, key="survey_interests_widget", on_change=sync_survey_interests, placeholder="Pilih bidang yang kamu suka...")
            st.markdown("<div class='fugu-meta'>Contoh: teknologi, kesehatan, bisnis, desain, pendidikan, atau humaniora.</div>", unsafe_allow_html=True)
        _, next_col = st.columns([1, 1])
        with next_col:
            if st.button("Lanjut →", type="primary", key="survey_next_1", use_container_width=True):
                if not st.session_state.survey_interests:
                    st.warning("Pilih minimal satu bidang minat agar hasil dapat dibandingkan.")
                else:
                    st.session_state.survey_step = 2
                    st.rerun()

    elif step == 2:
        st.markdown('<div class="section-title">Apa kekuatan atau pengalaman yang ingin kamu bawa?</div>', unsafe_allow_html=True)
        st.caption("Pilih cara kerja yang kamu sukai. Jawaban berupa teks hanya untuk refleksi dan tidak digunakan dalam skor.")
        with st.container(border=True):
            st.multiselect("Kegiatan atau preferensi yang kamu sukai", options=SKILLS, key="survey_skills_widget", on_change=sync_survey_skills, placeholder="Pilih beberapa (opsional)")
            left, right = st.columns([1.6, 1])
            with left:
                st.text_area("Apa yang kamu suka lakukan? (opsional)", key="survey_strengths_text_widget", on_change=sync_survey_strengths, placeholder="Contoh: menghitung, menggambar, meneliti, menulis, mengatur kegiatan...", height=140)
            with right:
                st.text_area("Pengalaman yang pernah kamu coba? (opsional)", key="survey_experience_text_widget", on_change=sync_survey_experience, placeholder="Contoh: proyek sekolah, organisasi, eksperimen, kegiatan kreatif...", height=140)
        a, b = st.columns(2)
        with a:
            if st.button("← Kembali", key="survey_back_2", use_container_width=True):
                st.session_state.survey_step = 1
                st.rerun()
        with b:
            if st.button("Lanjut →", type="primary", key="survey_next_2", use_container_width=True):
                st.session_state.survey_step = 3
                st.rerun()

    elif step == 3:
        st.markdown('<div class="section-title">Rekomendasi program studi awal</div>', unsafe_allow_html=True)
        st.caption("Lihat contoh program yang memiliki tag minat serupa. Ini adalah pratinjau; hasil akhir masih mempertimbangkan preferensi wilayah.")
        f1, f2 = st.columns([2, 1])
        with f1:
            q = st.text_input("Cari jurusan atau kampus", placeholder="Cari di daftar contoh...", key="survey_program_query")
        with f2:
            cat = st.selectbox("Bidang", ["Semua bidang"] + CATEGORIES, key="survey_program_category")
        categories = [] if cat == "Semua bidang" else [cat]
        previews = filter_programs(programs, q, categories)
        ranked_previews = score_programs(previews, st.session_state.survey_interests, st.session_state.survey_skills)[:4]
        if not ranked_previews:
            st.info("Belum ada hasil yang cocok dengan pencarian/filter saat ini. Ubah kata kunci atau kategori.")
        for start_idx in range(0, len(ranked_previews), 2):
            cols = st.columns(2, gap="medium")
            for col, p in zip(cols, ranked_previews[start_idx:start_idx + 2]):
                with col:
                    st.markdown(f'<div class="fugu-card"><div class="kicker">{safe(p["category"])}</div><h3>{safe(p["program_name"])}</h3><p><strong>{safe(p["university"])}</strong></p><p>{safe(p["summary"])}</p><p class="fugu-meta">Skor preferensi awal: {p["score"]:.1f}/100</p></div>', unsafe_allow_html=True)
                    st.link_button("Sumber program resmi ↗", p["program_url"], use_container_width=True)
        a, b = st.columns(2)
        with a:
            if st.button("← Kembali", key="survey_back_3", use_container_width=True):
                st.session_state.survey_step = 2
                st.rerun()
        with b:
            if st.button("Lanjut pilih wilayah →", type="primary", key="survey_next_3", use_container_width=True):
                st.session_state.survey_step = 4
                st.rerun()

    elif step == 4:
        st.markdown('<div class="section-title">Temukan universitas pilihanmu</div>', unsafe_allow_html=True)
        st.caption("Pilih wilayah dan—bila sudah ada—kampus yang ingin kamu prioritaskan. Pilihan kampus menjadi filter hasil akhir, bukan tambahan skor kualitas.")
        with st.container(border=True):
            province_options = ["Semua wilayah"] + sorted({u["province"] for u in universities})
            st.selectbox("Wilayah pilihan", options=province_options, key="survey_region_widget", on_change=sync_survey_region)
            uni_options = [u["university"] for u in universities if st.session_state.survey_region == "Semua wilayah" or u["province"] == st.session_state.survey_region]
            current_uni = [u for u in st.session_state.survey_universities if u in uni_options]
            st.session_state.survey_universities = current_uni
            st.session_state.survey_universities_widget = current_uni
            st.multiselect("Kampus yang ingin diprioritaskan (opsional)", options=uni_options, key="survey_universities_widget", on_change=sync_survey_universities, placeholder="Tidak memilih berarti semua kampus di katalog tetap dipertimbangkan")
        filtered_unis = [u for u in universities if st.session_state.survey_region == "Semua wilayah" or u["province"] == st.session_state.survey_region]
        for start_idx in range(0, min(len(filtered_unis), 4), 2):
            cols = st.columns(2, gap="medium")
            for col, uni in zip(cols, filtered_unis[start_idx:start_idx + 2]):
                with col:
                    st.markdown(f'<div class="fugu-card"><div class="kicker">{safe(uni["type"])} · {safe(uni["province"])}</div><h3>{safe(uni["university"])}</h3><p>{safe(uni["city"])}</p></div>', unsafe_allow_html=True)
                    st.link_button("Situs resmi kampus ↗", uni["official_url"], use_container_width=True)
        a, b = st.columns(2)
        with a:
            if st.button("← Kembali", key="survey_back_4", use_container_width=True):
                st.session_state.survey_step = 3
                st.rerun()
        with b:
            if st.button("Lanjut ke beasiswa →", type="primary", key="survey_next_4", use_container_width=True):
                st.session_state.survey_step = 5
                st.rerun()

    elif step == 5:
        st.markdown('<div class="section-title">Adakah beasiswa yang ingin kamu cek?</div>', unsafe_allow_html=True)
        st.caption("Langkah ini opsional. Jadwal dan syarat beasiswa berubah; cek laman resmi setiap penyelenggara.")
        with st.container(border=True):
            scholarship_options = {s["name"]: s for s in scholarships}
            st.multiselect("Simpan untuk dilihat lagi", options=list(scholarship_options.keys()), key="survey_scholarship_names_widget", on_change=sync_survey_scholarships, placeholder="Pilih satu atau beberapa beasiswa (opsional)")
        for start_idx in range(0, len(scholarships), 2):
            cols = st.columns(2, gap="medium")
            for col, s in zip(cols, scholarships[start_idx:start_idx + 2]):
                with col:
                    st.markdown(f'<div class="fugu-card"><div class="kicker">{safe(s["provider"])}</div><h3>{safe(s["name"])}</h3><p>{safe(s["summary"])}</p><p class="fugu-meta">Periksa syarat dan periode pada situs resmi.</p></div>', unsafe_allow_html=True)
                    st.link_button("Buka sumber resmi ↗", s["official_url"], use_container_width=True)
        a, b, c = st.columns(3)
        with a:
            if st.button("← Kembali", key="survey_back_5", use_container_width=True):
                st.session_state.survey_step = 4
                st.rerun()
        with b:
            if st.button("Lewati langkah ini →", key="survey_skip_5", use_container_width=True):
                st.session_state.survey_step = 6
                st.rerun()
        with c:
            if st.button("Lanjut →", type="primary", key="survey_next_5", use_container_width=True):
                st.session_state.survey_step = 6
                st.rerun()

    else:
        st.markdown('<div class="section-title">Ringkasan pilihanmu</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.write("**Bidang minat:** " + (", ".join(st.session_state.survey_interests) or "Belum dipilih"))
            st.write("**Preferensi/keterampilan:** " + (", ".join(st.session_state.survey_skills) or "Tidak dipilih"))
            st.write("**Wilayah:** " + st.session_state.survey_region)
            st.write("**Kampus prioritas:** " + (", ".join(st.session_state.survey_universities) or "Tidak dibatasi"))
            st.write("**Beasiswa yang ingin dicek:** " + (", ".join(st.session_state.survey_scholarship_names) or "Belum dipilih"))
        st.markdown('<div class="fugu-note">Hasil rekomendasi membandingkan tag minat dan preferensi dengan deskripsi program di dataset awal. Skor tidak mengukur bakat, tidak menunjukkan peluang diterima, dan tidak memprediksi kelulusan.</div>', unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            if st.button("← Kembali", key="survey_back_6", use_container_width=True):
                st.session_state.survey_step = 5
                st.rerun()
        with b:
            if st.button("Tampilkan hasil rekomendasi →", type="primary", key="survey_finish", use_container_width=True):
                if not st.session_state.survey_interests:
                    st.session_state.survey_step = 1
                    st.warning("Pilih minimal satu bidang minat dahulu.")
                else:
                    goto("Rekomendasi")
                    st.rerun()

def render_explore():
    st.markdown('<div class="eyebrow">JELAJAHI PILIHANMU</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Temukan jurusan yang ingin kamu kenali.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Cari nama program, kampus, kota, atau bidang. Buka laman resmi untuk memeriksa detail terkini.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2.2, 1, 1])
    with c1:
        query = st.text_input("Cari jurusan atau kampus", placeholder="Misalnya: informatika, psikologi, UGM...", key="explore_query")
    with c2:
        category = st.selectbox("Bidang", ["Semua bidang"] + CATEGORIES, key="explore_category")
    with c3:
        province = st.selectbox("Wilayah", ["Semua wilayah"] + PROVINCES, key="explore_province")
    universities_options = ["Semua kampus"] + sorted({p["university"] for p in programs})
    university = st.selectbox("Kampus", universities_options, key="explore_university")
    categories = [] if category == "Semua bidang" else [category]
    filtered = filter_programs(programs, query, categories, province, university)
    st.caption(f"{len(filtered)} program ditemukan · {len(programs)} program dalam katalog awal")
    if not filtered:
        st.warning("Belum ada program yang cocok dengan filter ini. Coba hapus sebagian filter atau gunakan kata kunci lain.")
        return
    for start in range(0, len(filtered), 2):
        row = st.columns(2, gap="medium")
        for col, program in zip(row, filtered[start:start + 2]):
            with col:
                program_card(program, key_prefix="explore")
        st.write("")


def render_detail_program():
    lookup = {p["program_id"]: p for p in programs}
    program = lookup.get(st.session_state.selected_program_id, programs[0])
    st.markdown('<div class="eyebrow">DETAIL PROGRAM STUDI</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{safe(program["program_name"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-copy">{safe(program["university"])} · {safe(program["degree"])} · {safe(program["city"])}, {safe(program["province"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="fugu-card"><h3>Tentang program</h3><p>{safe(program["summary"])}</p><div>{"".join(f"<span class=fugu-pill>{safe(tag)}</span>" for tag in program["interests"])}</div></div>', unsafe_allow_html=True)
    st.write("")
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        with st.container(border=True):
            st.markdown("**Apa yang mungkin dipelajari?**")
            for subject in program["subjects"]:
                st.markdown(f"- {subject}")
    with col2:
        with st.container(border=True):
            st.markdown("**Arah eksplorasi karier**")
            for career in program["careers"]:
                st.markdown(f"- {career}")
            st.caption("Daftar ini bersifat orientasi umum. Syarat profesi tertentu dapat membutuhkan pendidikan/izin lanjutan.")
    st.write("")
    st.markdown("**Sumber data**")
    st.write(program["source_note"])
    st.caption(f"Sumber diperiksa: {program['source_checked_on']} · Label minat disusun FuGu untuk prototipe, bukan label resmi kampus.")
    a, b, c = st.columns(3)
    with a:
        st.link_button("Laman Resmi Program ↗", program["program_url"], use_container_width=True)
    with b:
        st.link_button("Situs Resmi Kampus ↗", program["university_url"], use_container_width=True)
    with c:
        if st.button("Cari Universitas →", type="primary", key="detail_go_university", use_container_width=True):
            st.session_state.selected_university = program["university"]
            goto("Detail Universitas")
            st.rerun()
    if st.button("← Kembali ke Eksplorasi", key="detail_back"):
        goto("Eksplorasi")
        st.rerun()


def render_universities():
    st.markdown('<div class="eyebrow">TEMUKAN UNIVERSITAS PILIHANMU</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Bandingkan kampus berdasarkan lokasi dan program yang tersedia.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Jumlah program di setiap kartu menunjukkan berapa banyak yang ada di katalog FuGu saat ini, bukan seluruh program yang ditawarkan kampus.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        query = st.text_input("Cari universitas", placeholder="Nama kampus atau kota...", key="university_query")
    with c2:
        province = st.selectbox("Provinsi", ["Semua wilayah"] + sorted({u["province"] for u in universities}), key="university_province")
    with c3:
        typ = st.selectbox("Jenis", ["Semua", "PTN", "PTS"], key="university_type")
    q = query.casefold().strip()
    filtered = [u for u in universities if (not q or q in (u["university"] + " " + u["city"] + " " + u["province"]).casefold()) and (province == "Semua wilayah" or u["province"] == province) and (typ == "Semua" or u["type"] == typ)]
    st.caption(f"{len(filtered)} perguruan tinggi di direktori contoh")
    if not filtered:
        st.warning("Tidak ada kampus yang cocok. Coba kata kunci atau filter lain.")
        return
    for start in range(0, len(filtered), 2):
        cols = st.columns(2, gap="medium")
        for col, uni in zip(cols, filtered[start:start + 2]):
            with col:
                university_card(uni, "univ")
        st.write("")


def render_university_detail():
    uni = next((u for u in universities if u["university"] == st.session_state.selected_university), universities[0])
    st.markdown('<div class="eyebrow">PROFIL UNIVERSITAS</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{safe(uni["university"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-copy">{safe(uni["city"])}, {safe(uni["province"])} · {safe(uni["type"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="fugu-card"><h3>Tentang direktori FuGu</h3><p>{safe(uni["note"])}</p><p>Katalog ini hanya menampilkan program yang sudah dimasukkan ke dataset awal. Untuk daftar resmi yang lengkap, kunjungi laman program atau situs kampus.</p></div>', unsafe_allow_html=True)
    st.write("")
    st.link_button("Kunjungi Situs Resmi ↗", uni["official_url"], use_container_width=True)
    st.markdown("**Program yang terdapat dalam katalog FuGu**")
    offerings = [p for p in programs if p["university"] == uni["university"]]
    if not offerings:
        st.info("Belum ada program dari kampus ini yang dimasukkan ke dataset FuGu.")
    for start in range(0, len(offerings), 2):
        cols = st.columns(2)
        for col, program in zip(cols, offerings[start:start + 2]):
            with col:
                program_card(program, key_prefix="univdetail")
    if st.button("← Kembali ke daftar universitas", key="university_detail_back"):
        goto("Universitas")
        st.rerun()


def render_scholarships():
    st.markdown('<div class="eyebrow">PELUANG PENDIDIKAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Temukan beasiswa yang ingin kamu periksa.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">FuGu tidak menyimpan jadwal pendaftaran sebagai jaminan berlaku. Gunakan tautan resmi untuk mengecek periode, syarat, dan perguruan tinggi mitra terbaru.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        query = st.text_input("Cari beasiswa atau penyedia", placeholder="Nama program atau penyedia...", key="scholarship_query")
    with c2:
        provider = st.selectbox("Penyedia", ["Semua"] + sorted({s["provider"] for s in scholarships}), key="scholarship_provider")
    q = query.casefold().strip()
    filtered = [s for s in scholarships if (not q or q in (s["name"] + " " + s["provider"] + " " + s["summary"] + " " + s["audience"]).casefold()) and (provider == "Semua" or provider == s["provider"])]
    st.caption(f"{len(filtered)} program beasiswa pada daftar awal")
    for start in range(0, len(filtered), 2):
        cols = st.columns(2, gap="medium")
        for col, scholarship in zip(cols, filtered[start:start + 2]):
            with col:
                scholarship_card(scholarship)
        st.write("")
    saved = [s for s in scholarships if s["scholarship_id"] in st.session_state.saved_scholarships]
    if saved:
        st.markdown("### Beasiswa tersimpan untuk dibandingkan")
        for s in saved:
            st.markdown(f"- **{safe(s['name'])}** — [sumber resmi]({s['official_url']})")


def render_recommendations():
    st.markdown('<div class="eyebrow">HASIL EKSPLORASI</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Pilihan yang selaras dengan minatmu.</div>', unsafe_allow_html=True)
    interests = st.session_state.survey_interests
    skills = st.session_state.survey_skills
    province = st.session_state.survey_region
    if not interests:
        st.info("Isi survei Kenali Dirimu terlebih dahulu untuk menghasilkan rekomendasi.")
        if st.button("Mulai survei →", type="primary", key="result_start_survey"):
            st.session_state.survey_step = 1
            goto("Kenali Dirimu")
            st.rerun()
        return
    ranked = score_programs(programs, interests, skills, province)
    preferred_universities = st.session_state.survey_universities
    if preferred_universities:
        ranked = [p for p in ranked if p["university"] in preferred_universities]
    if not ranked:
        if preferred_universities:
            st.warning("Tidak ada program dalam katalog awal untuk kombinasi kampus pilihan ini. Kembali ke survei dan hapus sebagian pilihan kampus atau pilih 'Semua wilayah'.")
            if st.button("Ubah pilihan kampus", key="results_change_universities"):
                st.session_state.survey_step = 4
                goto("Kenali Dirimu")
                st.rerun()
            return
        st.warning("Tidak cukup data untuk menghitung rekomendasi.")
        return
    st.markdown(f'<div class="fugu-note">Hasil dibuat dari {len(interests)} bidang minat' + (f' dan {len(skills)} preferensi/keterampilan' if skills else '') + (f' dengan wilayah pilihan {safe(province)}' if province != "Semua wilayah" else '') + (f'. Kandidat dibatasi pada kampus pilihanmu.' if preferred_universities else '') + '. Skor adalah perbandingan preferensi yang dinyatakan, bukan ukuran bakat, peluang diterima, atau prediksi kelulusan.</div>', unsafe_allow_html=True)
    top = ranked[:5]
    chart_df = pd.DataFrame([{"Program": f"{p['program_name']} · {p['university'].split('(')[0].strip()}", "Skor kecocokan": p["score"]} for p in top])
    fig = px.bar(chart_df, x="Skor kecocokan", y="Program", orientation="h", range_x=[0, 100], text="Skor kecocokan", title="Perbandingan skor 5 hasil teratas")
    fig.update_traces(marker_color="#075DDD", texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
    fig.update_layout(height=max(320, 64 * len(top)), plot_bgcolor="#FFFFFF", paper_bgcolor="#F1F6FB", margin=dict(l=8, r=34, t=50, b=10), xaxis_title="Skor kecocokan (0–100)", yaxis_title="", showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key="recommendation_chart")
    with st.expander("Bagaimana skor ini dihitung?"):
        st.markdown("- **Minat (70%)**: proporsi minat yang kamu pilih dan juga diberi tag pada program.")
        st.markdown("- **Preferensi/keterampilan (20%)**: proporsi pilihan keterampilan yang cocok, jika kamu mengisinya.")
        st.markdown("- **Wilayah (10%)**: cocok dengan provinsi pilihan atau tidak, jika kamu memilih satu provinsi.")
        st.markdown("Jika kriteria opsional tidak dipilih, bobot aktif dinormalisasi. Bobot ini adalah pilihan desain prototipe dan perlu dievaluasi sebelum digunakan untuk penelitian formal.")
    for start in range(0, len(ranked[:8]), 2):
        cols = st.columns(2, gap="medium")
        for col, program in zip(cols, ranked[start:start + 2]):
            with col:
                program_card(program, score=program["score"], key_prefix="recommend")
                with st.expander("Lihat alasan skor"):
                    st.write(f"Skor minat: {program['interest_score']:.1f}/100")
                    if program["skill_score"] is not None:
                        st.write(f"Skor preferensi/keterampilan: {program['skill_score']:.1f}/100")
                    if program["region_score"] is not None:
                        st.write(f"Skor wilayah: {program['region_score']:.1f}/100")
                    for reason in program["reasons"]:
                        st.markdown(f"- {reason}")
                    st.caption("Tag minat dan keterampilan merupakan metadata kurasi FuGu untuk prototipe, bukan kategori yang ditetapkan universitas.")
    a, b = st.columns(2)
    with a:
        if st.button("Ubah jawaban survei", key="result_edit_survey", use_container_width=True):
            st.session_state.survey_step = 1
            goto("Kenali Dirimu")
            st.rerun()
    with b:
        if st.button("Bandingkan semua jurusan", key="result_explore", type="primary", use_container_width=True):
            goto("Eksplorasi")
            st.rerun()


def render_methods():
    st.markdown('<div class="eyebrow">TRANSPARANSI</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Metode, sumber data, dan batasan FuGu</div>', unsafe_allow_html=True)
    st.markdown("""<div class="fugu-note">Dataset di paket ini adalah sampel awal yang dikurasi dari beberapa halaman resmi. Dataset ini bukan daftar seluruh perguruan tinggi atau seluruh program studi Indonesia. Periksa sumber asli sebelum mengambil keputusan pendidikan atau mengutip data dalam KTI.</div>""", unsafe_allow_html=True)
    st.markdown("### Logika rekomendasi")
    st.write("FuGu menghitung kecocokan tag minat, preferensi/keterampilan, dan wilayah. Tag minat serta keterampilan ditambahkan oleh penyusun dataset berdasarkan pembacaan deskripsi program; tag bukan klasifikasi resmi dari kampus. Bobot 70/20/10 hanya bobot prototipe dan tidak boleh disebut tervalidasi secara ilmiah sebelum uji dengan evaluator dan profil uji dilakukan.")
    st.markdown("### Pemeriksaan kualitas data internal")
    warnings = validate_records(programs)
    if warnings:
        st.warning("Ditemukan peringatan struktur data:")
        for warning in warnings:
            st.write("- " + warning)
    else:
        st.success(f"Struktur {len(programs)} rekaman program lolos pemeriksaan dasar ID, kolom wajib, dan format URL HTTPS. Ini bukan verifikasi independen atas seluruh fakta pada situs sumber.")
    st.markdown("### Dataset kampus dan program studi")
    rows = [{"Program studi": p["program_name"], "Perguruan tinggi": p["university"], "Wilayah": p["province"], "Jenjang": p["degree"], "Tanggal pemeriksaan": p["source_checked_on"], "Sumber": p["program_url"]} for p in programs]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, column_config={"Sumber": st.column_config.LinkColumn("Sumber resmi", display_text="Buka sumber ↗")})
    st.markdown("### Sumber beasiswa")
    for s in scholarships:
        st.markdown(f"- **{safe(s['name'])}** — [situs resmi]({s['official_url']}). {safe(s['status_note'])}")
    st.markdown("### Bacaan ilmiah awal")
    for ref in references:
        st.markdown(f"**{safe(ref['authors'])} ({safe(ref['year'])}). {safe(ref['title'])}.** {safe(ref['publication'])}. DOI: [{safe(ref['doi'])}]({ref['url']}).")
        st.caption(ref["use"])
    st.markdown("### Rekomendasi evaluasi untuk KTI")
    st.markdown("1. Buat rubrik relevansi program (misalnya skala 0–3) dan libatkan evaluator yang memahami bidang terkait.\n2. Bandingkan hasil FuGu dengan baseline sederhana, seperti jumlah tag minat yang sama.\n3. Laporkan Precision@5 dan/atau nDCG@5 hanya jika label relevansi telah dikumpulkan dengan prosedur yang jelas.\n4. Uji kemudahan penggunaan pada peserta dengan persetujuan yang sesuai; bila peserta di bawah umur, ikuti prosedur izin sekolah/orang tua dan pembimbing.\n5. Simpan versi dataset, kode, kriteria eksklusi, dan hasil uji agar eksperimen dapat diulang.")
    st.markdown("### Sumber portal resmi")
    official_sources = [
        ("PDDikti", "https://pddikti.kemdiktisaintek.go.id/"),
        ("BAN-PT", "https://www.banpt.or.id/"),
        ("SNPMB", "https://www.snpmb.id/jadwal-penting"),
        ("KIP Kuliah", "https://kip-kuliah.kemdiktisaintek.go.id/"),
    ]
    for name, url in official_sources:
        st.markdown(f"- [{name}]({url})")


# ---------- App router ----------
render_header()
page = st.session_state.page
if page == "Home":
    render_home()
elif page == "Kenali Dirimu":
    render_survey()
elif page == "Eksplorasi":
    render_explore()
elif page == "Detail Program":
    render_detail_program()
elif page == "Universitas":
    render_universities()
elif page == "Detail Universitas":
    render_university_detail()
elif page == "Beasiswa":
    render_scholarships()
elif page == "Rekomendasi":
    render_recommendations()
elif page == "Metode & Sumber":
    render_methods()
else:
    goto("Home")
    st.rerun()

render_footer()
