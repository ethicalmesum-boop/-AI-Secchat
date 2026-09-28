# ============================================
# AI-SecChat - Main Application
# TEE (Trusted Execution Environment) enabled
# Works on Local (Kali) + Streamlit Cloud
# ============================================

import streamlit as st
import time
import os
from pathlib import Path
from google import genai
from tee_layer import TEELayer

# Crypto Tools import - Hash, Encrypt, Decrypt
from crypto_tools import (
    generate_hashes, hash_file, crack_hash, identify_hash,
    caesar_encrypt, caesar_decrypt, base64_encrypt, base64_decrypt,
    aes_encrypt, aes_decrypt, reverse_text, rot13,
    hex_encode, hex_decode
)


# ============================================
# LOAD API KEY (Local + Cloud dono ke liye)
# ============================================
API_KEY = None

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY not found in secrets or .env file!")
    st.stop()


# ============================================
# MODEL + CLIENT
# ============================================
MODEL_NAME = "gemini-3.8-flash"
client = genai.Client(api_key=API_KEY)


# ============================================
# TEE LAYER
# ============================================
if "tee" not in st.session_state:
    st.session_state.tee = TEELayer()
tee = st.session_state.tee


# ============================================
# CSS LOADER
# ============================================
def load_css(file_name):
    css_file = Path(__file__).parent / file_name
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="AI-SecChat",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css("styles.css")


# ============================================
# SESSION STATE
# ============================================
if "history" not in st.session_state:
    st.session_state.history = []

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()


