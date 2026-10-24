
import streamlit as st
import json
import os
import html
from pathlib import Path
from datetime import datetime, timedelta

from google import genai
from google.genai import types


# ============================================
# MESSY - HACKATHON DEMO EDITION
# ============================================

st.set_page_config(
    page_title="Messy | Your Mess Companion",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MODEL = "gemma-4-26b-a4b-it"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "messy_data.json"


# ============================================
# CLEAN, HIGH-CONTRAST DESIGN
# ============================================

st.markdown("""
<style>
    :root {
        color-scheme: light;
    }

    .stApp {
        background: #F6F4FA !important;
        color: #21182F !important;
    }

    .block-container {
        max-width: 1120px !important;
        padding-top: 1.3rem !important;
        padding-bottom: 2rem !important;
    }

    .stApp h1,
    .stApp h2,
    .stApp h3 {
        color: #29183F !important;
        font-weight: 750 !important;
    }

    .stApp p,
    .stApp label {
        color: #30263F;
    }

    .hero {
        background: #57348D;
        border-radius: 20px;
        padding: 30px 34px;
        margin-bottom: 18px;
    }

    .hero-title {
        color: #FFFFFF !important;
        font-size: 42px;
        font-weight: 800;
        line-height: 1.2;
    }

    .hero-subtitle {
        color: #FFFFFF !important;
        font-size: 19px;
        font-weight: 600;
        margin-top: 6px;
    }

    .hero-note {
        color: #EEE4FF !important;
        font-size: 14px;
        margin-top: 10px;
    }

    .meal-card {
        background: #FFFFFF;
        border: 2px solid #DED3EB;
        border-radius: 16px;
        padding: 22px;
        min-height: 150px;
        margin-bottom: 12px;
    }

    .meal-title {
        color: #503080 !important;
        font-size: 19px;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .meal-body {
        color: #21182F !important;
        font-size: 16px;
        font-weight: 500;
        line-height: 1.8;
    }

    .info-card {
        background: #FFFFFF;
        border: 1px solid #DDD2EB;
        border-radius: 15px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }

    .info-title {
        color: #38204F !important;
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .info-body {
        color: #30263F !important;
        font-size: 15px;
        line-height: 1.6;
    }

    .info-meta {
        color: #5C526A !important;
        font-size: 13px;
        margin-top: 9px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF !important;
        border: 1px solid #D9CBEA !important;
        border-radius: 10px !important;
        padding: 12px 15px !important;
    }

    .stTabs [data-baseweb="tab"] p {
        color: #392451 !important;
        font-weight: 750 !important;
        font-size: 15px !important;
    }

    .stTabs [aria-selected="true"] {
        background: #57348D !important;
        border-color: #57348D !important;
    }

    .stTabs [aria-selected="true"] p {
        color: #FFFFFF !important;
    }

    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 2px solid #DED3EB !important;
        border-radius: 16px !important;
        padding: 20px !important;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #DED3EB !important;
        border-radius: 14px !important;
        padding: 17px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #503080 !important;
    }

    div[data-testid="stMetricLabel"] p {
        color: #473756 !important;
    }

    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        color: #21182F !important;
    }

    input, textarea {
        color: #21182F !important;
        -webkit-text-fill-color: #21182F !important;
    }

    .stButton button[kind="primary"],
    .stFormSubmitButton button[kind="primary"] {
        background: #57348D !important;
        border-color: #57348D !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
    }

    .stButton button[kind="primary"] p,
    .stFormSubmitButton button[kind="primary"] p {
        color: #FFFFFF !important;
    }

    div[data-testid="stCaptionContainer"] p {
        color: #5C526A !important;
    }
</style>
""", unsafe_allow_html=True)


# DARK MODE VISIBILITY FIX

st.markdown("""
<style>
.stApp,
[data-testid="stAppViewContainer"] {
    background: #14101F !important;
    color: #FFFFFF !important;
    color-scheme: dark !important;
}

.stApp h1, .stApp h2, .stApp h3,
.stApp p, .stApp label {
    color: #F8F4FF !important;
}

/* Dark cards with readable text */
.meal-card, .info-card,
div[data-testid="stForm"],
div[data-testid="stMetric"] {
    background: #241B35 !important;
    border: 1px solid #594675 !important;
}

.meal-title, .info-title,
.meal-body, .info-body {
    color: #FFFFFF !important;
}

.info-meta {
    color: #D2C5E5 !important;
}

/* All input boxes */
div[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
    background: #302540 !important;
    border-color: #8C72B1 !important;
    color: #FFFFFF !important;
}

/* Typed text */
input, textarea {
    background: #302540 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Dropdown selected text */
div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Dropdown menus */
div[data-baseweb="popover"],
ul[role="listbox"],
li[role="option"] {
    background: #302540 !important;
    color: #FFFFFF !important;
}

/* Placeholder text */
input::placeholder, textarea::placeholder {
    color: #D2C5E5 !important;
    opacity: 1 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background: #241B35 !important;
    border: 1px solid #594675 !important;
}

.stTabs [data-baseweb="tab"] p {
    color: #FFFFFF !important;
}

.stTabs [aria-selected="true"] {
    background: #794CC0 !important;
}

/* Buttons */
.stButton button[kind="primary"],
.stFormSubmitButton button[kind="primary"] {
    background: #8958D0 !important;
    color: #FFFFFF !important;
}

.stButton button[kind="primary"] p,
.stFormSubmitButton button[kind="primary"] p {
    color: #FFFFFF !important;
}

/* Captions */
div[data-testid="stCaptionContainer"] p {
    color: #D2C5E5 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# SAMPLE MENU AND SAVED DATA
# ============================================

def default_data():
    return {
        "menu": {
            "Monday": {
                "Breakfast": ["Poha", "Tea"],
                "Lunch": ["Dal", "Rice", "Roti", "Sabji"],
                "Dinner": ["Paneer", "Roti", "Rice"]
            },
            "Tuesday": {
                "Breakfast": ["Paratha", "Tea"],
                "Lunch": ["Rajma", "Rice", "Roti"],
                "Dinner": ["Dal", "Roti", "Sabji"]
            },
            "Wednesday": {
                "Breakfast": ["Upma", "Tea"],
                "Lunch": ["Chole", "Rice", "Roti"],
                "Dinner": ["Dal", "Roti", "Rice"]
            },
            "Thursday": {
                "Breakfast": ["Idli", "Sambar"],
                "Lunch": ["Dal", "Rice", "Sabji"],
                "Dinner": ["Roti", "Mix Veg", "Rice"]
            },
            "Friday": {
                "Breakfast": ["Poha", "Tea"],
                "Lunch": ["Kadhi", "Rice", "Roti"],
                "Dinner": ["Paneer", "Roti"]
            },
            "Saturday": {
                "Breakfast": ["Paratha", "Tea"],
                "Lunch": ["Dal", "Rice", "Sabji"],
                "Dinner": ["Veg Pulao", "Raita"]
            },
            "Sunday": {
                "Breakfast": ["Aloo Paratha", "Tea"],
                "Lunch": ["Chole", "Rice", "Roti"],
                "Dinner": ["Special Dinner", "Sweet"]
            }
        },
        "ratings": [],
        "reports": [],
        "suggestions": []
    }


def load_data():
    DATA_DIR.mkdir(exist_ok=True)

    if not DATA_FILE.exists():
        return default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)

        if not isinstance(saved, dict):
            raise ValueError("Invalid saved data")

        defaults = default_data()

        for key, value in defaults.items():
            saved.setdefault(key, value)

        return saved

    except (OSError, ValueError, TypeError):
        st.error(
            "Saved data could not be loaded. "
            "Please check data/messy_data.json."
        )
        st.stop()


data = load_data()


def save_data():
    DATA_DIR.mkdir(exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================
# HELPER FUNCTIONS
# ============================================

def now_text():
    return datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )


def safe(value):
    return html.escape(str(value))


def all_dishes():
    dishes = set()

    for day in data["menu"].values():
        for meal in day.values():
            dishes.update(meal)

    for rating in data["ratings"]:
        if rating.get("dish"):
            dishes.add(rating["dish"])

    return sorted(dishes)


def dish_average(dish):
    scores = []

    for rating in data["ratings"]:
        if rating.get("dish") == dish:
            try:
                scores.append(int(rating["stars"]))
            except (KeyError, TypeError, ValueError):
                pass

    if not scores:
        return None, 0

    return sum(scores) / len(scores), len(scores)


def parse_time(value):
    formats = [
        "%d %b %Y, %I:%M %p",
        "%Y-%m-%d %H:%M:%S"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue

    return None


def freshness(report):
    timestamp = parse_time(report.get("time"))

    if not timestamp:
        return "Time unavailable", False

    minutes = int(
        (datetime.now() - timestamp).total_seconds() / 60
    )

    if minutes < 0:
        return "Timestamp needs checking", False

    if minutes <= 2:
        return "Just reported", True

    if minutes < 60:
        return f"{minutes} minutes ago", True

    if minutes <= 120:
        return f"{minutes // 60} hour(s) ago", True

    return "Older update", False


def show_card(title, body, meta=""):
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">{safe(title)}</div>
            <div class="info-body">{safe(body)}</div>
            <div class="info-meta">{safe(meta)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_menu(day):
    meals = data["menu"].get(day, {})

    icons = {
        "Breakfast": "🌅",
        "Lunch": "☀️",
        "Dinner": "🌙"
    }

    cols = st.columns(3)

    for i, meal in enumerate(
        ["Breakfast", "Lunch", "Dinner"]
    ):
        dishes = meals.get(meal, [])

        with cols[i]:
            st.markdown(
                f"""
                <div class="meal-card">
                    <div class="meal-title">
                        {icons[meal]} {meal}
                    </div>
                    <div class="meal-body">
                        {safe(", ".join(dishes) if dishes else "Not updated")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================
# GEMMA 4
# ============================================

def get_client():
    key = os.getenv("GEMINI_API_KEY", "").strip()

    if not key:
        return None, (
            "GEMINI_API_KEY is missing. "
            "Set it in Command Prompt before "
            "starting the app."
        )

    try:
        return genai.Client(api_key=key), None

    except Exception as error:
        return None, str(error)


def test_gemma():
    client, error = get_client()

    if error:
        return False, error

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents="Say: Messy AI connection successful."
        )

        if response.text:
            return True, response.text

        return False, "Gemma returned an empty response."

    except Exception as error:
        return False, str(error)


def analyze_feedback():
    client, error = get_client()

    if error:
        return None, error

    if not (
        data["ratings"]
        or data["reports"]
        or data["suggestions"]
    ):
        return None, "No feedback has been submitted yet."

    averages = {}

    for dish in all_dishes():
        avg, count = dish_average(dish)

        if avg is not None:
            averages[dish] = {
                "average": round(avg, 2),
                "count": count
            }

    payload = {
        "ratings": data["ratings"][-100:],
        "reports": data["reports"][-100:],
        "suggestions": data["suggestions"][-100:],
        "averages": averages,
        "current_time": now_text()
    }

    prompt = f"""
You are Gemma 4 inside Messy,
a hostel mess food feedback application.

Analyze the following student-submitted data:

{json.dumps(payload, ensure_ascii=False)}

Write a clear report with these sections:

1. OVERALL FEEDBACK
2. REPEATED PROBLEMS
3. PRIORITY: HIGH, MEDIUM OR LOW
4. PRACTICAL IMPROVEMENTS
5. POSITIVE FEEDBACK
6. STUDENT SUGGESTIONS
7. MANAGEMENT ACTION PLAN

Rules:
- Use actual submitted evidence only.
- Do not invent complaints or statistics.
- Identify repeated complaints carefully.
- Treat student reports as unverified.
- Consider timestamps for live reports.
- Explain priorities in simple language.
- Recommend affordable, practical solutions.
- State when there is not enough evidence.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        if not response.text:
            return None, "Gemma returned an empty report."

        return response.text, None

    except Exception as error:
        return None, str(error)


def read_menu_image(photo):
    client, error = get_client()

    if error:
        return None, error

    try:
        part = types.Part.from_bytes(
            data=photo.getvalue(),
            mime_type=photo.type
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=[
                part,
                """
                Read this hostel mess menu photograph.
                Extract the visible days and meals.
                Organize into breakfast, lunch and dinner.
                Do not invent unreadable text.
                """
            ]
        )

        if not response.text:
            return None, "No menu text was extracted."

        return response.text, None

    except Exception as error:
        return None, str(error)


# ============================================
# HEADER
# ============================================

st.markdown("""
<div class="hero">
    <div class="hero-title">🍽️ Messy</div>
    <div class="hero-subtitle">
        Your mess. Your voice. Your choice.
    </div>
    <div class="hero-note">
        A smarter way to experience hostel meals.
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================
# FIVE TABS
# ============================================

home, rate, updates, menu, ai = st.tabs([
    "🏠 Home",
    "⭐ Rate Food",
    "📢 Live Updates",
    "📅 Mess Menu",
    "✨ Gemma AI"
])


# ============================================
# HOME
# ============================================

with home:

    today = datetime.now().strftime("%A")

    st.header("Welcome to Messy 👋")

    st.write(
        "Everything about your hostel mess, "
        "in one simple place."
    )

    st.subheader(f"🍽️ Today's Menu · {today}")

    show_menu(today)

    st.caption(
        "The menu currently contains sample data."
    )

    st.divider()

    st.subheader("💜 Community Activity")

    c1, c2, c3 = st.columns(3)

    c1.metric("Food Ratings", len(data["ratings"]))
    c2.metric("Student Updates", len(data["reports"]))
    c3.metric("Dish Suggestions", len(data["suggestions"]))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("⭐ Student Favorites")

        dishes = []

        for dish in all_dishes():
            avg, count = dish_average(dish)

            if avg is not None:
                dishes.append((dish, avg, count))

        dishes.sort(
            key=lambda x: (-x[1], -x[2])
        )

        if not dishes:
            st.info("No food ratings yet.")

        for dish, avg, count in dishes[:4]:
            show_card(
                dish,
                f"⭐ {avg:.1f} out of 5",
                f"{count} student rating(s)"
            )

    with right:
        st.subheader("📢 Recent Updates")

        if not data["reports"]:
            st.info("No student updates yet.")

        for report in reversed(data["reports"][-4:]):
            label, _ = freshness(report)

            show_card(
                report.get("dish", "Mess update"),
                report.get("status", ""),
                label
            )


# ============================================
# RATE FOOD
# ============================================

with rate:

    st.header("⭐ Rate Your Food")

    st.write(
        "Tell us what you liked and "
        "what needs improvement."
    )

    with st.form(
        "rating_form",
        clear_on_submit=True
    ):

        dish = st.selectbox(
            "Select a dish",
            all_dishes()
        )

        stars = st.radio(
            "Give your rating",
            [1, 2, 3, 4, 5],
            index=2,
            horizontal=True,
            format_func=lambda x: f"{x} ⭐"
        )

        tags = st.multiselect(
            "Describe your experience",
            [
                "Delicious",
                "Fresh",
                "Good quantity",
                "Too salty",
                "Too spicy",
                "Too oily",
                "Cold food",
                "Small portion",
                "Needs improvement"
            ]
        )

        comment = st.text_area(
            "Your feedback",
            placeholder="Write your experience here..."
        )

        submitted = st.form_submit_button(
            "Submit Rating",
            type="primary"
        )

    if submitted:

        data["ratings"].append({
            "dish": dish,
            "stars": stars,
            "tags": tags,
            "comment": comment.strip(),
            "time": now_text()
        })

        save_data()

        st.success("Rating submitted successfully!")

    st.divider()

    st.subheader("💬 Recent Reviews")

    if not data["ratings"]:
        st.info("No reviews submitted yet.")

    for rating in reversed(data["ratings"][-8:]):

        try:
            score = int(rating.get("stars", 0))
        except (TypeError, ValueError):
            score = 0

        description = rating.get("comment", "")

        if not description:
            description = ", ".join(
                rating.get("tags", [])
            )

        if not description:
            description = "Rating submitted"

        show_card(
            f"{rating.get('dish', 'Dish')} · {'⭐' * max(0, min(score, 5))}",
            description,
            rating.get("time", "")
        )


# ============================================
# LIVE UPDATES
# ============================================

with updates:

    st.header("📢 Live Student Updates")

    st.write(
        "Share queue lengths and food availability "
        "with other students."
    )

    st.caption(
        "Student-submitted updates are not "
        "automatically verified."
    )

    report_type = st.selectbox(
        "What would you like to report?",
        ["Queue Length", "Food Availability"]
    )

    report_dish = st.selectbox(
        "Select dish or counter",
        all_dishes()
    )

    with st.form("update_form"):

        if report_type == "Queue Length":

            status = st.radio(
                "Queue status",
                [
                    "Short Queue",
                    "Medium Queue",
                    "Long Queue"
                ]
            )

        else:

            status = st.radio(
                "Food status",
                [
                    "Available",
                    "Running Low",
                    "Finished"
                ]
            )

        send = st.form_submit_button(
            "Share Update",
            type="primary"
        )

    if send:

        data["reports"].append({
            "dish": report_dish,
            "type": report_type,
            "status": status,
            "time": now_text()
        })

        save_data()

        st.success("Update shared successfully!")

    st.divider()

    recent_tab, old_tab = st.tabs([
        "🟢 Recent",
        "🕒 Earlier"
    ])

    with recent_tab:

        recent_reports = [
            r for r in data["reports"]
            if freshness(r)[1]
        ]

        if not recent_reports:
            st.info(
                "No updates submitted within "
                "the last two hours."
            )

        for report in reversed(recent_reports[-15:]):
            label, _ = freshness(report)

            show_card(
                report.get("dish", "Mess update"),
                report.get("status", ""),
                label
            )

    with old_tab:

        older_reports = [
            r for r in data["reports"]
            if not freshness(r)[1]
        ]

        if not older_reports:
            st.info("No earlier updates.")

        for report in reversed(older_reports[-15:]):

            show_card(
                report.get("dish", "Mess update"),
                report.get("status", ""),
                report.get("time", "")
            )


# ============================================
# MESS MENU
# ============================================

with menu:

    st.header("📅 Mess Menu")

    st.write(
        "See what's cooking today, tomorrow, "
        "or on another day."
    )

    today = datetime.now().strftime("%A")

    tomorrow = (
        datetime.now() + timedelta(days=1)
    ).strftime("%A")

    choice = st.radio(
        "Choose a menu",
        ["Today", "Tomorrow", "Other Day"],
        horizontal=True
    )

    if choice == "Today":
        day = today

    elif choice == "Tomorrow":
        day = tomorrow

    else:
        day = st.selectbox(
            "Select day",
            list(data["menu"].keys())
        )

    st.subheader(f"🍽️ {day}'s Meals")

    show_menu(day)

    st.divider()

    st.subheader("💡 Suggest a Dish")

    with st.form(
        "suggestion_form",
        clear_on_submit=True
    ):

        suggested_dish = st.text_input(
            "Dish name",
            placeholder="Example: Chole Bhature"
        )

        reason = st.text_area(
            "Why should it be added?"
        )

        suggest = st.form_submit_button(
            "Send Suggestion",
            type="primary"
        )

    if suggest:

        if not suggested_dish.strip():
            st.warning("Enter a dish name.")

        else:

            data["suggestions"].append({
                "dish": suggested_dish.strip(),
                "reason": reason.strip(),
                "time": now_text()
            })

            save_data()

            st.success("Suggestion submitted!")

    st.divider()

    st.subheader("📷 Read a Menu Photo")

    photo = st.file_uploader(
        "Upload a menu image",
        type=["png", "jpg", "jpeg"]
    )

    if photo:

        st.image(
            photo,
            use_container_width=True
        )

        if st.button(
            "✨ Read with Gemma 4",
            type="primary"
        ):

            with st.spinner(
                "Gemma is reading the menu..."
            ):
                result, error = read_menu_image(photo)

            if error:
                st.error("Menu reading failed.")
                st.code(error)

            else:
                st.markdown(result)

                st.caption(
                    "Verify the extracted text "
                    "against the original image."
                )


# ============================================
# GEMMA AI
# ============================================

with ai:

    st.header("✨ Gemma 4 AI")

    st.write(
        "Messy's AI turns student feedback "
        "into practical suggestions for "
        "mess management."
    )

    st.subheader("🔌 Test AI Connection")

    if st.button("Test Gemma 4"):

        with st.spinner("Checking AI connection..."):
            working, message = test_gemma()

        if working:
            st.success("Gemma 4 is responding!")
            st.write(message)

        else:
            st.error("Gemma 4 is not responding.")
            st.code(message)

    st.divider()

    st.subheader("🧠 AI Problem Detector")

    st.write(
        "Find repeated complaints, identify "
        "important issues, and suggest solutions."
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Ratings", len(data["ratings"]))
    c2.metric("Reports", len(data["reports"]))
    c3.metric("Suggestions", len(data["suggestions"]))

    if st.button(
        "✨ Analyze Student Feedback",
        type="primary"
    ):

        with st.spinner(
            "Gemma is analyzing feedback..."
        ):
            report, error = analyze_feedback()

        if error:
            st.session_state.pop(
                "messy_report", None
            )
            st.error("AI analysis failed.")
            st.code(error)

        else:
            st.session_state["messy_report"] = report

    if "messy_report" in st.session_state:

        st.divider()

        st.subheader("📋 Management Report")

        st.markdown(
            st.session_state["messy_report"]
        )

        st.download_button(
            "📥 Download Report",
            data=st.session_state["messy_report"],
            file_name="Messy_Management_Report.txt",
            mime="text/plain"
        )

        st.caption(
            "AI suggestions are based on "
            "student-submitted information "
            "and require human verification."
        )


# ============================================
# FOOTER
# ============================================

st.divider()

st.caption(
    "🍽️ Messy · Your mess. Your voice. Your choice. "
    "· Powered by Gemma 4"
)
