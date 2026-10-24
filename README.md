# QRShield

QR code authentication using digital signatures. A normal QR code is just text, so anyone can fake one. QRShield signs each code with an RSA private key, so a verifier with the public key can tell a genuine code from an edited or forged one.

## How it works

1. A token is built: `USER=...|TOKEN=...|ACCESS=AUTHORIZED`
2. The server signs it with RSA-2048, SHA-256 and PSS padding.
3. The token and signature are encoded in a QR code.
4. The public key verifies the signature. A match grants access. Any change to the data denies it.

The web interface includes a live **Tamper with it** button that edits the signed data and shows the verification failing.

## Run it

```bash
pip install flask qrcode pillow cryptography
python main.py
```

Open http://127.0.0.1:5000

## Project structure

```
main.py            Flask routes: /, /generate, /verify
crypto_utils.py    Key generation, signing, verification
templates/         index.html
static/            style.css, script.js
```

## Limitations

- A photographed QR still verifies (no expiry or replay protection yet).
- Keys are regenerated each time the app starts.
- The private key is stored unencrypted.

## Planned

Camera QR scanning, token expiry and replay protection, JSON payloads, persistent key storage.

## Tech

Python, Flask, `cryptography`, `qrcode`, HTML/CSS/JavaScript
