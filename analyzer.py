import requests
from bs4 import BeautifulSoup
import json
import google.generativeai as genai
import streamlit as st

api_key = st.secrets["api_keys"]["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Load technology signatures from JSON file
with open("technologies.json", "r") as f:
    tech_data = json.load(f)

tech_logos = {
    "React": "https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original.svg",
    "Angular": "https://raw.githubusercontent.com/devicons/devicon/master/icons/angularjs/angularjs-original.svg",
    "Vue": "https://raw.githubusercontent.com/devicons/devicon/master/icons/vuejs/vuejs-original.svg",
    "Bootstrap": "https://raw.githubusercontent.com/devicons/devicon/master/icons/bootstrap/bootstrap-original.svg",
    "Tailwind": "https://raw.githubusercontent.com/devicons/devicon/master/icons/tailwindcss/tailwindcss-plain.svg",
    "jQuery": "https://raw.githubusercontent.com/devicons/devicon/master/icons/jquery/jquery-original.svg",
    "Node.js": "https://raw.githubusercontent.com/devicons/devicon/master/icons/nodejs/nodejs-original.svg",
    "Python": "https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg",
    "Django": "https://raw.githubusercontent.com/devicons/devicon/master/icons/django/django-plain.svg",
    "Next.js": "https://raw.githubusercontent.com/devicons/devicon/master/icons/nextjs/nextjs-original.svg"
}

def detect_technologies(url):
    try:
        response = requests.get(url, timeout=10)
        html = response.text.lower()
    except Exception as e:
        return {"error": str(e)}

    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    links = soup.find_all("link")
    metas = soup.find_all("meta")

    detected = {category: [] for category in tech_data.keys()}

    for category, frameworks in tech_data.items():
        for keyword, name in frameworks.items():
            keyword = keyword.lower()
            if (
                any(keyword in str(tag).lower() for tag in scripts + links + metas)
                or keyword in html
            ):
                detected[category].append(name)

    # Remove duplicates + empty categories
    detected = {cat: list(set(frameworks)) for cat, frameworks in detected.items() if frameworks}
    return detected

def analyze_with_ai(detected_data, url):
    prompt = f"""
    I scanned the website: {url}
    and detected these technologies/frameworks:

    {json.dumps(detected_data, indent=2)}

    Please analyze and give short summaries for each:
    1. What kind of stack this is (frontend, backend, databases, frameworks, etc.)
    2. Why the developers might have chosen these.
    3. Strengths and weaknesses of the stack.
    4. What type of product/website this could be.
    """

    response = model.generate_content(prompt)
    return response.text


st.set_page_config(page_title="AI Website Tech Analyzer", layout="wide", page_icon="🌐")
st.title("🌐 AI Website Tech Stack Analyzer")

# Sidebar input
url = st.sidebar.text_input("Enter Website URL:")

if st.sidebar.button("Analyze") and url:
    with st.spinner("Detecting technologies..."):
        results = detect_technologies(url)

    if "error" in results:
        st.error(results["error"])
    else:
        # Columns for detected tech and AI analysis
        col1, col2 = st.columns([1,2])

        with col1:
            st.subheader("🛠 Detected Technologies")
            for category, frameworks in results.items():
                st.markdown(f"**{category.replace('_',' ').title()}:**")
                for fw in frameworks:
                    logo = tech_logos.get(fw, None)
                    col_logo, col_name = st.columns([1,5])
                    if logo:
                        with col_logo:
                            st.image(logo, width=30)
                    with col_name:
                        st.write(fw)


        with col2:
            st.subheader("🤖 AI Analysis")
            with st.expander("Show AI Analysis"):
                # Split long text into paragraphs for readability
                for para in analyze_with_ai(results, url).split("\n\n"):
                    st.write(para)
            st.download_button("Download Analysis", analyze_with_ai(results, url), file_name="analysis.txt")

else:
    st.info("Enter a URL in the sidebar and click Analyze.")
