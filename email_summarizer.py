import imaplib
import email
from email import policy
from openai import OpenAI
import os


# Function to get email summaries using yield
def fetch_emails_generator(user, password, number_of_emails=25):
    imap_url = "imap.gmail.com"

    try:
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(user, password)
        mail.select("inbox")

        # Fetch all email IDs in the inbox
        _, data = mail.search(None, "ALL")
        mail_ids = data[0].split()

        # Fetch the last 'n' email IDs
        latest_email_ids = mail_ids[-number_of_emails:]

        # Loop through the latest email IDs
        for num in latest_email_ids:
            _, data = mail.fetch(num, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(
                        response_part[1], policy=policy.default
                    )

                    # Extract important information
                    sender = msg["from"]
                    date = msg["date"]
                    subject = msg["subject"]

                    message_body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                message_body += part.get_payload(decode=True).decode(
                                    part.get_content_charset() or "utf-8"
                                )
                    else:
                        if msg.get_content_type() == "text/plain":
                            message_body = msg.get_payload(decode=True).decode(
                                msg.get_content_charset() or "utf-8"
                            )

                    # Email summarization using OpenAI
                    email_content = message_body
                    system_prompt = """The task is to summarize the email in a concise manner while capturing all details, no matter how small.
                    The summary should categorize the type of email (advertisement, social media notification, or site notification).
                    If it is a social media notification, specify the platform (e.g., Facebook, LinkedIn).
                    If it is a site notification, mention the site from which it originates.
                    Explain the purpose or motive behind the email and include any additional relevant information.
                    Ensure the summary is complete yet succinct, covering all key points without omission."""

                    prompt = email_content + system_prompt
                    client = OpenAI(api_key=os.getenv("OPENAI-API-KEY"))
                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        temperature=0.5,
                        messages=[{"role": "user", "content": prompt}],
                    )

                    summary = completion.choices[0].message.content

                    # Yield email data one at a time
                    yield {
                        "from": sender,
                        "date": date,
                        "subject": subject,
                        "summary": summary,
                    }

    except Exception as e:
        yield {"summary": str(e)}
