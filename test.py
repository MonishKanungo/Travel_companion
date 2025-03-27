import google.generativeai as genai

GENAI_API_KEY = "AIzaSyB3kV_-Q3b2ftVsBUCN_OcprTdMtgN8weg"
genai.configure(api_key=GENAI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Test")
print(response.text)
