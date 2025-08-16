Bill Assistant is a Streamlit web application that lets you:
\nUpload bill/receipt images
\nExtract text 
\nStore and query extracted data
\nChat with an AI assistant that remembers context

app.py: uses Pytesseract to extract the data. This is the main app that is deployed on streamlit.
\napp2.py: uses EasyOCR to extract the data. Performs slighlty better on tabular data but overall performance and speed is worse.

Run the following command to launch the app:
\nstreamit run app.py
