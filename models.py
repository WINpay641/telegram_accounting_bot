import json
import os
from config import DB_PATH

DATA = {
    "income": [],
    "in_exchange": 1.0
}

def load_data():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            global DATA
            DATA = json.load(f)

def save_data():
    with open(DB_PATH, "w") as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)

def new_session():
    DATA["income"] = []
    save_data()

def add_income(amount):
    DATA["income"].append({"amount": amount})
    save_data()

def set_rate(key, value):
    DATA[key] = value
    save_data()

def show_bill():
    rate = DATA.get("in_exchange", 1.0)
    income = DATA.get("income", [])
    total = sum(x["amount"] for x in income)
    u_amount = total / rate if rate else 0

    lines = []
    lines.append(f"今日入款（{len(income)}笔）：")
    for x in income:
        u = x["amount"] / rate
        lines.append(f"- {x['amount']} → {u:.2f}U")
    lines.append(f"\n入款汇率：{rate:.3f}")
    lines.append(f"应下发：{total:.2f} → {u_amount:.2f}U")
    return "\n".join(lines)
