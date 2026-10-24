
import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types


# ==========================================
# MESSY - HOSTEL MESS ASSISTANT
# ==========================================

st.set_page_config(
    page_title="Messy - Hostel Mess Assistant",
    page_icon="🍽️",
    layout="wide"
)

MODEL = "gemma-4-26b-a4b-it"

APP_FOLDER = Path(__file__).parent
DATA_FOLDER = APP_FOLDER / "data"
DATA_FILE = DATA_FOLDER / "messy_data.json"


# ==========================================
# DATA STORAGE
# ==========================================

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


def save_data(data):
    DATA_FOLDER.mkdir(exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_data():
    DATA_FOLDER.mkdir(exist_ok=True)

    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            st.error(
                "The saved data file could not be read. "
                "Please check the data folder."
            )
            st.stop()

    data = default_data()
    save_data(data)
    return data


data = load_data()


def current_time():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


def get_all_dishes():
    dishes = set()

    for day in data["menu"].values():
        for meal in day.values():
            dishes.update(meal)

    return sorted(dishes)


def calculate_average(dish):
    scores = [
        rating["stars"]
        for rating in data["ratings"]
        if rating["dish"] == dish
    ]

    if not scores:
        return None

    return sum(scores) / len(scores)


# ==========================================
# GEMMA 4 API CONNECTION
# ==========================================

def get_ai_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def gemma_feedback_summary():
    client = get_ai_client()

    if client is None:
        return (
            "API key not found. Set GEMINI_API_KEY "
            "in Command Prompt and restart the app."
        )

    averages = {}

    for dish in get_all_dishes():
        average = calculate_average(dish)

        if average is not None:
            count = sum(
                1 for rating in data["ratings"]
                if rating["dish"] == dish
            )

            averages[dish] = {
                "average": round(average, 2),
                "number_of_ratings": count
            }

    prompt = f"""
You are the AI assistant for Messy, a hostel mess application.

Analyze this actual student feedback.

Food ratings calculated by Python:
{json.dumps(averages)}

Individual ratings and comments:
{json.dumps(data["ratings"])}

Student queue and availability reports:
{json.dumps(data["reports"])}

Student suggestions:
{json.dumps(data["suggestions"])}

Instructions:
1. Summarize actual student feedback.
2. Identify repeated complaints, if any.
3. Mention positive feedback when present.
4. Suggest realistic improvements.
5. Never invent ratings, complaints, or reports.
6. Clearly state that student reports are unverified.
7. If there is insufficient data, say so.
8. Use simple English.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text or "Gemma returned an empty response."

    except Exception as error:
        return f"Gemma API error: {error}"


def gemma_read_menu(photo):
    client = get_ai_client()

    if client is None:
        return "API key not found. Set GEMINI_API_KEY first."

    try:
        image_part = types.Part.from_bytes(
            data=photo.getvalue(),
            mime_type=photo.type
        )

        prompt = """
Read this hostel mess menu photograph.

Extract the visible:
- Day names
- Meal names
- Food dishes

Keep the original wording.

Do not invent missing information.
Mark unreadable words as [unclear].
Present the result as a readable draft.
Remind the user to verify it before publishing.
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=[image_part, prompt]
        )

        return response.text or "No menu text was extracted."

    except Exception as error:
        return f"Gemma image processing error: {error}"


# ==========================================
# WEBSITE HEADING
# ==========================================

st.title("🍽️ Messy")

st.subheader("Your mess. Your voice. Your choice.")

st.write(
    "A student-powered hostel mess assistant "
    "built using Python, Streamlit and Gemma 4."
)




# ==========================================
# WEBSITE TABS
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "⭐ Rate Food",
    "📢 Live Reports",
    "📅 Mess Menu",
    "🤖 Gemma AI"
])


# ==========================================
# DASHBOARD
# ==========================================

with tab1:

    st.header("Messy Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Food Ratings", len(data["ratings"]))
    col2.metric("Student Reports", len(data["reports"]))
    col3.metric("Suggestions", len(data["suggestions"]))

    st.subheader("Dish Ratings")

    rated_dishes = sorted({
        rating["dish"] for rating in data["ratings"]
    })

    if not rated_dishes:
        st.info("No food ratings submitted yet.")

    for dish in rated_dishes:
        average = calculate_average(dish)

        if average is not None:
            count = sum(
                1 for rating in data["ratings"]
                if rating["dish"] == dish
            )

            st.write(
                f"⭐ **{dish}** — {average:.1f}/5 "
                f"({count} rating(s))"
            )

    st.subheader("Recent Student Reports")

    if not data["reports"]:
        st.info("No student reports submitted yet.")

    for report in reversed(data["reports"][-5:]):
        st.write(
            f"**{report['dish']}** — "
            f"{report['type']}: {report['status']}"
        )

        st.caption(
            f"Student-reported at {report['time']}"
        )


# ==========================================
# RATE FOOD
# ==========================================

