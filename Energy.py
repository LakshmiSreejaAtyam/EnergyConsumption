import streamlit as st
import google.generativeai as genai
from pymongo import MongoClient
import datetime

# Set your Generative AI API key
genai.configure(api_key="AIzaSyC_IdYlWLiCXtVvn2qlLZIFgD6Rm9Smg5U")  # Replace with your actual API key

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")  # Ensure MongoDB is running
db = client["home_assistance"]
devices_collection = db["devices"]

# Streamlit UI
st.title("🔋 Energy Consumption Tracker with AI Insights")

# Input fields
device_name = st.text_input("Enter Device Name:")
power = st.number_input("Power (W)", min_value=0.0, format="%.2f")
hours = st.number_input("Hours Used per Day", min_value=0.0, format="%.2f")
device_status = st.radio("Device Status:", ["ON", "OFF"])

if st.button("Calculate & Save Data"):
    if device_name and power > 0 and hours > 0:
        # Calculate energy consumption
        daily_consumption = (power * hours) / 1000  # kWh
        monthly_consumption = daily_consumption * 30
        yearly_consumption = daily_consumption * 365

        # Save device status to MongoDB
        device_data = {
            "device_name": device_name,
            "power": power,
            "hours": hours,
            "status": device_status,
            "last_updated": datetime.datetime.now()
        }
        devices_collection.update_one({"device_name": device_name}, {"$set": device_data}, upsert=True)

        # Display consumption results
        st.write(f"### {device_name} Energy Consumption:")
        st.write(f"- *{daily_consumption:.2f} kWh/day*")
        st.write(f"- *{monthly_consumption:.2f} kWh/month*")
        st.write(f"- *{yearly_consumption:.2f} kWh/year*")

        # Manual Energy-Saving Tips
        st.subheader("💡 Manual Energy-Saving Tips")
        st.write("- Turn off devices when not in use.")
        st.write("- Use energy-efficient appliances like LED bulbs.")
        st.write("- Unplug chargers and electronics when not needed.")
        st.write("- Reduce screen brightness and use power-saving modes.")

        # AI-Generated Energy-Saving Tips
        st.subheader("🤖 AI-Generated Energy-Saving Tips")
        prompt = f"Suggest energy-saving tips for a {device_name} consuming {power}W for {hours} hours daily."

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            st.write(response.text)
        except Exception as e:
            st.error("Error generating AI response. Please check your API key.")

    else:
        st.error("⚠ Please enter valid values.")

# **Check Devices Left ON**
st.subheader("🚨 Devices Currently Left ON")
devices_left_on = devices_collection.find({"status": "ON"})
device_list = [d["device_name"] for d in devices_left_on]

if device_list:
    for device in device_list:
        st.warning(f"⚠ {device} is still ON! Consider turning it OFF to save energy.")
else:
    st.success("✅ All devices are OFF. No energy wastage!")

