from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import os

app = Flask(__name__)
DATA_FILE = "data.json"
team_members = []

def calculate_renewal_dates(start_date_str):
    try:
        start = datetime.strptime(start_date_str, "%Y-%m-%d")
    except ValueError:
        return []
    return [(start + relativedelta(months=6 * i)).strftime("%Y-%m-%d") for i in range(1, 5)]

def load_data():
    global team_members
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                for member in raw_data:
                    join_date = member.get("join_date")
                    if join_date:
                        member["renewals"] = calculate_renewal_dates(join_date)
                    else:
                        member["renewals"] = []
                team_members = raw_data
        except (json.JSONDecodeError, KeyError):
            team_members = []
    else:
        team_members = []

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(team_members, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    global team_members
    edit_index = None
    edited_member = {}

    if request.method == "POST":
        if "add" in request.form:
            name = request.form.get("name", "").strip()
            experience = request.form.get("experience", "").strip()
            join_date = request.form.get("join_date", "").strip()
            contact = request.form.get("contact", "").strip()
            if name and experience.isdigit() and join_date:
                renewals = calculate_renewal_dates(join_date)
                team_members.append({
                    "name": name,
                    "experience": experience,
                    "join_date": join_date,
                    "contact": contact,
                    "renewals": renewals
                })
                save_data()

        elif "delete" in request.form:
            idx_str = request.form.get("delete")
            if idx_str and idx_str.isdigit():
                idx = int(idx_str)
                if 0 <= idx < len(team_members):
                    team_members.pop(idx)
                    save_data()

        elif "edit" in request.form:
            idx_str = request.form.get("edit")
            if idx_str and idx_str.isdigit():
                idx = int(idx_str)
                if 0 <= idx < len(team_members):
                    edit_index = idx
                    edited_member = team_members[idx]

        elif "save_edit" in request.form:
            idx_str = request.form.get("save_edit")
            if idx_str and idx_str.isdigit():
                idx = int(idx_str)
                if 0 <= idx < len(team_members):
                    name = request.form.get("name", "").strip()
                    experience = request.form.get("experience", "").strip()
                    join_date = request.form.get("join_date", "").strip()
                    contact = request.form.get("contact", "").strip()
                    if name and experience.isdigit() and join_date:
                        team_members[idx]["name"] = name
                        team_members[idx]["experience"] = experience
                        team_members[idx]["join_date"] = join_date
                        team_members[idx]["contact"] = contact
                        team_members[idx]["renewals"] = calculate_renewal_dates(join_date)
                        save_data()
                        return redirect(url_for("index"))

    sorted_members = sorted(
        enumerate(team_members),
        key=lambda pair: int(pair[1]["experience"]),
        reverse=True
    )

    return render_template(
        "index.html",
        members=sorted_members,
        edit_index=edit_index,
        edited_member=edited_member,
        today=datetime.today().strftime("%Y-%m-%d")
    )

if __name__ == "__main__":
    load_data()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
