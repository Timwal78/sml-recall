import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template, abort, redirect
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from tools.keygen import generate_key
except ImportError:
    import random, string
    def generate_key(prefix):
        seg = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}-{seg()}-{seg()}-{seg()}-{seg()}"

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='../docs')

TIERS = {
    'recall-core': 'CORE',
    'recall-beastmode': 'BEAST',
    'recall-bundle': 'BNDL',
    'core': 'CORE',
    'beastmode': 'BEAST',
    'bundle': 'BNDL'
}

KEYS_POOL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'keys_pool.json')

def pop_key(prefix):
    """Pop a pre-generated key from the pool. Falls back to generating one."""
    try:
        with open(KEYS_POOL_PATH, 'r') as f:
            pool = json.load(f)
        keys = pool.get(prefix, [])
        if keys:
            key = keys.pop(0)
            with open(KEYS_POOL_PATH, 'w') as f:
                json.dump(pool, f, indent=2)
            remaining = {t: len(v) for t, v in pool.items()}
            print(f"🔑 Pool remaining: {remaining}")
            return key
    except Exception as e:
        print(f"⚠️  Key pool error: {e} — generating fresh key")
    return generate_key(prefix)

def send_key_email(to_email, key, tier_name):
    """Send the license key to the customer via Gmail SMTP."""
    sender = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')

    if not sender or not password:
        print(f"⚠️  EMAIL_USER/EMAIL_PASS not set. Key for {to_email}: {key}")
        return False

    subject = f"Your SML-RECALL {tier_name} License Key"
    body = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SML-RECALL — License Key Delivery
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your {tier_name} key:

  {key}

SETUP:
1. Clone the repo: github.com/Timwal78/sml-recall
2. Copy config.yaml.example → config.yaml
3. Add your key and Anthropic API key to config.yaml
4. Run: pip install -r requirements.txt

Questions? Check the README — everything is documented.

Built by a disabled veteran. Thank you for the support.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, to_email, msg.as_string())
        print(f"✅ Key emailed to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed for {to_email}: {e}")
        return False

@app.route('/')
def index():
    return render_template('recall-landing.html')

@app.route('/checkout/<tier>')
def redirect_checkout(tier):
    gumroad_urls = {
        'core': 'https://timwalton.gumroad.com/l/qdfqci',
        'beastmode': 'https://timwalton.gumroad.com/l/xtmgww',
        'bundle': 'https://timwalton.gumroad.com/l/danyb'
    }
    tier_lower = tier.lower()
    if tier_lower in gumroad_urls:
        return redirect(gumroad_urls[tier_lower], code=302)
    return abort(404)

@app.route('/webhook/gumroad', methods=['POST'])
def gumroad_webhook():
    data = request.form or request.json
    if not data:
        return "No payload", 400

    if data.get('test') == 'true':
        return "Ping successful", 200

    permalink = data.get('permalink', '')
    email = data.get('email', '')

    if not email:
        return "Missing email", 400

    prefix = TIERS.get(permalink)
    if not prefix:
        prod_name = data.get('product_name', '').lower()
        if 'bundle' in prod_name:    prefix = 'BNDL'
        elif 'beastmode' in prod_name: prefix = 'BEAST'
        elif 'core' in prod_name:    prefix = 'CORE'
        else:                         prefix = 'CORE'

    tier_names = {'CORE': 'Core', 'BEAST': 'Beastmode', 'BNDL': 'Bundle'}
    new_key = pop_key(prefix)
    tier_name = tier_names.get(prefix, prefix)

    print(f"✅ Purchase: {email} | {tier_name} | Key: {new_key}")
    send_key_email(email, new_key, tier_name)

    return "OK", 200

@app.route('/pay', methods=['POST'])
@app.route('/api/rails/issue-key', methods=['POST'])
def xrpl_payment():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON payload"}), 400

    expected_secret = os.environ.get('RAILS_SHARED_SECRET', 'changeme_12345')
    if data.get('secret') != expected_secret:
        return jsonify({"error": "Unauthorized"}), 401

    tier = data.get('tier', '').lower()
    prefix = TIERS.get(tier, 'CORE')
    new_key = pop_key(prefix)

    email = data.get('email')
    if email:
        tier_names = {'CORE': 'Core', 'BEAST': 'Beastmode', 'BNDL': 'Bundle'}
        send_key_email(email, new_key, tier_names.get(prefix, prefix))

    print(f"✅ XRPL Payment — issued {prefix} key: {new_key}")
    return jsonify({"status": "success", "tier": tier, "key": new_key})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
