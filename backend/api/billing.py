"""
Stripe billing integration for subscription management
"""
from flask import Blueprint, request, jsonify, g
import os
import stripe
from datetime import datetime

billing_bp = Blueprint('billing', __name__)

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'user_limit': 5,
        'api_rate_limit': 1000,
        'features': ['basic_guidance', 'meditation']
    },
    'basic': {
        'name': 'Basic',
        'price': 29,
        'stripe_price_id': os.environ.get('STRIPE_BASIC_PRICE_ID', 'price_basic'),
        'user_limit': 25,
        'api_rate_limit': 10000,
        'features': ['basic_guidance', 'meditation', 'analytics', 'api_access']
    },
    'pro': {
        'name': 'Professional',
        'price': 99,
        'stripe_price_id': os.environ.get('STRIPE_PRO_PRICE_ID', 'price_pro'),
        'user_limit': 100,
        'api_rate_limit': 50000,
        'features': ['basic_guidance', 'meditation', 'analytics', 'api_access', 'custom_branding', 'priority_support']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 299,
        'stripe_price_id': os.environ.get('STRIPE_ENTERPRISE_PRICE_ID', 'price_enterprise'),
        'user_limit': 1000,
        'api_rate_limit': 200000,
        'features': ['all_features', 'white_label', 'sso', 'dedicated_support', 'custom_domain']
    }
}