with tab2:

    st.header("⭐ Rate Your Mess Food")

    st.write("Choose a dish and share your feedback.")

    with st.form("food_rating_form"):

        dish = st.selectbox(
            "Choose a dish",
            get_all_dishes()
        )

        stars = st.radio(
            "How many stars would you give?",
            options=[1, 2, 3, 4, 5],
            index=2,
            horizontal=True,
            format_func=lambda x: f"{x} ⭐"
        )

        feedback_tags = st.multiselect(
            "What did you think?",
            [
                "Delicious",
                "Too spicy",
                "Too salty",
                "Too oily",
                "Cold food",
                "Good quality",
                "Needs improvement"
            ]
        )

        comment = st.text_area(
            "Additional feedback (optional)",
            placeholder="Example: Dal was too salty today."
        )

        submit_rating = st.form_submit_button(
            "Submit Rating"
        )

    if submit_rating:

        data["ratings"].append({
            "dish": dish,
            "stars": stars,
            "tags": feedback_tags,
            "comment": comment.strip(),
            "time": current_time()
        })

        save_data(data)

        st.success("Your rating has been submitted!")


# ==========================================
# LIVE REPORTS - FIXED
# ==========================================

with tab3:

    st.header("📢 Student Live Reports")

    st.warning(
        "These reports are submitted by students. "
        "They are not verified real-time measurements."
    )

    # Outside the form, so changes happen immediately
    report_dish = st.selectbox(
        "Select a dish or counter",
        get_all_dishes(),
        key="report_dish"
    )

    report_type = st.selectbox(
        "What would you like to report?",
        ["Queue Length", "Food Availability"],
        key="report_type"
    )

    with st.form("report_form"):

        if report_type == "Queue Length":

            report_status = st.radio(
                "How long is the queue?",
                [
                    "Short Queue",
                    "Medium Queue",
                    "Long Queue"
                ]
            )

        else:

            report_status = st.radio(
                "Is the dish available?",
                [
                    "Available",
                    "Running Low",
                    "Finished"
                ]
            )

        submit_report = st.form_submit_button(
            "Submit Report"
        )

    if submit_report:

        data["reports"].append({
            "dish": report_dish,
            "type": report_type,
            "status": report_status,
            "time": current_time()
        })

        save_data(data)

        st.success("Your report has been submitted!")

    st.subheader("Recent Reports")

    if not data["reports"]:
        st.info("No reports yet.")

    for report in reversed(data["reports"][-10:]):

        st.write(
            f"**{report['dish']}** — "
            f"{report['type']}: {report['status']}"
        )

        st.caption(
            f"Student-reported: {report['time']}"
        )


# ==========================================
# WEEKLY MESS MENU
# ==========================================

with tab4:

    st.header("📅 Weekly Mess Menu")

    selected_day = st.selectbox(
        "Choose a day",
        list(data["menu"].keys())
    )

    meals = data["menu"][selected_day]

    for meal_name, dishes in meals.items():

        st.subheader(meal_name)

        for food in dishes:
            st.write("🍽️", food)

    st.caption(
        "Sample menu for demonstration. "
        "Confirm the actual menu with the hostel."
    )

    st.divider()

    st.subheader("💡 Suggest a Dish")

    with st.form("menu_suggestion_form"):

        suggested_dish = st.text_input(
            "Which dish would you like?",
            placeholder="Example: Chole Bhature"
        )

        reason = st.text_area(
            "Why would you like this dish?",
            placeholder="Example: Many students enjoy it."
        )

        submit_suggestion = st.form_submit_button(
            "Send Suggestion"
        )

    if submit_suggestion:

        if not suggested_dish.strip():

            st.warning("Please enter a dish name.")

        else:

            data["suggestions"].append({
                "dish": suggested_dish.strip(),
                "reason": reason.strip(),
                "time": current_time(),
                "status": "Unverified student suggestion"
            })

            save_data(data)

            st.success("Your suggestion has been saved!")

    st.divider()

    st.subheader("📷 Read Mess Menu Using Gemma 4")

    uploaded_photo = st.file_uploader(
        "Upload a clear photograph of your mess menu",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_photo:

        st.image(
            uploaded_photo,
            caption="Uploaded Menu",
            use_container_width=True
        )

        if st.button("✨ Read Menu with Gemma 4"):

            with st.spinner("Gemma 4 is reading the menu..."):

                extracted_menu = gemma_read_menu(
                    uploaded_photo
                )

            st.subheader("Extracted Menu Draft")

            st.write(extracted_menu)

            st.warning(
                "Please verify the extracted menu. "
                "AI can make mistakes, and this draft "
                "does not automatically change the menu."
            )


# ==========================================
# GEMMA 4 AI INSIGHTS
# ==========================================

with tab5:

    st.header("🤖 Gemma 4 AI Insights")

    st.write(
        "Gemma 4 summarizes student ratings, "
        "feedback, reports, and suggestions."
    )

    

    if st.button("✨ Generate AI Feedback Summary"):

        with st.spinner("Gemma 4 is analyzing feedback..."):

            summary = gemma_feedback_summary()

        st.subheader("AI Feedback Summary")

        st.write(summary)

    st.warning(
        "AI-generated summaries may contain mistakes. "
        "Student reports should be verified."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Messy | Your mess. Your voice. Your choice. "
    "| Powered by Python, Streamlit and Gemma 4 API"
)
