import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import hashlib
import re
import time
from datetime import datetime
import pyrebase

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="IRIS PAY",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 50%, #0a0a1a 100%);
    }

    h1, h2, h3 {
        font-family: 'Orbitron', monospace !important;
        color: #00d4ff !important;
        letter-spacing: 2px;
    }

    .iris-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #7b2fff, #00d4ff);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s infinite;
        text-align: center;
        letter-spacing: 4px;
        margin-bottom: 0.2rem;
    }

    @keyframes shimmer {
        0% { background-position: 0% }
        100% { background-position: 200% }
    }

    .subtitle {
        text-align: center;
        color: #4a9eff;
        font-size: 0.85rem;
        letter-spacing: 3px;
        margin-bottom: 2rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00d4ff22, #7b2fff22);
        border: 1px solid #00d4ff55;
        color: #00d4ff;
        font-family: 'Orbitron', monospace;
        font-size: 0.75rem;
        letter-spacing: 2px;
        padding: 0.6rem 1.5rem;
        border-radius: 4px;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #00d4ff44, #7b2fff44);
        border-color: #00d4ff;
        box-shadow: 0 0 20px #00d4ff33;
        transform: translateY(-1px);
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: #0d1b2a !important;
        border: 1px solid #00d4ff33 !important;
        color: #a0d8ef !important;
        border-radius: 4px !important;
        font-family: 'Rajdhani', sans-serif !important;
    }

    .stSelectbox > div > div {
        background: #0d1b2a !important;
        border: 1px solid #00d4ff33 !important;
        color: #a0d8ef !important;
    }

    .stRadio > div {
        background: #0d1b2a11;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #00d4ff22;
    }

    .metric-card {
        background: linear-gradient(135deg, #0d1b2a, #0a1628);
        border: 1px solid #00d4ff33;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }

    .metric-value {
        font-family: 'Orbitron', monospace;
        font-size: 1.8rem;
        color: #00d4ff;
        font-weight: 700;
    }

    .metric-label {
        color: #4a9eff;
        font-size: 0.75rem;
        letter-spacing: 2px;
        margin-top: 0.3rem;
    }

    .txn-row {
        background: linear-gradient(90deg, #0d1b2a, #0a1628);
        border: 1px solid #00d4ff22;
        border-left: 3px solid #00d4ff;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        font-family: 'Rajdhani', sans-serif;
        color: #a0d8ef;
        font-size: 0.9rem;
    }

    .success-banner {
        background: linear-gradient(135deg, #003322, #004433);
        border: 1px solid #00ff88;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        color: #00ff88;
        font-family: 'Orbitron', monospace;
        font-size: 1.1rem;
        letter-spacing: 2px;
        margin: 1rem 0;
    }

    .warning-banner {
        background: linear-gradient(135deg, #330000, #440011);
        border: 1px solid #ff4455;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        color: #ff4455;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.9rem;
        letter-spacing: 1px;
    }

    /* ── Notification Bell Banner ── */
    .notif-banner {
        background: linear-gradient(135deg, #0a1f0a, #0d2b1a);
        border: 1px solid #00ff88;
        border-left: 4px solid #00ff88;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.5rem;
        font-family: 'Rajdhani', sans-serif;
        color: #00ff88;
        font-size: 0.95rem;
        letter-spacing: 1px;
        animation: fadeSlide 0.4s ease;
    }

    .notif-banner-debit {
        background: linear-gradient(135deg, #1a0a0a, #2b0d0d);
        border: 1px solid #ff6655;
        border-left: 4px solid #ff6655;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.5rem;
        font-family: 'Rajdhani', sans-serif;
        color: #ff9988;
        font-size: 0.95rem;
        letter-spacing: 1px;
        animation: fadeSlide 0.4s ease;
    }

    .notif-header {
        font-family: 'Orbitron', monospace;
        font-size: 0.85rem;
        color: #00d4ff;
        letter-spacing: 3px;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .notif-badge {
        background: #ff4455;
        color: white;
        border-radius: 50%;
        width: 22px;
        height: 22px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        margin-left: 6px;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 #ff445566; }
        50% { transform: scale(1.15); box-shadow: 0 0 0 6px #ff445500; }
    }

    @keyframes fadeSlide {
        from { opacity: 0; transform: translateY(-8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .divider {
        border: none;
        border-top: 1px solid #00d4ff22;
        margin: 1.5rem 0;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #060d16 0%, #0a1628 100%);
        border-right: 1px solid #00d4ff22;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: #a0d8ef !important;
        font-family: 'Rajdhani', sans-serif;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FIREBASE CONFIG
# ============================================================
firebaseConfig = {
    "apiKey": "AIzaSyAtXFRP71QPvJ74zEBpZvMlLCsEKN5TG_4",
    "authDomain": "irispay-26a81.firebaseapp.com",
    "databaseURL": "https://irispay-26a81-default-rtdb.firebaseio.com",
    "projectId": "irispay-26a81",
    "storageBucket": "irispay-26a81.firebasestorage.app",
    "messagingSenderId": "932322573680",
    "appId": "1:932322573680:web:3b72417f24a1b1be9fa3b5"
}

@st.cache_resource
def init_firebase():
    firebase = pyrebase.initialize_app(firebaseConfig)
    return firebase.database()

db = init_firebase()

# ============================================================
# MEDIAPIPE INIT
# ============================================================
@st.cache_resource
def init_mediapipe():
    mp_face_mesh = mp.solutions.face_mesh
    return mp_face_mesh.FaceMesh(
        refine_landmarks=True,
        max_num_faces=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

face_mesh = init_mediapipe()

LEFT_IRIS  = [468, 469, 470, 471, 472]
RIGHT_IRIS = [473, 474, 475, 476, 477]

LEFT_EYE_TOP    = 159
LEFT_EYE_BOTTOM = 145
LEFT_EYE_LEFT   = 33
LEFT_EYE_RIGHT  = 133

# ============================================================
# SESSION STATE
# ============================================================
for key, val in {
    "user_id": None,
    "user_data": None,
    "merchant_id": None,
    "merchant_data": None,
    "role": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def validate_phone(phone: str) -> bool:
    return bool(re.match(r'^\d{10}$', phone))

def validate_pin(pin: str) -> bool:
    return bool(re.match(r'^\d{4,6}$', pin))

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

# ============================================================
# NOTIFICATION FUNCTIONS  ← NEW
# ============================================================

def push_notification(entity_id: str, entity_type: str,
                      message: str, notif_type: str, txn_time: str):
    """
    Push a notification into Firebase for a user or merchant.

    entity_type : "user" | "merchant"
    notif_type  : "credit" | "debit"
    """
    db.child("notifications").child(entity_type).child(entity_id).push({
        "message":  message,
        "time":     txn_time,
        "type":     notif_type,   # "credit" or "debit"
        "read":     False
    })


def send_payment_notifications(uid: str, user_name: str,
                                mid: str, shop_name: str,
                                amount: float, txn_time: str):
    """
    After a successful payment send notifications to BOTH parties.
    """
    # Debit alert → User
    push_notification(
        entity_id   = uid,
        entity_type = "user",
        message     = f"₹{amount:.2f} debited — paid to {shop_name}",
        notif_type  = "debit",
        txn_time    = txn_time
    )
    # Credit alert → Merchant
    push_notification(
        entity_id   = mid,
        entity_type = "merchant",
        message     = f"₹{amount:.2f} credited — received from {user_name}",
        notif_type  = "credit",
        txn_time    = txn_time
    )


def get_unread_notifications(entity_id: str, entity_type: str) -> list:
    """
    Fetch all unread notifications for a user or merchant.
    Returns list of dicts with keys: key, message, time, type.
    """
    try:
        result = db.child("notifications").child(entity_type)\
                   .child(entity_id).get()
        if not result or not result.each():
            return []
        unread = []
        for item in result.each():
            val = item.val()
            if isinstance(val, dict) and not val.get("read", True):
                unread.append({
                    "key":     item.key(),
                    "message": val.get("message", ""),
                    "time":    val.get("time", ""),
                    "type":    val.get("type", "credit")
                })
        return unread
    except Exception:
        return []


def mark_notifications_read(entity_id: str, entity_type: str, keys: list):
    """Mark a list of notification keys as read."""
    for k in keys:
        try:
            db.child("notifications").child(entity_type)\
              .child(entity_id).child(k).update({"read": True})
        except Exception:
            pass


def show_notification_panel(entity_id: str, entity_type: str):
    """
    Render the notification bell + panel at the top of any dashboard.
    Automatically marks shown notifications as read after display.
    """
    unread = get_unread_notifications(entity_id, entity_type)

    if not unread:
        st.markdown(
            '<div style="color:#2a4a5a; font-family:Rajdhani,sans-serif; '
            'font-size:0.85rem; letter-spacing:1px; margin-bottom:0.8rem;">'
            '🔔 No new notifications</div>',
            unsafe_allow_html=True
        )
        return

    # Bell header with badge
    count = len(unread)
    st.markdown(
        f'<div class="notif-header">'
        f'🔔 NOTIFICATIONS'
        f'<span class="notif-badge">{count}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    keys_to_mark = []
    for n in unread:
        css_class = "notif-banner-debit" if n["type"] == "debit" else "notif-banner"
        icon      = "💸" if n["type"] == "debit" else "💰"
        st.markdown(
            f'<div class="{css_class}">'
            f'{icon} &nbsp;<b>{n["message"]}</b>'
            f'<br><span style="font-size:0.78rem; opacity:0.7;">🕐 {n["time"]}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        keys_to_mark.append(n["key"])

    # Mark all as read silently
    mark_notifications_read(entity_id, entity_type, keys_to_mark)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ============================================================
# IRIS FUNCTIONS
# ============================================================

def extract_iris_vector(frame: np.ndarray) -> np.ndarray | None:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    if not results.multi_face_landmarks:
        return None
    landmarks = results.multi_face_landmarks[0].landmark
    iris_pts = []
    for idx in LEFT_IRIS + RIGHT_IRIS:
        lm = landmarks[idx]
        iris_pts.extend([lm.x, lm.y, lm.z])
    return np.array(iris_pts, dtype=np.float32)


def compute_ear(landmarks, h: int, w: int) -> float:
    top    = landmarks[LEFT_EYE_TOP]
    bottom = landmarks[LEFT_EYE_BOTTOM]
    left   = landmarks[LEFT_EYE_LEFT]
    right  = landmarks[LEFT_EYE_RIGHT]
    vertical   = abs(top.y - bottom.y)
    horizontal = abs(left.x - right.x) + 1e-6
    return vertical / horizontal


def live_iris_capture(require_blink: bool = True):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None, False

    EAR_BLINK_THRESHOLD = 0.18
    BLINK_CONSEC_FRAMES = 2
    COLLECT_FRAMES      = 40
    MAX_WAIT_FRAMES     = 150

    blink_confirmed  = False
    blink_counter    = 0
    collected_vecs   = []

    stframe = st.empty()
    status  = st.empty()
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame   = cv2.flip(frame, 1)
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        h, w    = frame.shape[:2]
        display = frame.copy()

        if results.multi_face_landmarks:
            lms = results.multi_face_landmarks[0].landmark
            ear = compute_ear(lms, h, w)

            if require_blink and not blink_confirmed:
                if ear < EAR_BLINK_THRESHOLD:
                    blink_counter += 1
                else:
                    if blink_counter >= BLINK_CONSEC_FRAMES:
                        blink_confirmed = True
                        status.success("✅ Blink detected! Capturing iris...")
                    blink_counter = 0
                if not blink_confirmed:
                    status.info(f"👁️ Please blink once to confirm liveness... EAR={ear:.3f}")

            if blink_confirmed or not require_blink:
                vec = extract_iris_vector(frame)
                if vec is not None:
                    collected_vecs.append(vec)
                for idx in LEFT_IRIS + RIGHT_IRIS:
                    lm = lms[idx]
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    cv2.circle(display, (px, py), 2, (0, 212, 255), -1)
                if len(collected_vecs) >= COLLECT_FRAMES:
                    break
        else:
            if not blink_confirmed:
                status.warning("⚠️ No face detected. Please face the camera.")

        stframe.image(
            cv2.cvtColor(display, cv2.COLOR_BGR2RGB),
            channels="RGB",
            caption="IRIS SCANNER — Keep eyes open and face the camera",
            use_column_width=True
        )
        frame_count += 1

        if require_blink and not blink_confirmed and frame_count > MAX_WAIT_FRAMES:
            status.error("⏱️ Timeout: No blink detected. Please try again.")
            cap.release()
            stframe.empty()
            return None, False

    cap.release()
    stframe.empty()
    status.empty()

    if len(collected_vecs) < 5:
        return None, blink_confirmed

    averaged = np.mean(collected_vecs, axis=0)
    return averaged, blink_confirmed


# ============================================================
# DATABASE HELPERS
# ============================================================

def phone_exists_in_users(phone: str) -> bool:
    users = db.child("users").get().val() or {}
    return any(d.get("phone") == phone for d in users.values())

def phone_exists_in_merchants(phone: str) -> bool:
    merchants = db.child("merchants").get().val() or {}
    return any(d.get("phone") == phone for d in merchants.values())

def find_user_by_phone(phone: str):
    users = db.child("users").get().val() or {}
    for uid, data in users.items():
        if data.get("phone") == phone:
            return uid, data
    return None, None

def find_merchant_by_credentials(shop: str, phone: str):
    merchants = db.child("merchants").get().val() or {}
    for mid, data in merchants.items():
        if data.get("shop_name") == shop and data.get("phone") == phone:
            return mid, data
    return None, None

def get_iris_vector(user_id: str) -> np.ndarray | None:
    data = db.child("users").child(user_id).child("iris_vector").get().val()
    if data:
        return np.array(data, dtype=np.float32)
    return None

def save_iris_vector(user_id: str, vec: np.ndarray):
    db.child("users").child(user_id).update({"iris_vector": vec.tolist()})

def iris_enrolled(user_id: str) -> bool:
    return get_iris_vector(user_id) is not None

# ============================================================
# TITLE
# ============================================================
st.markdown('<div class="iris-title">👁 IRIS PAY</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">BIOMETRIC PAYMENT PLATFORM</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🔐 NAVIGATION")
    menu = st.radio(
        "",
        ["Login / Register", "Dashboard"],
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.session_state.role == "user":
        st.markdown(f"**Logged in as:** User")
        st.markdown(f"**Phone:** {st.session_state.user_data.get('phone', '')}")
    elif st.session_state.role == "merchant":
        st.markdown(f"**Logged in as:** Merchant")
        st.markdown(f"**Shop:** {st.session_state.merchant_data.get('shop_name', '')}")

    if st.session_state.role is not None:
        if st.button("🚪 LOGOUT"):
            st.session_state.user_id       = None
            st.session_state.user_data     = None
            st.session_state.merchant_id   = None
            st.session_state.merchant_data = None
            st.session_state.role          = None
            st.rerun()

# ============================================================
# LOGIN / REGISTER
# ============================================================
if menu == "Login / Register":

    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])

    # ---- LOGIN ----
    with tab1:
        role_login = st.selectbox("Role", ["User", "Merchant"], key="login_role")

        if role_login == "User":
            phone_l = st.text_input("Phone Number", key="login_phone",
                                     placeholder="10-digit mobile number")
            pin_l   = st.text_input("PIN", type="password", key="login_pin",
                                     placeholder="4–6 digit PIN")

            if st.button("LOGIN AS USER", key="btn_login_user"):
                if not validate_phone(phone_l):
                    st.error("❌ Enter a valid 10-digit phone number.")
                elif not pin_l:
                    st.error("❌ PIN cannot be empty.")
                else:
                    uid, udata = find_user_by_phone(phone_l)
                    if uid is None:
                        st.error("❌ User not found.")
                    elif udata.get("pin") != hash_pin(pin_l):
                        st.error("❌ Incorrect PIN.")
                    else:
                        st.session_state.user_id       = uid
                        st.session_state.user_data     = udata
                        st.session_state.merchant_id   = None
                        st.session_state.merchant_data = None
                        st.session_state.role          = "user"
                        st.success("✅ Logged in successfully!")
                        st.rerun()

        else:
            shop_l  = st.text_input("Shop Name", key="login_shop")
            phone_l = st.text_input("Phone Number", key="login_mphone",
                                     placeholder="10-digit mobile number")

            if st.button("LOGIN AS MERCHANT", key="btn_login_merchant"):
                if not validate_phone(phone_l):
                    st.error("❌ Enter a valid 10-digit phone number.")
                else:
                    mid, mdata = find_merchant_by_credentials(shop_l, phone_l)
                    if mid is None:
                        st.error("❌ Merchant not found. Check shop name and phone.")
                    else:
                        st.session_state.merchant_id   = mid
                        st.session_state.merchant_data = mdata
                        st.session_state.user_id       = None
                        st.session_state.user_data     = None
                        st.session_state.role          = "merchant"
                        st.success("✅ Merchant logged in!")
                        st.rerun()

    # ---- REGISTER ----
    with tab2:
        role_reg = st.selectbox("Role", ["User", "Merchant"], key="reg_role")

        if role_reg == "User":
            name_r  = st.text_input("Full Name", key="reg_name")
            phone_r = st.text_input("Phone Number", key="reg_phone",
                                     placeholder="10-digit mobile number")
            pin_r   = st.text_input("PIN", type="password", key="reg_pin",
                                     placeholder="4–6 digit PIN")
            pin_c   = st.text_input("Confirm PIN", type="password", key="reg_pin_c",
                                     placeholder="Re-enter PIN")

            if st.button("REGISTER USER", key="btn_reg_user"):
                errors = []
                if not name_r.strip():
                    errors.append("Name is required.")
                if not validate_phone(phone_r):
                    errors.append("Enter a valid 10-digit phone number.")
                if not validate_pin(pin_r):
                    errors.append("PIN must be 4–6 digits.")
                if pin_r != pin_c:
                    errors.append("PINs do not match.")
                if phone_exists_in_users(phone_r):
                    errors.append("This phone number is already registered.")

                if errors:
                    for e in errors:
                        st.error(f"❌ {e}")
                else:
                    db.child("users").push({
                        "name":        name_r.strip(),
                        "phone":       phone_r,
                        "pin":         hash_pin(pin_r),
                        "balance":     1000.0,
                        "iris_vector": None
                    })
                    st.success("✅ User registered! You can now log in.")

        else:
            shop_r  = st.text_input("Shop Name", key="reg_shop")
            phone_r = st.text_input("Phone Number", key="reg_mphone",
                                     placeholder="10-digit mobile number")
            lic_r   = st.text_input("Business License Number", key="reg_lic")

            if st.button("REGISTER MERCHANT", key="btn_reg_merchant"):
                errors = []
                if not shop_r.strip():
                    errors.append("Shop name is required.")
                if not validate_phone(phone_r):
                    errors.append("Enter a valid 10-digit phone number.")
                if not lic_r.strip():
                    errors.append("License number is required.")
                if phone_exists_in_merchants(phone_r):
                    errors.append("This phone is already registered as a merchant.")

                if errors:
                    for e in errors:
                        st.error(f"❌ {e}")
                else:
                    db.child("merchants").push({
                        "shop_name": shop_r.strip(),
                        "phone":     phone_r,
                        "license":   lic_r.strip(),
                        "balance":   0.0
                    })
                    st.success("✅ Merchant registered! You can now log in.")

# ============================================================
# DASHBOARD
# ============================================================
elif menu == "Dashboard":

    if st.session_state.role is None:
        st.markdown("""
        <div class="warning-banner">
            ⚠️  You are not logged in.<br>
            Please go to Login / Register.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ============================================================
    # USER DASHBOARD
    # ============================================================
    if st.session_state.role == "user":

        uid   = st.session_state.user_id
        udata = db.child("users").child(uid).get().val()   # fresh
        st.session_state.user_data = udata

        st.markdown(f"### 👤 Welcome, {udata.get('name', 'User')}")

        # ── NOTIFICATION PANEL (always shown at top) ──────────────
        show_notification_panel(uid, "user")

        # Balance + Iris status cards
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">₹{udata.get('balance', 0):.2f}</div>
                <div class="metric-label">WALLET BALANCE</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            enrolled    = iris_enrolled(uid)
            status_text = "ENROLLED ✅" if enrolled else "NOT ENROLLED ❌"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="font-size:1rem;">{status_text}</div>
                <div class="metric-label">IRIS STATUS</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Refresh button to check for new notifications
        if st.button("🔄 REFRESH NOTIFICATIONS", key="user_refresh"):
            st.rerun()

        st.markdown("---")

        # Iris enrollment
        with st.expander("👁️ ENROLL MY IRIS", expanded=not enrolled):
            st.info(
                "Your iris will be captured via webcam. "
                "You will be asked to **blink once** to confirm liveness. "
                "Keep your face well-lit and look directly at the camera."
            )
            if st.button("START IRIS ENROLLMENT", key="user_enroll"):
                with st.spinner("Initializing camera..."):
                    vec, blinked = live_iris_capture(require_blink=True)

                if vec is None:
                    st.error("❌ Iris capture failed. Please try again in good lighting.")
                elif not blinked:
                    st.error("❌ Liveness check failed. Blink was not detected.")
                else:
                    save_iris_vector(uid, vec)
                    st.markdown(
                        '<div class="success-banner">✅ IRIS ENROLLED SUCCESSFULLY</div>',
                        unsafe_allow_html=True
                    )
                    st.rerun()

        # Transaction history
        st.markdown("### 📋 TRANSACTION HISTORY")
        history = db.child("users").child(uid).child("history").get()

        if history and history.each():
            for h in history.each():
                val = h.val()
                st.markdown(f"""
                <div class="txn-row">
                    💸 <b>₹{val.get('amount', 0)}</b> → {val.get('to', 'Unknown')}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    🕐 {val.get('time', '')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No transactions yet.")

    # ============================================================
    # MERCHANT DASHBOARD
    # ============================================================
    elif st.session_state.role == "merchant":

        mid   = st.session_state.merchant_id
        mdata = db.child("merchants").child(mid).get().val()   # fresh
        st.session_state.merchant_data = mdata

        st.markdown(f"### 🏪 {mdata.get('shop_name', 'Merchant')}")

        # ── NOTIFICATION PANEL (always shown at top) ──────────────
        show_notification_panel(mid, "merchant")

        # Balance card
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{mdata.get('balance', 0):.2f}</div>
            <div class="metric-label">TOTAL RECEIVED</div>
        </div>
        """, unsafe_allow_html=True)

        # Refresh button
        if st.button("🔄 REFRESH NOTIFICATIONS", key="merchant_refresh"):
            st.rerun()

        st.markdown("---")

        option = st.radio(
            "SELECT OPERATION",
            ["💳 Process Payment", "👁️ Enroll User Iris", "📋 Transaction History"],
            horizontal=True
        )

        st.markdown("---")

        # ---- ENROLL USER IRIS (by merchant) ----
        if option == "👁️ Enroll User Iris":

            st.markdown("#### 👁️ USER IRIS ENROLLMENT")
            st.info("Enter the user's phone number, then capture their iris.")

            phone_e = st.text_input("User Phone Number", placeholder="10-digit number",
                                     key="enroll_phone")

            if st.button("CAPTURE IRIS", key="btn_enroll"):
                if not validate_phone(phone_e):
                    st.error("❌ Enter a valid 10-digit phone number.")
                else:
                    uid_e, udata_e = find_user_by_phone(phone_e)
                    if uid_e is None:
                        st.error("❌ User not found. Ask user to register first.")
                    else:
                        st.success(f"✅ User found: **{udata_e.get('name')}**")
                        st.info("Ask the user to **blink once** when prompted.")

                        with st.spinner("Opening camera..."):
                            vec, blinked = live_iris_capture(require_blink=True)

                        if vec is None:
                            st.error("❌ Iris capture failed. Try again.")
                        elif not blinked:
                            st.error("❌ Liveness check failed. No blink detected.")
                        else:
                            save_iris_vector(uid_e, vec)
                            st.markdown(
                                '<div class="success-banner">✅ IRIS ENROLLED SUCCESSFULLY</div>',
                                unsafe_allow_html=True
                            )

        # ---- PROCESS PAYMENT ----
        elif option == "💳 Process Payment":

            st.markdown("#### 💳 PAYMENT TERMINAL")

            phone_p  = st.text_input("User Phone Number", key="pay_phone",
                                      placeholder="10-digit number")
            amount_p = st.number_input("Amount (₹)", min_value=1,
                                        max_value=50000, step=1, key="pay_amount")
            pin_p    = st.text_input("User PIN", type="password", key="pay_pin",
                                      placeholder="User's 4–6 digit PIN")

            if st.button("🔍 AUTHENTICATE & PAY", key="btn_pay"):

                # Step 1: Validate inputs
                if not validate_phone(phone_p):
                    st.error("❌ Enter a valid 10-digit phone number.")
                    st.stop()
                if not pin_p:
                    st.error("❌ PIN is required.")
                    st.stop()

                # Step 2: Find user
                uid_p, udata_p = find_user_by_phone(phone_p)
                if uid_p is None:
                    st.error("❌ User not found.")
                    st.stop()

                # Step 3: Verify PIN
                if udata_p.get("pin") != hash_pin(pin_p):
                    st.error("❌ Incorrect PIN.")
                    st.stop()

                st.success(f"✅ PIN verified for **{udata_p.get('name')}**")

                # Step 4: Check iris enrolled
                stored_vec = get_iris_vector(uid_p)
                if stored_vec is None:
                    st.error("❌ User iris not enrolled. Enroll first.")
                    st.stop()

                # Step 5: Liveness + Iris capture
                st.info("👁️ Ask the user to look at the camera and **blink once**.")
                with st.spinner("Waiting for user..."):
                    input_vec, blinked = live_iris_capture(require_blink=True)

                if input_vec is None:
                    st.error("❌ Iris capture failed. Try again.")
                    st.stop()

                if not blinked:
                    st.error("❌ Liveness check failed. Blink not detected.")
                    st.stop()

                # Step 6: Match iris
                score = cosine_similarity(input_vec, stored_vec)
                st.write(f"🔬 Iris match score: `{score:.4f}`")

                THRESHOLD = 0.92
                if score < THRESHOLD:
                    st.markdown(
                        f'<div class="warning-banner">❌ IRIS MISMATCH — '
                        f'Score: {score:.4f} (Required: ≥{THRESHOLD})</div>',
                        unsafe_allow_html=True
                    )
                    st.stop()

                # Step 7: Check balance
                balance = float(udata_p.get("balance", 0))
                if balance < amount_p:
                    st.error(f"❌ Insufficient balance. Available: ₹{balance:.2f}")
                    st.stop()

                # Step 8: Execute transaction
                new_user_balance     = balance - amount_p
                new_merchant_balance = float(mdata.get("balance", 0)) + amount_p
                txn_time             = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                # Update balances
                db.child("users").child(uid_p).update({"balance": new_user_balance})
                db.child("merchants").child(mid).update({"balance": new_merchant_balance})

                # Save transaction history
                db.child("users").child(uid_p).child("history").push({
                    "amount": amount_p,
                    "to":     mdata.get("shop_name"),
                    "time":   txn_time,
                    "status": "SUCCESS"
                })
                db.child("merchants").child(mid).child("history").push({
                    "amount": amount_p,
                    "from":   phone_p,
                    "time":   txn_time,
                    "status": "SUCCESS"
                })

                # ── STEP 9: Send notifications to BOTH parties ────────
                send_payment_notifications(
                    uid       = uid_p,
                    user_name = udata_p.get("name", phone_p),
                    mid       = mid,
                    shop_name = mdata.get("shop_name", "Merchant"),
                    amount    = amount_p,
                    txn_time  = txn_time
                )
                # ──────────────────────────────────────────────────────

                st.markdown(f"""
                <div class="success-banner">
                    🎉 PAYMENT SUCCESSFUL<br><br>
                    ₹{amount_p:.2f} received from {udata_p.get('name')}<br>
                    <small style="font-size:0.7rem; letter-spacing:1px;">{txn_time}</small>
                </div>
                """, unsafe_allow_html=True)

                st.info(
                    "🔔 Notification sent to **user** (debit alert) "
                    "and stored for **merchant** (credit alert). "
                    "Both parties will see it on their next dashboard refresh."
                )

                # Refresh merchant session data
                st.session_state.merchant_data = db.child("merchants").child(mid).get().val()

        # ---- HISTORY ----
        elif option == "📋 Transaction History":

            st.markdown("#### 📋 TRANSACTION HISTORY")
            history = db.child("merchants").child(mid).child("history").get()

            if history and history.each():
                for h in history.each():
                    val = h.val()
                    st.markdown(f"""
                    <div class="txn-row">
                        💰 <b>₹{val.get('amount', 0)}</b> from {val.get('from', 'Unknown')}
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        🕐 {val.get('time', '')}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No transactions yet.")