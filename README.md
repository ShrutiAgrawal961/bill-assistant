Bill Assistant is a Streamlit web application that lets you:
Upload bill/receipt images
Extract text 
Store and query extracted data
Chat with an AI assistant that remembers context

app.py: uses Pytesseract to extract the data. This is the main app that is deployed on streamlit.
app2.py: uses EasyOCR to extract the data. Performs slighlty better on tabular data but overall performance and speed is worse.
