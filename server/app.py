import os
import sys
import stripe
from flask import Flask, request, redirect, render_template, url_for, jsonify, abort
from dotenv import load_dotenv
from models import db, Payment
from datetime import datetime, timezone

# Add parent directory to path to import keygen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from tools.keygen import generate_key
except ImportError:
    # Fallback if running standalone
    import random
    import string
    def generate_key_segment():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    def generate_key(prefix):
        return f"{prefix}-{generate_key_segment()}-{generate_key_segment()}-{generate_key_segment()}-{generate_key_segment()}"

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///recall_payments.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

TIERS = {
    'core': {
        'name': 'SML-RECALL Core Tier',
        'price': 2700, # $27.00
        'prefix': 'CORE'
    },
    'beastmode': {
        'name': 'SML-RECALL Beastmode Tier',
        'price': 6700, # $67.00
        'prefix': 'BEAST'
    },
    'bundle': {
        'name': 'SML-RECALL Bundle Tier',
        'price': 9700, # $97.00
        'prefix': 'BNDL'
    }
}

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('recall-landing.html')

@app.route('/checkout/<tier>')
def create_checkout_session(tier):
    tier = tier.lower()
    if tier not in TIERS:
        abort(404, description="Tier not found")
        
    if not stripe.api_key:
        return "Stripe API Key not configured.", 500

    tier_data = TIERS[tier]
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': tier_data['name'],
                    },
                    'unit_amount': tier_data['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.url_root + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.url_root + 'cancel',
            metadata={'tier': tier}
        )
        
        # Track pending payment
        payment = Payment(session_id=session.id, tier=tier, status='pending')
        db.session.add(payment)
        db.session.commit()
        
        return redirect(session.url, code=303)
    except Exception as e:
        return str(e), 500

@app.route('/success')
def success():
    session_id = request.args.get('session_id')
    if not session_id:
        return "Invalid session", 400
        
    payment = Payment.query.filter_by(session_id=session_id).first()
    if not payment:
        return "Payment tracking record not found", 404
        
    if payment.status == 'fulfilled':
        # Already fulfilled, just show them their key again
        return render_template('success.html', key=payment.generated_key, tier=payment.tier.upper())
        
    # Verify with Stripe
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            # Generate key
            prefix = TIERS[payment.tier]['prefix']
            new_key = generate_key(prefix)
            
            # Update DB
            payment.status = 'fulfilled'
            payment.generated_key = new_key
            payment.fulfilled_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return render_template('success.html', key=new_key, tier=payment.tier.upper())
        else:
            return "Payment not completed.", 400
    except Exception as e:
        return str(e), 500

@app.route('/cancel')
def cancel():
    return "Checkout canceled. You can close this window."

@app.route('/api/rails/issue-key', methods=['POST'])
def rails_issue_key():
    """
    Webhook for SML Rails (XRPL crypto payments).
    Expects JSON: { "secret": "...", "tier": "beastmode" }
    """
    data = request.json
    if not data:
        return jsonify({"error": "No JSON payload"}), 400
        
    # Simple shared secret authentication
    expected_secret = os.environ.get('RAILS_SHARED_SECRET')
    if not expected_secret or data.get('secret') != expected_secret:
        return jsonify({"error": "Unauthorized"}), 401
        
    tier = data.get('tier', '').lower()
    if tier not in TIERS:
        return jsonify({"error": "Invalid tier"}), 400
        
    prefix = TIERS[tier]['prefix']
    new_key = generate_key(prefix)
    
    # We could log this to the DB as well, but for now just return it
    return jsonify({
        "status": "success",
        "tier": tier,
        "key": new_key
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