@billing_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Get available subscription plans"""
    return jsonify({'plans': SUBSCRIPTION_PLANS})

@billing_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session for subscription"""
    data = request.json
    
    try:
        from api.enterprise import require_tenant, require_auth
        
        # Get tenant and plan details
        tenant_id = data.get('tenant_id')
        plan_id = data.get('plan_id')
        
        if plan_id not in SUBSCRIPTION_PLANS:
            return jsonify({'error': 'Invalid plan'}), 400
            
        plan = SUBSCRIPTION_PLANS[plan_id]
        
        if plan_id == 'free':
            return jsonify({'error': 'Free plan does not require checkout'}), 400
        
        # Create or get Stripe customer
        from models.enterprise import Tenant
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        
        if not tenant.stripe_customer_id:
            customer = stripe.Customer.create(
                email=data.get('email'),
                name=tenant.name,
                metadata={'tenant_id': tenant_id}
            )
            tenant.stripe_customer_id = customer.id
            from models.enterprise import db
            db.session.commit()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=tenant.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': plan['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=data.get('success_url', 'https://your-domain.com/success'),
            cancel_url=data.get('cancel_url', 'https://your-domain.com/cancel'),
            metadata={
                'tenant_id': tenant_id,
                'plan_id': plan_id
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/portal', methods=['POST'])
def create_customer_portal():
    """Create Stripe customer portal session"""
    data = request.json
    
    try:
        from models.enterprise import Tenant
        
        tenant_id = data.get('tenant_id')
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        
        if not tenant or not tenant.stripe_customer_id:
            return jsonify({'error': 'No active subscription found'}), 404
        
        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=tenant.stripe_customer_id,
            return_url=data.get('return_url', 'https://your-domain.com/dashboard')
        )
        
        return jsonify({
            'portal_url': portal_session.url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_payment_failed(event['data']['object'])
    
    return jsonify({'status': 'success'})

def handle_subscription_created(subscription):
    """Handle new subscription creation"""
    try:
        from models.enterprise import Tenant, Subscription, db
        
        # Get tenant from customer metadata
        customer = stripe.Customer.retrieve(subscription['customer'])
        tenant_id = customer.metadata.get('tenant_id')
        
        if not tenant_id:
            print(f"No tenant_id found in customer metadata for {subscription['customer']}")
            return
        
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        if not tenant:
            print(f"Tenant not found: {tenant_id}")
            return
        
        # Determine plan from price_id
        price_id = subscription['items']['data'][0]['price']['id']
        plan_id = None
        for plan, details in SUBSCRIPTION_PLANS.items():
            if details.get('stripe_price_id') == price_id:
                plan_id = plan
                break
        
        if not plan_id:
            print(f"Unknown price_id: {price_id}")
            return
        
        # Update tenant subscription
        tenant.subscription_tier = plan_id
        tenant.subscription_status = subscription['status']
        tenant.user_limit = SUBSCRIPTION_PLANS[plan_id]['user_limit']
        tenant.api_rate_limit = SUBSCRIPTION_PLANS[plan_id]['api_rate_limit']
        
        # Create subscription record
        sub_record = Subscription(
            tenant_id=tenant_id,
            stripe_subscription_id=subscription['id'],
            stripe_customer_id=subscription['customer'],
            stripe_price_id=price_id,
            status=subscription['status'],
            current_period_start=datetime.fromtimestamp(subscription['current_period_start']),
            current_period_end=datetime.fromtimestamp(subscription['current_period_end'])
        )
        
        db.session.add(sub_record)
        db.session.commit()
        
        # Log the event
        from api.enterprise import log_audit_event
        log_audit_event('subscription_created', tenant_id, {
            'plan_id': plan_id,
            'stripe_subscription_id': subscription['id']
        })
        
    except Exception as e:
        print(f"Error handling subscription created: {e}")

def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    try:
        from models.enterprise import Subscription, Tenant, db
        
        sub_record = Subscription.query.filter_by(
            stripe_subscription_id=subscription['id']
        ).first()
        
        if not sub_record:
            print(f"Subscription record not found: {subscription['id']}")
            return
        
        # Update subscription
        sub_record.status = subscription['status']
        sub_record.current_period_start = datetime.fromtimestamp(subscription['current_period_start'])
        sub_record.current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
        
        # Update tenant status
        tenant = Tenant.query.filter_by(id=sub_record.tenant_id).first()
        if tenant:
            tenant.subscription_status = subscription['status']
        
        db.session.commit()
        
        # Log the event
        from api.enterprise import log_audit_event
        log_audit_event('subscription_updated', sub_record.tenant_id, {
            'stripe_subscription_id': subscription['id'],
            'status': subscription['status']
        })
        
    except Exception as e:
        print(f"Error handling subscription updated: {e}")

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        from models.enterprise import Subscription, Tenant, db
        
        sub_record = Subscription.query.filter_by(
            stripe_subscription_id=subscription['id']
        ).first()
        
        if not sub_record:
            return
        
        # Update tenant to free plan
        tenant = Tenant.query.filter_by(id=sub_record.tenant_id).first()
        if tenant:
            tenant.subscription_tier = 'free'
            tenant.subscription_status = 'canceled'
            tenant.user_limit = SUBSCRIPTION_PLANS['free']['user_limit']
            tenant.api_rate_limit = SUBSCRIPTION_PLANS['free']['api_rate_limit']
        
        # Update subscription record
        sub_record.status = 'canceled'
        
        db.session.commit()
        
        # Log the event
        from api.enterprise import log_audit_event
        log_audit_event('subscription_canceled', sub_record.tenant_id, {
            'stripe_subscription_id': subscription['id']
        })
        
    except Exception as e:
        print(f"Error handling subscription deleted: {e}")

def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    try:
        from api.enterprise import log_audit_event
        
        # Get subscription
        subscription_id = invoice.get('subscription')
        if subscription_id:
            from models.enterprise import Subscription
            sub_record = Subscription.query.filter_by(
                stripe_subscription_id=subscription_id
            ).first()
            
            if sub_record:
                log_audit_event('payment_succeeded', sub_record.tenant_id, {
                    'amount': invoice.get('amount_paid'),
                    'invoice_id': invoice.get('id')
                })
        
    except Exception as e:
        print(f"Error handling payment succeeded: {e}")

def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        from api.enterprise import log_audit_event
        
        # Get subscription
        subscription_id = invoice.get('subscription')
        if subscription_id:
            from models.enterprise import Subscription
            sub_record = Subscription.query.filter_by(
                stripe_subscription_id=subscription_id
            ).first()
            
            if sub_record:
                log_audit_event('payment_failed', sub_record.tenant_id, {
                    'amount': invoice.get('amount_due'),
                    'invoice_id': invoice.get('id'),
                    'error': 'Payment failed'
                })
        
    except Exception as e:
        print(f"Error handling payment failed: {e}")

@billing_bp.route('/subscription', methods=['GET'])
def get_subscription():
    """Get current subscription details"""
    try:
        tenant_id = request.args.get('tenant_id')
        
        from models.enterprise import Tenant, Subscription
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        subscription = None
        if tenant.subscription_tier != 'free':
            subscription = Subscription.query.filter_by(tenant_id=tenant_id).first()
        
        return jsonify({
            'tenant_id': tenant.id,
            'current_plan': tenant.subscription_tier,
            'status': tenant.subscription_status,
            'user_limit': tenant.user_limit,
            'api_rate_limit': tenant.api_rate_limit,
            'features': SUBSCRIPTION_PLANS[tenant.subscription_tier]['features'],
            'subscription': {
                'id': subscription.id if subscription else None,
                'current_period_end': subscription.current_period_end.isoformat() if subscription else None,
                'stripe_subscription_id': subscription.stripe_subscription_id if subscription else None
            } if subscription else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500