import streamlit as st
from openai import OpenAI

# ==========================================
# ⚙️ MINIMALIST PAGE SETUP
# ==========================================
st.set_page_config(page_title="CareerOS", page_icon="⚫", layout="wide")

# Custom CSS to hide default Streamlit clutter (Hamburger menu, Footer, etc.)
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
# 🧠 SYSTEM PROMPT (UNCHANGED)
# ==========================================
SYSTEM_PROMPT = """
You are helping design and power a web application for job applications.
The app has:
- A dropdown where the user selects either "Resume Editor" or "Cover Letter Editor".
- A text area to paste their base resume.
- A text area to paste the job description.
- If "Cover Letter Editor" is selected, an optional field for a short personal note.

Behavior:
1. When the mode is Resume Editor:
   - Extract the most important skills, tools, and responsibilities from the job description.
   - Map those to relevant parts of the user’s base resume.
   - Rewrite the resume to target this job.
   - Output: Keyword focus list, then Tailored resume.

2. When the mode is Cover Letter Editor:
   - Produce a one-page cover letter hooking into the company name and connecting resume highlights.
   - Output: Keyword focus list, then Tailored cover letter.

Output format:
- Always start with: "Mode: resume" or "Mode: cover_letter"
- Then: "Keyword focus:" followed by a bullet list.
- Then: "Result:" followed by the final tailored text.
"""

# ==========================================
# 🎨 MINIMALIST SIDEBAR (UPDATED)
# ==========================================
with st.sidebar:
    st.markdown("### `SYSTEM_CONFIG`")
    
    # Try to grab key from secrets first
    try:
        default_key = st.secrets["OPENAI_API_KEY"]
        st.success("API Key Loaded from Secrets 🔒")
    except:
        default_key = ""

    # If secret is found, use it. If not, show text box.
    api_key = st.text_input("API Key", value=default_key, type="password")
    
    st.markdown("---")
    
    st.markdown("### `MODE_SELECT`")
    mode = st.radio("Target Output", ["Resume Editor", "Cover Letter Editor"], label_visibility="collapsed")
    
    st.markdown("---")
    st.caption("v1.0.0 | CareerOS")

# ==========================================
# 📝 MAIN INTERFACE
# ==========================================
st.markdown("## `INPUT_DATA`")

c1, c2 = st.columns(2)

with c1:
    base_resume = st.text_area("Base Resume", height=300, placeholder="// Paste your raw resume text here...")

with c2:
    job_description = st.text_area("Job Description", height=300, placeholder="// Paste the job post here...")

extra_context = ""
if mode == "Cover Letter Editor":
    extra_context = st.text_area("User Notes", placeholder="// Optional context (e.g. 'Emphasize my Python skills')")

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
        with st.spinner("PROCESSING..."):
            try:
                client = OpenAI(api_key=api_key)
                internal_mode = "resume" if mode == "Resume Editor" else "cover_letter"
                
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
                
                # Parsing Output
                if "Result:" in result:
                    parts = result.split("Result:")
                    meta = parts[0].replace("Mode: resume", "").replace("Mode: cover_letter", "").strip()
                    content = parts[1].strip()
                    
                    st.success("STATUS: COMPLETE")
                    
                    # Display Keywords
                    with st.expander("VIEW KEYWORD ANALYSIS", expanded=False):
                        st.markdown(meta)
                    
                    # Display Final Result
                    st.markdown("## `OUTPUT_RESULT`")
                    st.text_area("Final Draft", value=content, height=600)
                    
                    st.download_button(
                        "DOWNLOAD .TXT", 
                        data=content, 
                        file_name=f"tailored_{internal_mode}.txt",
                        use_container_width=True
                    )
                else:
                    st.write(result)

            except Exception as e:
                st.error(f"SYSTEM_ERROR: {e}")