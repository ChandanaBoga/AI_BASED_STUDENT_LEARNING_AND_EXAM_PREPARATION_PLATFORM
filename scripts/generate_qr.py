import qrcode
import os

# Application URL (Local IP)
REPO_URL = "http://192.168.1.4:8001/"

# Output Path
OUTPUT_PATH = os.path.join("frontend", "assets", "app_qrcode.png")

def generate_qr():
    print(f"[*] Generating QR code for: {REPO_URL}")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(REPO_URL)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    img.save(OUTPUT_PATH)
    print(f"[+] QR code saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_qr()
