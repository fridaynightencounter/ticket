"""
Friday Night Encounter — Bulk Ticket Generator
================================================
Usage:
  1. Place this script in the same folder as your CSV and the header image
  2. Run: python3 generate_tickets.py
  3. All tickets will be saved to ./tickets/ folder
  4. Upload the ./tickets/ folder to your GitHub repo

Requirements:
  pip3 install pillow qrcode
"""

import os
import csv
import qrcode
from PIL import Image, ImageDraw, ImageFont

# ── CONFIG ─────────────────────────────────────────────────────────────────────
CSV_FILE        = "tickets.csv"
HEADER_IMAGE    = "EC26_Eventbrite_Header_Fri-Night_2.png"
OUTPUT_DIR      = "tickets"

# Column positions (0-indexed) — no header row, comma separated
COL_FIRSTNAME   = 0
COL_BARCODE     = 1
COL_PHONE       = 2

# ── DESIGN ─────────────────────────────────────────────────────────────────────
CARD_W      = 1080
QR_SIZE     = 320
PADDING     = 60
BG_COLOR    = "#111111"
ACCENT      = "#E06030"

# ── FONTS ──────────────────────────────────────────────────────────────────────
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except:
            return ImageFont.load_default()

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

font_medium = load_font(FONT_BOLD, 32)
font_small  = load_font(FONT_REG,  24)
font_tiny   = load_font(FONT_REG,  20)

# ── LOAD HEADER ONCE ───────────────────────────────────────────────────────────
header_src = Image.open(HEADER_IMAGE).convert("RGBA")
h_ratio    = CARD_W / header_src.width
header_h   = int(header_src.height * h_ratio)
header_img = header_src.resize((CARD_W, header_h), Image.LANCZOS)

# Pre-calculate card height
top_text_h    = 80
qr_section_h  = QR_SIZE + PADDING * 2
bottom_text_h = 110
CARD_H = header_h + top_text_h + qr_section_h + bottom_text_h

# ── TICKET GENERATOR ───────────────────────────────────────────────────────────
def generate_ticket(barcode_str, output_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2
    )
    qr.add_data(barcode_str)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_img = qr_img.resize((QR_SIZE, QR_SIZE), Image.LANCZOS)

    canvas = Image.new("RGBA", (CARD_W, CARD_H), BG_COLOR)
    draw   = ImageDraw.Draw(canvas)

    canvas.paste(header_img, (0, 0), header_img)

    y = header_h
    draw.rectangle([(0, y), (CARD_W, y + 3)], fill=ACCENT)

    y += 18
    draw.text((CARD_W // 2, y + 10), "YOUR TICKET", font=font_medium,
              fill="#FFFFFF", anchor="mt")

    y += top_text_h
    qr_x = (CARD_W - QR_SIZE) // 2
    canvas.paste(qr_img, (qr_x, y + PADDING // 2), qr_img)

    y_barcode = y + PADDING // 2 + QR_SIZE + 12
    draw.text((CARD_W // 2, y_barcode), barcode_str, font=font_tiny,
              fill="#AAAAAA", anchor="mt")

    y_footer = y_barcode + 36
    draw.text((CARD_W // 2, y_footer), "See you there 🙌", font=font_medium,
              fill="#FFFFFF", anchor="mt")

    draw.text((CARD_W // 2, y_footer + 48), "crclondon.com", font=font_small,
              fill="#666666", anchor="mt")

    canvas.convert("RGB").save(output_path, "JPEG", quality=92)


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    wassenger_rows = []

    with open(CSV_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=",")
        rows = [
            {"firstname": r[COL_FIRSTNAME], "barcode": r[COL_BARCODE], "phone": r[COL_PHONE]}
            for r in reader
            if len(r) >= 3 and r[COL_BARCODE].strip() != ""
        ]

    total = len(rows)
    print(f"Found {total} rows in CSV\n")

    skipped = 0
    generated = 0

    for i, row in enumerate(rows, 1):
        barcode   = row["barcode"].strip()
        phone     = row["phone"].strip()
        firstname = row["firstname"].strip().split()[0]

        filename    = f"{barcode}.jpg"
        output_path = os.path.join(OUTPUT_DIR, filename)

        # Skip if image already exists
        if os.path.exists(output_path):
            skipped += 1
        else:
            generate_ticket(barcode, output_path)
            generated += 1

        # GitHub Pages URL
        ticket_url = f"https://fridaynightencounter.github.io/ticket/tickets/{filename}"

        wassenger_rows.append({
            "phone": phone,
            "name": firstname,
            "ticket_link": ticket_url
        })

        if i % 100 == 0 or i == total:
            print(f"  [{i}/{total}] — generated: {generated}, skipped: {skipped}")

    # Write Wassenger-ready CSV
    wassenger_csv = "wassenger_import.csv"
    with open(wassenger_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["phone", "name", "ticket_link"])
        writer.writeheader()
        writer.writerows(wassenger_rows)

    print(f"\n✅ All done!")
    print(f"   Generated: {generated} new tickets")
    print(f"   Skipped:   {skipped} existing tickets")
    print(f"   Tickets folder    → ./{OUTPUT_DIR}/")
    print(f"   Wassenger CSV     → ./{wassenger_csv}")


if __name__ == "__main__":
    main()