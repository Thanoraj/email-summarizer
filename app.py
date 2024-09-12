import streamlit as st
from email_summarizer import fetch_emails_generator

# Streamlit UI
st.title("Email Summarizer")

# Input form for credentials and number of emails
with st.form("email_credentials"):
    user = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input(
        "Password", placeholder="Enter your password", type="password"
    )
    number_of_emails = st.selectbox(
        "Number of emails to fetch", [5, 10, 15, 20, 25, 30]
    )

    submit_button = st.form_submit_button(label="Fetch and Summarize Emails")

# If the user submitted the form
if submit_button:
    if user and password:
        st.write(f"Fetching and summarizing {number_of_emails} emails...")

        # Call the generator function
        email_generator = fetch_emails_generator(user, password, number_of_emails)

        # Create a placeholder to append each email summary
        for mail in email_generator:
            # Display the emails one after the other without clearing previous ones
            with st.container():
                st.subheader(f"From: {mail['from']}")
                st.write(f"Date: {mail['date']}")
                st.write(f"Subject: {mail['subject']}")
                st.write(f"**Summary**: {mail['summary']}")
                st.write("---")
    else:
        st.error("Please provide both email and password.")
