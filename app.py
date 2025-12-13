import streamlit as st
from openai import OpenAI
from fpdf import FPDF

# ==========================================
# ⚙️ MINIMALIST PAGE SETUP
# ==========================================
st.set_page_config(page_title="CareerOS", page_icon="⚫", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stTextArea textarea {font-family: 'Courier New', monospace;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ==========================================
# 🧠 PDF GENERATION FUNCTIONS
# ==========================================
def create_pdf(text_content, style):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    if style == "Modern":
        pdf.set_fill_color(30, 60, 114) 
        pdf.rect(0, 0, 210, 30, 'F')
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, "DOCUMENT EXPORT", ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(20)

    elif style == "Creative":
        pdf.set_fill_color(50, 50, 50)
        pdf.rect(0, 0, 60, 297, 'F')
        pdf.set_font("Courier", "B", 16)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(10, 20)
        pdf.cell(50, 10, "PROFILE", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(70, 20)

    # Add Generated Text
    if style == "Creative":
        pdf.set_font("Courier", "", 12)
        pdf.set_xy(70, 30)
        safe_text = text_content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(130, 6, safe_text)
    else:
        pdf.set_font("Arial", "", 12)
        safe_text = text_content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, safe_text)
        
    return pdf

# ==========================================
# 🧠 SYSTEM PROMPT
# ==========================================
SYSTEM_PROMPT = """
You are helping design and power a web application for job applications.
Output format:
- Always start with: "Mode: resume" or "Mode: cover_letter"
- Then: "Keyword focus:" followed by a bullet list.
- Then: "Result:" followed by the final tailored text.
"""

# ==========================================
# 🎨 SIDEBAR (WITH DROPDOWN)
# ==========================================
with st.sidebar:
    st.markdown("### `SYSTEM_CONFIG`")
    try:
        default_key = st.secrets["OPENAI_API_KEY"]
        st.success("API Key Loaded 🔒")
    except:
        default_key = ""

    api_key = st.text_input("API Key", value=default_key, type="password")
    st.markdown("---")
    
    # --- RESTORED DROPDOWN ---
    st.markdown("### `MODE_SELECT`")
    mode = st.selectbox("Target Output", ["Resume Editor", "Cover Letter Editor"])
    
    st.caption("v2.1.0 | CareerOS")

# ==========================================
# 📝 MAIN INTERFACE
# ==========================================
st.markdown(f"## `INPUT_DATA` ({mode})")

c1, c2 = st.columns(2)
with c1:
    base_resume = st.text_area("Base Resume", height=250, placeholder="// Paste raw resume...")
with c2:
    job_description = st.text_area("Job Description", height=250, placeholder="// Paste job post...")

# --- RESTORED COVER LETTER LOGIC ---
extra_context = ""
if mode == "Cover Letter Editor":
    st.info("✍️ **Cover Letter Notes:**")
    extra_context = st.text_area("User Notes", height=100, placeholder="// E.g. 'Emphasize my leadership skills and Python experience'")

# ==========================================
# 🎨 TEMPLATE SELECTION
# ==========================================
st.markdown("---")
st.markdown("### `SELECT_TEMPLATE`")

if 'selected_template' not in st.session_state:
    st.session_state.selected_template = "Modern"

t1, t2 = st.columns(2)

with t1:
    try: st.image("assets/modern.png", caption="Modern")
    except: st.markdown("🟦 **Modern**") 
    if st.button("Select Modern", key="btn_mod", use_container_width=True):
        st.session_state.selected_template = "Modern"

with t2:
    try: st.image("assets/creative.png", caption="Creative")
    except: st.markdown("🟪 **Creative**")
    if st.button("Select Creative", key="btn_cre", use_container_width=True):
        st.session_state.selected_template = "Creative"

st.info(f"Current Style: **{st.session_state.selected_template}**")

# ==========================================
# 🚀 EXECUTION
# ==========================================
st.markdown("---")

if st.button("RUN GENERATOR ⚡", type="primary", use_container_width=True):
    if not api_key:
        st.error("MISSING_API_KEY")
    elif not base_resume or not job_description:
        st.warning("MISSING_INPUT_DATA")
    else:
        with st.spinner("AI GENERATING CONTENT..."):
            try:
                client = OpenAI(api_key=api_key)
                internal_mode = "resume" if mode == "Resume Editor" else "cover_letter"
                
                # --- UPDATED MESSAGE TO INCLUDE USER NOTES ---
                user_message = f"Mode: {internal_mode}\n<resume>{base_resume}</resume>\n<job>{job_description}</job>\n<note>{extra_context}</note>"

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7
                )
                
                result = response.choices[0].message.content
                
                if "Result:" in result:
                    parts = result.split("Result:")
                    meta = parts[0].strip()
                    final_content = parts[1].strip()
                    
                    st.success("STATUS: COMPLETE")
                    
                    # GENERATE PDF
                    pdf = create_pdf(final_content, st.session_state.selected_template)
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    
                    st.markdown("### `PREVIEW`")
                    st.text_area("Generated Text", value=final_content, height=400)
                    
                    st.download_button(
                        label=f"⬇️ DOWNLOAD PDF ({st.session_state.selected_template})",
                        data=pdf_bytes,
                        file_name=f"tailored_{internal_mode}_{st.session_state.selected_template}.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
                else:
                    st.write(result)

            except Exception as e:
                st.error(f"SYSTEM_ERROR: {e}")