# ============================================
# AI HELPER (TEE ke through)
# ============================================
def ask_ai(prompt, force_local=False, max_retries=3):
    """TEE layer ke through AI se poochta hai"""
    tee_result = tee.process(prompt, force_local=force_local)
    route = tee_result["route"]
    safe_prompt = tee_result["safe_prompt"]
    
    if route == "local":
        response = tee.query_local_ai(safe_prompt)
        return response, tee_result
    
    # Cloud (Gemini) - retry logic
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=safe_prompt
            )
            return resp.text, tee_result
        except Exception as e:
            if ("503" in str(e) or "UNAVAILABLE" in str(e)):
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
            raise e


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <div style='font-size: 2.5rem; filter: drop-shadow(0 0 20px #4FF7FF);'>🛡️</div>
        <h1 style='font-size: 1.4rem !important; margin: 10px 0;'>AI-SecChat</h1>
        <div style='color: #5a7391; font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase;'>
            v1.2 • Cyber Security
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚡ System Health")
    
    local_status = "🟢 Online" if tee.local_ai_available else "🟡 Cloud Only"
    local_class = "ok" if tee.local_ai_available else "warn"
    
    st.markdown(f"""
    <div class='system-block'>
        <div><span class='ok'>●</span> TEE Layer: <span class='ok'>Active</span></div>
        <div><span class='{local_class}'>●</span> Local AI: <span class='{local_class}'>{local_status}</span></div>
        <div><span class='ok'>●</span> Gemini API: <span class='ok'>Ready</span></div>
        <div><span class='ok'>●</span> Audit Log: <span class='ok'>{len(tee.audit_log)} entries</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Modules")
    st.markdown("""
    <div class='system-block'>
        <div>💬 AI Chatbot</div>
        <div>🎣 Phishing Detector</div>
        <div>🔑 Password Advisor</div>
        <div>🔗 URL Checker</div>
        <div>🔐 TEE Audit Log</div>
        <div>🔒 Crypto Toolkit</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Stack")
    st.markdown("""
    <div class='system-block'>
        <div>› Python 3.10+</div>
        <div>› Streamlit</div>
        <div>› Google Gemini 3.8</div>
        <div>› Ollama (Local AI)</div>
        <div>› TEE Layer</div>
        <div>› Cryptography</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #4a5d7a; font-size: 0.7rem; 
                letter-spacing: 1px; padding: 10px;'>
        <div style='color: #4FF7FF; font-weight: 600; margin-bottom: 4px;'>
            TEAM SILENT EXPLOIT
        </div>
        <div>Made for Hackathon 2026</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# HERO SECTION
# ============================================
st.title("🛡️ AI-SecChat")

st.markdown("""
<div class='hero'>
    <b>AI-POWERED CYBER SECURITY ASSISTANT</b><br>
    <span style='color: #5a7391; letter-spacing: 3px; font-size: 0.75rem;'>
        DETECT • ANALYZE • PROTECT • TRUST
    </span><br>
    <small>🔐 TEE-ENABLED • ZERO-TRUST PROCESSING</small>
</div>
""", unsafe_allow_html=True)

uptime = int(time.time() - st.session_state.start_time)
uptime_str = f"{uptime//60:02d}:{uptime%60:02d}"

st.markdown(f"""
<div style='display: flex; justify-content: space-between; align-items: center;
            padding: 8px 16px; background: rgba(10, 25, 50, 0.5); 
            border: 1px solid rgba(46, 155, 255, 0.15);
            border-radius: 8px; margin-bottom: 20px;
            font-family: JetBrains Mono, monospace; font-size: 0.7rem;'>
    <span style='color: #4FF7FF;'>◉ SYSTEM ONLINE</span>
    <span style='color: #5a7391;'>TEE: ACTIVE</span>
    <span style='color: #5a7391;'>UPTIME: {uptime_str}</span>
    <span style='color: #5a7391;'>LOGS: {len(tee.audit_log)}</span>
</div>
""", unsafe_allow_html=True)


# ============================================
# TABS - 6 Tabs
# ============================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 AI Chat",
    "🎣 Phishing Detector",
    "🔑 Password Advisor",
    "🔗 URL Checker",
    "🔐 TEE Audit Log",
    "🔒 Crypto Toolkit"
])


# ============================================
# TAB 1: AI CHAT (Auto Route)
# ============================================
with tab1:
    st.header("💬 Security AI Chatbot")
    st.write("Ask any question:")
    
    question = st.text_input("Question:", key="chat_q")
    
    if st.button("Generate", key="chat_btn"):
        if question:
            with st.spinner("AI Fetching Data..."):
                try:
                    # Chat: Auto route (safe data cloud, sensitive local)
                    answer, tee_info = ask_ai(
                        f"You are a cyber security expert. "
                        f"Answer in simple Roman English "
                        f"(English words written in Roman script, no Hindi/Urdu). "
                        f"Keep it short and clear: {question}",
                        force_local=False
                    )
                    
                    if tee_info["route"] == "local":
                        st.info("🔒 Processed Locally (TEE)")
                    else:
                        st.info("☁️ Processed via Cloud AI (Anonymized)")
                    
                    st.success(answer)
                    
                    st.session_state.history.append({
                        "type": "Chat",
                        "input": question[:50],
                        "time": time.strftime("%H:%M:%S")
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter any question")


# ============================================
# TAB 2: PHISHING DETECTOR (Auto Route)
# ============================================
with tab2:
    st.header("🎣 Phishing Email Detector")
    st.write("Paste your Email/Message:")
    
    email = st.text_area("Email content:", height=200, key="phish_email")
    
    if st.button("Check Email", key="phish_btn"):
        if email:
            with st.spinner("AI Fetching Data..."):
                try:
                    prompt = f"""Analyze this email/message for phishing:

{email}

Reply in this format (in Roman English):
VERDICT: [PHISHING or SAFE or SUSPICIOUS]
CONFIDENCE: [High/Medium/Low]
REASON: [2-3 lines]
RED FLAGS: [bullet points]
ADVICE: [what user should do]
"""
                    # Auto route (PII detect hogi automatically)
                    result, tee_info = ask_ai(prompt, force_local=False)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if tee_info["route"] == "local":
                            st.info("🔒 Local Processing")
                        else:
                            st.info("☁️ Cloud Processing")
                    with col2:
                        if tee_info["pii_found"]:
                            st.warning(f"⚠️ PII: {', '.join(tee_info['pii_found'])}")
                        else:
                            st.success("✅ No PII")
                    
                    st.markdown(result)
                    
                    st.session_state.history.append({
                        "type": "Phishing",
                        "input": email[:50],
                        "time": time.strftime("%H:%M:%S")
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter Email/Message")


# ============================================
# TAB 3: PASSWORD ADVISOR (PERMANENT LOCAL)
# ============================================
with tab3:
    st.header("🔑 AI Password Advisor")
    st.write("Enter your Password:")
    
    pwd = st.text_input("Password:", type="password", key="pwd_input")
    
    # Info box - permanent local
    st.info("🔒 This feature always runs LOCALLY (TEE) - Password never leaves your device")
    
    if st.button("Check Password", key="pwd_btn"):
        if pwd:
            with st.spinner("AI Fetching Data (Local)..."):
                try:
                    prompt = f"""Analyze this password: {pwd}

Give (in Roman English):
1. STRENGTH: [Weak / Medium / Strong]
2. SCORE: [out of 10]
3. PROBLEMS: (bullet points)
4. BETTER SUGGESTIONS: (3 strong examples)
5. TIPS: (2 lines)
"""
                    # Permanent force_local=True
                    result, tee_info = ask_ai(prompt, force_local=True)
                    
                    if tee_info["route"] == "local":
                        st.success("🔒 Password processed LOCALLY - Not sent to cloud!")
                    else:
                        st.info("☁️ Cloud processing (anonymized)")
                    
                    st.markdown(result)
                    
                    st.session_state.history.append({
                        "type": "Password",
                        "input": "****",
                        "time": time.strftime("%H:%M:%S")
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter your Password")


# ============================================
# TAB 4: URL CHECKER (Auto Route)
# ============================================
with tab4:
    st.header("🔗 URL Safety Checker")
    st.write("Paste your URL:")
    
    url = st.text_input(
        "URL:",
        placeholder="https://example.com",
        key="url_input"
    )
    
    if st.button("Check URL", key="url_btn"):
        if url:
            with st.spinner("AI Fetching Data..."):
                try:
                    prompt = f"""Is this URL safe or malicious? {url}

Check for:
- Suspicious keywords
- Typosquatting (paypa1 vs paypal)
- Suspicious TLD (.tk, .ml, .ga)
- IP address instead of domain

Reply (in Roman English):
VERDICT: [SAFE or SUSPICIOUS or MALICIOUS]
CONFIDENCE: [High/Medium/Low]
REASON: [2-3 lines]
ADVICE: [what user should do]
"""
                    result, tee_info = ask_ai(prompt, force_local=False)
                    
                    if tee_info["route"] == "local":
                        st.info("🔒 Local Processing")
                    else:
                        st.info("☁️ Cloud Processing")
                    
                    st.markdown(result)
                    
                    st.session_state.history.append({
                        "type": "URL",
                        "input": url[:50],
                        "time": time.strftime("%H:%M:%S")
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter your URL")


# ============================================
# TAB 5: TEE AUDIT LOG
# ============================================
with tab5:
    st.header("🔐 TEE Audit Log")
    st.write("This shows where each request was processed")
    
    if tee.audit_log:
        total = len(tee.audit_log)
        local_count = sum(1 for x in tee.audit_log if x["route"] == "local")
        cloud_count = total - local_count
        pii_count = sum(1 for x in tee.audit_log if x["pii_found"][0] != "None")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Requests", total)
        col2.metric("🔒 Local", local_count)
        col3.metric("☁️ Cloud", cloud_count)
        col4.metric("⚠️ PII Detected", pii_count)
        
        st.markdown("---")
        st.markdown("### 📋 Full Audit Log")
        for entry in reversed(tee.audit_log):
            with st.expander(
                f"[{entry['timestamp']}] {entry['route'].upper()} | "
                f"Hash: {entry['hash']}"
            ):
                st.write(f"**Timestamp:** {entry['timestamp']}")
                st.write(f"**Data Hash:** `{entry['hash']}`")
                st.write(f"**Route:** {entry['route']}")
                st.write(f"**PII Detected:** {', '.join(entry['pii_found'])}")
                st.write(f"**Anonymized:** {entry['anonymized']}")
    else:
        st.info("No requests made yet. Try a tab!")


# ============================================
# TAB 6: CRYPTO TOOLKIT
# ============================================
with tab6:
    st.header("🔒 Crypto Toolkit")
    st.write("Hash Generator + Hash Cracker + Encrypt + Decrypt")
    st.caption("⚠️ Educational Purpose Only")
    
    crypto_tab1, crypto_tab2, crypto_tab3, crypto_tab4 = st.tabs([
        "🔢 Hash Generator",
        "🔓 Hash Cracker",
        "🔒 Encrypt",
        "🔑 Decrypt"
    ])
    
    # ========== SUB-TAB 1: HASH GENERATOR ==========
    with crypto_tab1:
        st.subheader("🔢 Hash Generator")
        st.write("Generate hashes from Text or File")
        
        hash_input_type = st.radio(
            "Input type:",
            ["Text", "File"],
            horizontal=True,
            key="hash_input_type"
        )
        
        if hash_input_type == "Text":
            hash_text = st.text_area(
                "Enter text to hash:",
                height=100,
                key="hash_text_input"
            )
            
            if st.button("Generate Hashes", key="gen_hash_btn"):
                if hash_text:
                    hashes = generate_hashes(hash_text)
                    st.success("✅ Hashes generated!")
                    
                    for algo, hash_val in hashes.items():
                        col1, col2 = st.columns([1, 3])
                        col1.write(f"**{algo}**")
                        col2.code(hash_val)
                    
                    st.markdown("**Combined output:**")
                    combined = "\n".join([f"{k}: {v}" for k, v in hashes.items()])
                    st.code(combined)
                else:
                    st.warning("Please enter text first!")
        
        else:
            uploaded = st.file_uploader(
                "Upload a file:",
                key="hash_file_upload"
            )
            
            if uploaded:
                file_bytes = uploaded.read()
                st.info(f"📁 File: {uploaded.name} ({len(file_bytes)} bytes)")
                
                if st.button("Generate File Hashes", key="gen_file_hash_btn"):
                    hashes = hash_file(file_bytes)
                    st.success("✅ File hashes generated!")
                    
                    for algo, hash_val in hashes.items():
                        col1, col2 = st.columns([1, 3])
                        col1.write(f"**{algo}**")
                        col2.code(hash_val)
    
    # ========== SUB-TAB 2: HASH CRACKER ==========
    with crypto_tab2:
        st.subheader("🔓 Hash Cracker (Dictionary Attack)")
        st.caption("Common passwords try karta hai - CrackStation style")
        
        crack_hash_input = st.text_input(
            "Enter hash to crack:",
            placeholder="5d41402abc4b2a76b9719d911017c592",
            key="crack_hash_input"
        )
        
        if crack_hash_input:
            detected = identify_hash(crack_hash_input)
            if detected != "Not a valid hash":
                st.info(f"🔍 Detected: **{detected}**")
            else:
                st.warning("⚠️ Invalid hash format")
        
        crack_algo = st.selectbox(
            "Algorithm:",
            ["auto", "md5", "sha1", "sha256", "sha512"],
            key="crack_algo"
        )
        
        if st.button("🔓 Crack Hash", key="crack_btn"):
            if crack_hash_input:
                with st.spinner("Cracking... (trying common passwords)"):
                    if crack_algo == "auto":
                        detected = identify_hash(crack_hash_input)
                        algo_map = {
                            "MD5": "md5", "SHA1": "sha1",
                            "SHA256": "sha256", "SHA512": "sha512"
                        }
                        crack_algo = algo_map.get(detected, "md5")
                    
                    result = crack_hash(crack_hash_input, crack_algo)
                    
                    if result:
                        st.success(f"🎉 CRACKED! Original text: **{result}**")
                        st.balloons()
                    else:
                        st.error("❌ Not cracked. Password strong hai ya wordlist mein nahi.")
                        st.info("💡 Strong passwords easily crack nahi hote!")
            else:
                st.warning("Please enter a hash!")
        
        st.markdown("---")
        st.markdown("### 🧪 Try These Test Samples")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Test: 123456", key="test1"):
                st.code("e10adc3949ba59abbe56e057f20f883e")
        with col2:
            if st.button("Test: password", key="test2"):
                st.code("5f4dcc3b5aa765d61d8327deb882cf99")
        with col3:
            if st.button("Test: admin", key="test3"):
                st.code("21232f297a57a5a743894a0e4a801fc3")
    
    # ========== SUB-TAB 3: ENCRYPT ==========
    with crypto_tab3:
        st.subheader("🔒 Encrypt Text")
        
        encrypt_method = st.selectbox(
            "Encryption Method:",
            ["AES-256", "Base64", "Caesar Cipher", "ROT13", "Hex", "Reverse"],
            key="enc_method"
        )
        
        encrypt_text = st.text_area(
            "Text to encrypt:",
            height=100,
            key="enc_text"
        )
        
        if encrypt_method == "AES-256":
            encrypt_password = st.text_input(
                "Password:",
                type="password",
                key="enc_pwd"
            )
        elif encrypt_method == "Caesar Cipher":
            caesar_shift = st.slider(
                "Shift:", 1, 25, 3,
                key="caesar_shift"
            )
        
        if st.button("🔒 Encrypt", key="enc_btn"):
            if encrypt_text:
                try:
                    if encrypt_method == "AES-256":
                        if encrypt_password:
                            result = aes_encrypt(encrypt_text, encrypt_password)
                        else:
                            st.warning("Enter password!")
                            result = None
                    elif encrypt_method == "Base64":
                        result = base64_encrypt(encrypt_text)
                    elif encrypt_method == "Caesar Cipher":
                        result = caesar_encrypt(encrypt_text, caesar_shift)
                    elif encrypt_method == "ROT13":
                        result = rot13(encrypt_text)
                    elif encrypt_method == "Hex":
                        result = hex_encode(encrypt_text)
                    elif encrypt_method == "Reverse":
                        result = reverse_text(encrypt_text)
                    
                    if result:
                        st.success("✅ Encrypted!")
                        st.code(result)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Enter text first!")
    
    # ========== SUB-TAB 4: DECRYPT ==========
    with crypto_tab4:
        st.subheader("🔑 Decrypt Text")
        
        decrypt_method = st.selectbox(
            "Decryption Method:",
            ["AES-256", "Base64", "Caesar Cipher", "ROT13", "Hex", "Reverse"],
            key="dec_method"
        )
        
        decrypt_text = st.text_area(
            "Text to decrypt:",
            height=100,
            key="dec_text"
        )
        
        if decrypt_method == "AES-256":
            decrypt_password = st.text_input(
                "Password:",
                type="password",
                key="dec_pwd"
            )
        elif decrypt_method == "Caesar Cipher":
            caesar_shift_dec = st.slider(
                "Shift:", 1, 25, 3,
                key="caesar_shift_dec"
            )
        
        if st.button("🔑 Decrypt", key="dec_btn"):
            if decrypt_text:
                try:
                    if decrypt_method == "AES-256":
                        if decrypt_password:
                            result = aes_decrypt(decrypt_text, decrypt_password)
                        else:
                            st.warning("Enter password!")
                            result = None
                    elif decrypt_method == "Base64":
                        result = base64_decrypt(decrypt_text)
                    elif decrypt_method == "Caesar Cipher":
                        result = caesar_decrypt(decrypt_text, caesar_shift_dec)
                    elif decrypt_method == "ROT13":
                        result = rot13(decrypt_text)
                    elif decrypt_method == "Hex":
                        result = hex_decode(decrypt_text)
                    elif decrypt_method == "Reverse":
                        result = reverse_text(decrypt_text)
                    
                    if result:
                        if result.startswith("❌"):
                            st.error(result)
                        else:
                            st.success("✅ Decrypted!")
                            st.code(result)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Enter text first!")


# ============================================
# SIDEBAR HISTORY
# ============================================
with st.sidebar:
    if st.session_state.history:
        st.markdown("---")
        st.markdown("### 📜 Recent Scans")
        for item in st.session_state.history[-5:]:
            st.caption(f"**{item['type']}** | {item['time']}")


# ============================================
# FOOTER
# ============================================
st.markdown(f"""
<div class='footer'>
    🛡️ AI-SecChat v1.2 • TEE-Enabled • Powered by Google Gemini 3.8<br>
    <span style='color: #4FF7FF; letter-spacing: 2px;'>
        TEAM SILENT EXPLOIT
    </span>
</div>
""", unsafe_allow_html=True)