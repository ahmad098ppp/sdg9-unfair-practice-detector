import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import io

# --- Load environment variables ---
load_dotenv()

# --- Configure the Gemini API ---
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("GOOGLE_API_KEY not found. Please ensure it's set in your .env file.")
        st.stop()
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

# --- Gemini Model Configuration ---
try:
    vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model
    text_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error initializing Gemini models: {e}")
    st.stop()

# --- Analysis Function ---
def analyze_content(prompt, content_input):
    try:
        if isinstance(content_input, str):
            if not content_input.strip():
                return "Error: Please provide some text to analyze."
            model_input = [prompt, content_input]
            response = text_model.generate_content(model_input)
            return response.text

        elif isinstance(content_input, Image.Image):
            model_input = [prompt, content_input]
            response = vision_model.generate_content(model_input, stream=False)
            response.resolve()
            return response.text

        else:
            return "Error: Invalid input type provided."

    except Exception as e:
        error_message = f"An error occurred during analysis: {str(e)}"
        if "API key not valid" in str(e):
            error_message += "\nPlease check if your GOOGLE_API_KEY is configured correctly."
        elif "content has been blocked" in str(e).lower() or "safety settings" in str(e).lower():
            error_message += "\nThe input may have triggered Google's safety filters."
        elif "Resource has been exhausted" in str(e) or "quota" in str(e).lower():
            error_message += "\nAPI quota likely exceeded. Check your usage limits."
        elif "Deadline exceeded" in str(e):
            error_message += "\nThe request timed out. Try again later."

        print(f"Gemini API Error: {e}")
        return f"Error during analysis. Details: {error_message}"

# --- Define the Core Prompt ---
SDG9_PROMPT = """
You are an AI assistant specialized in analyzing violations of Sustainable Development Goal 9 (Industry, Innovation, and Infrastructure), focusing specifically on signs of unfair or unsustainable industrial practices based only on the provided input (text description or image).

Analyze the provided input:
1. Identify any visual or described elements that might indicate issues related to SDG 9, such as(what given below are only examples, you can bring any element you find, so consuder everything profoundly ):
   * Unsustainable Industrialization: Excessive smoke/pollution, improper waste disposal, environmental damage (e.g., polluted water, deforestation near factories).
   * Lack of Resilient Infrastructure: Visibly unsafe factory buildings, damaged infrastructure caused by industrial activity.
   * Non-Inclusive/Unfair Labor Practices (Visual Cues): Lack of safety equipment, signs of child labor, overcrowded or unsafe environments.
   * Technological Gaps: Outdated, poorly maintained, or highly polluting machinery.
2. Explain your reasoning for each identified element, linking it to SDG 9 concerns, profoundly and precisely in the narrative of UN and SDG literature, as if you are an officer of the UN. Acknowledge ONLY and only if input provides limited evidence or if interpretations are uncertain.
3. If no clear indicators are found, state that clearly.

4. (show Analysis Report instead of conclusion)"Analysis Report": If it violates SDG 9, then in the very first sentence, state it starting with "YES" (If you have too much uncertainties due to too much limited evidence on the input say Maybe YES type of things); if it doesn't, then state it starting with "NO". Make very strong, definitive judgments, as if the judgment is universal. (Focus on indicators which are violating SDG 9 and be very acute in your observation.)
"""

# --- Streamlit App UI ---
st.set_page_config(page_title="SDG 9 aiD", layout="wide")

# --- App Header and Description ---
st.markdown("""
    <style>
    .header {
        text-align: center;
        color: #0D47A1;
        font-size: 2em;
        font-weight: bold;
    }
    .description {
        text-align: center;
        color: #1565C0;
        font-size: 1.2em;
        margin-top: -10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header">SDG 9 aiD</div>', unsafe_allow_html=True)
st.markdown('<div class="description">A tool to analyze industrial practices and their alignment with Sustainable Development Goal 9</div>', unsafe_allow_html=True)

st.write("""
    This AI tool, created by AHMAD ABDULLAH, helps analyze text or images to detect potential violations of **Sustainable Development Goal 9 (Industry, Innovation, and Infrastructure)**. 
    It aims to identify issues like unsustainable industrialization, unsafe labor practices, and outdated infrastructure.
    **Disclaimer**: This is a prototype tool. Results are indicative, not conclusive proof.
""")
st.markdown("---")

# --- Input Section ---
st.subheader("Provide Input for Analysis:")

input_text = st.text_area("Enter a description of an industrial practice or scene:")
uploaded_image = st.file_uploader("Or upload an image of the industrial scene:", type=["jpg", "jpeg", "png"])

analyze_button = st.button("Analyze Input")

st.markdown("---")

# --- Analysis Area ---
st.subheader("Analysis Results:")
results_area = st.empty()

if analyze_button:
    analysis_input = None
    input_type = None

    # Prioritize uploaded image
    if uploaded_image is not None:
        try:
            image_bytes = uploaded_image.getvalue()
            analysis_input = Image.open(io.BytesIO(image_bytes))
            input_type = "image"
            results_area.info("Analyzing uploaded image... Please wait.")
        except Exception as e:
            results_area.error(f"Error processing image: {e}")
            st.stop()
    elif input_text.strip():
        analysis_input = input_text
        input_type = "text"
        results_area.info("Analyzing text description... Please wait.")
    else:
        results_area.warning("Please enter text or upload an image for analysis.")
        st.stop()

    # Perform analysis if input is valid
    if analysis_input:
        with st.spinner('SDG 9 aiD is analyzing... This may take a moment.'):
            analysis_result = analyze_content(SDG9_PROMPT, analysis_input)

        results_area.markdown(analysis_result)

        if input_type == "image" and analysis_input:
            with st.expander("See Uploaded Image"):
                st.image(analysis_input, caption="Analyzed Image", use_column_width=True)

        # Clear the input fields after analysis
        input_text = ""
        uploaded_image = None

        # Add a download button for the analysis result
        st.download_button(
            label="Download Analysis Result",
            data=analysis_result,
            file_name="analysis_result.txt",
            mime="text/plain"
        )

else:
    results_area.info("Enter text or upload an image and click 'Analyze Input'.")

