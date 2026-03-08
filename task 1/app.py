from flask import Flask, render_template, request
import requests
import re

app = Flask(__name__)

def extract_emails(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)

        html = response.text

        # Email regex
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+"

        emails = re.findall(pattern, html)

        emails = list(set(emails))  # remove duplicates

        if len(emails) == 0:
            emails.append("No emails found")

        return emails

    except:
        return ["Error fetching website"]


@app.route("/", methods=["GET", "POST"])
def home():

    emails = []

    if request.method == "POST":
        url = request.form["url"]
        emails = extract_emails(url)

    return render_template("index.html", emails=emails)


if __name__ == "__main__":
    app.run(debug=True)