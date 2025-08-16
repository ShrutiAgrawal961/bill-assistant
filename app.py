import streamlit as st
import pytesseract
# import easyocr
from PIL import Image
from openai import OpenAI
import json
import io

# Load API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Bill Assistant", layout="wide")
st.title("🧾 AI-Powered Bill Assistant")

# Initialize session state
if "bill_data" not in st.session_state:
    st.session_state.bill_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_file = st.file_uploader("📄 Upload a Bill Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", width=400)

    if st.button("Extract Bill Data"):
        with st.spinner("⏳ Extracting..."):
            # Reset old bill data
            st.session_state.bill_data = None

            # Step 1: OCR
            # bill_text = parse_bill_with_easyocr(uploaded_file)
            bill_text = pytesseract.image_to_string(image)
            print(bill_text)  # For debugging purposes

            # Step 2: Ask GPT to parse into structured JSON
            schema_prompt = f"""
            Extract the following fields from this bill text and return as JSON:
            - Vendor Name
            - Date
            - Customer Name
            - Bill/Invoice Number
            - Order ID
            - Shipping Address
            - Billing Address
            - PAN Number
            - GST Number 
            - Tax Amount
            - Discount
            - Total Amount 
            - Items (list with name, quantity, price, description)

            Take into account the following instructions:
            - If a field is not present or not applicable, return it as null.
            - For shipping and billing addresses, try to return the full address.
            
            Bill text:
            {bill_text}
            """
            response = client.responses.create(
                model="gpt-5-nano",
                input=schema_prompt
            )

            try:
                bill_json = json.loads(response.output_text)
            except json.JSONDecodeError:
                bill_json = {"error": "Could not parse bill into JSON", "raw_output": response.output_text}

            st.session_state.bill_data = bill_json
        st.success("✅ Bill data extracted and stored!")

#Save Bill JSON
if st.session_state.bill_data:
    json_bytes = io.BytesIO(json.dumps(st.session_state.bill_data, indent=2).encode())
    st.download_button(
        label="💾 Save Extracted Bill JSON",
        data=json_bytes,
        file_name="bill_data.json",
        mime="application/json"
    )

    st.markdown("*➡️ Upload a new bill if you want to query that instead.*")

# Chat Section
st.subheader("💬 Chat with AI")
st.markdown("You can ask questions about the bill data extracted above.")

# Display chat history
for speaker, msg in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"<b>{speaker}: </b>{msg}", unsafe_allow_html=True)
    else:
        st.markdown(f"<b>{speaker}: </b>{msg}", unsafe_allow_html=True) 

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", key="chat_input")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    bill_context = ""
    if st.session_state.bill_data:
        bill_context = f"\nBill Data:\n{json.dumps(st.session_state.bill_data)}\n"

    # Build full conversation history
    conversation = bill_context + "\nConversation so far:\n"
    for speaker, msg in st.session_state.chat_history:
        conversation += f"{speaker}: {msg}\n"

    # Add the latest user input
    conversation += f"You: {user_input}\nAI:"

    with st.spinner("⏳ Generating response..."):
        # Send full conversation to GPT
        response = client.responses.create(
            model="gpt-5-nano",
            input=conversation
        )

        ai_reply = response.output_text

    # Save history
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("AI", ai_reply))

    st.rerun()