import pdfplumber
import pandas as pd
import requests

pdf_path = "/Users/lathamac/Downloads/SVVC Classes.pdf"

all_rows = []
header = None

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            for i, row in enumerate(table):
                clean_row = [cell.replace('\n', ' ') if isinstance(cell, str) else cell for cell in row]
                
                if not header and i == 0:
                    header = clean_row
                    continue
                elif header and i == 0 and clean_row[0] and "Class Name" in clean_row[0]:
                    continue
                
                if any(clean_row):
                    all_rows.append(clean_row)

df = pd.DataFrame(all_rows, columns=header)

# Rename columns to match API if they differ slightly
rename_map = {
    'Age': 'Player Age',
    'Account BalancChannel': 'Account Balance', # in case of OCR merging
}
df = df.rename(columns=rename_map)

# Ensure 'Channel' exists
if 'Channel' not in df.columns:
    df['Channel'] = ''

# The PDF structure has parent info only on the first row of a block.
# We need to forward-fill these so every attendance/payment row is associated with the correct player.
cols_to_ffill = ['Class Name', 'Class Ages', 'Player', 'Player Age', 'Skill', 'Gender', 'Parent Name', 'Channel', 'Class Cost', 'Account Balance']
for col in cols_to_ffill:
    if col in df.columns:
        df[col] = df[col].replace('', pd.NA)
        df[col] = df[col].ffill()

csv_path = "SVVC_Classes_Parsed.csv"
df.to_csv(csv_path, index=False)
print(f"Saved parsed data to {csv_path}")

from database import SessionLocal
import models
from routers.import_data import safe_int, safe_float, safe_str

try:
    for index, row in df.iterrows():
        db = SessionLocal()
        try:
            class_name = safe_str(row.get('Class Name'))
            class_ages = safe_str(row.get('Class Ages'))
            player_age = safe_int(row.get('Player Age'))
            skill = safe_str(row.get('Skill'))
            gender = safe_str(row.get('Gender'))
            parent_name = safe_str(row.get('Parent Name'))
            payment_amount = safe_float(row.get('Payment Amount'))
            class_attended = safe_int(row.get('Class Attended'))
            class_cost = safe_float(row.get('Class Cost'))
            account_balance = safe_float(row.get('Account Balance'))
            channel = safe_str(row.get('Channel'))

            if not parent_name:
                continue
                
            # 1. Class Creation
            db_class = None
            if class_name:
                db_class = db.query(models.ClassSchedule).filter(models.ClassSchedule.class_name == class_name).first()
                if not db_class:
                    db_class = models.ClassSchedule(
                        class_name=class_name,
                        target_ages=class_ages,
                        fee_per_class=class_cost
                    )
                    db.add(db_class)
                    db.commit()
                    db.refresh(db_class)

            # 2. Player/Parent Creation
            db_player = db.query(models.Player).filter(
                models.Player.parent_name == parent_name,
                models.Player.age == player_age
            ).first()

            if not db_player:
                db_player = models.Player(
                    parent_name=parent_name,
                    age=player_age,
                    current_balance=account_balance,
                    channel=channel
                )
                db.add(db_player)
                db.commit()
                db.refresh(db_player)
            else:
                db_player.current_balance = account_balance
                db.commit()

            # 3. Financials & Credits
            if class_cost > 0 and payment_amount > 0:
                purchased_credits = int(payment_amount // class_cost)
                db_player.available_credits = purchased_credits - class_attended
                db.commit()
        finally:
            db.close()

    print("Successfully populated the database from PDF.")
except Exception as e:
    print("Database insert failed:", e)
