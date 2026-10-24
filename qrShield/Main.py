from flask import Flask, render_template, request, jsonify
import qrcode
import base64
import io
import uuid

from crypto_utils import (
    generate_keys,
    sign_data,
    verify_signature,
    PRIVATE_KEY_FILE,
    PUBLIC_KEY_FILE
)


app = Flask(__name__)


# ---------------------------------------------------------
# Generate RSA keys when application starts
# ---------------------------------------------------------

generate_keys()


# ---------------------------------------------------------
# Generate authentication token
# ---------------------------------------------------------

def create_token(user):

    token_id = "QRSHIELD-" + uuid.uuid4().hex[:8].upper()

    authentication_data = (
        f"USER={user}|"
        f"TOKEN={token_id}|"
        f"ACCESS=AUTHORIZED"
    )

    signature = sign_data(authentication_data)

    signature_text = base64.b64encode(
        signature
    ).decode("utf-8")

    qr_content = (
        f"{authentication_data}|"
        f"SIGNATURE={signature_text}"
    )

    return {
        "user": user,
        "token": token_id,
        "algorithm": "RSA-2048 / SHA-256",
        "data": authentication_data,
        "signature": signature_text,
        "qr_content": qr_content
    }


# ---------------------------------------------------------
# Generate QR image
# ---------------------------------------------------------

def generate_qr_image(data):

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ---------------------------------------------------------
# Generate QR endpoint
# ---------------------------------------------------------

@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json()

    user = data.get(
        "user",
        "Authorized User"
    )

    token = create_token(user)

    qr_image = generate_qr_image(
        token["qr_content"]
    )

    token["qr_image"] = qr_image

    return jsonify(token)


# ---------------------------------------------------------
# Verify signature
# ---------------------------------------------------------

@app.route("/verify", methods=["POST"])
def verify():

    data = request.get_json()

    authentication_data = data.get(
        "authentication_data"
    )

    signature_text = data.get(
        "signature"
    )

    try:

        signature = base64.b64decode(
            signature_text
        )

        valid = verify_signature(
            authentication_data,
            signature
        )

        if valid:

            return jsonify({
                "valid": True,
                "message": "Digital signature verified. Access granted."
            })

        else:

            return jsonify({
                "valid": False,
                "message": "Digital signature invalid. Access denied."
            })

    except Exception:

        return jsonify({
            "valid": False,
            "message": "Verification failed. Access denied."
        })


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )
#host: http://127.0.0.1:5000/