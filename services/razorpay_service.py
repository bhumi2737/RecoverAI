import os
import uuid
import razorpay
from dotenv import load_dotenv

load_dotenv()

class RazorpayService:
    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        self.demo_mode = str(os.getenv("DEMO_MODE", "True")).lower() in ["true", "1", "yes"]
        
        self.client = None
        if self.key_id and self.key_id != "your_razorpay_key_id" and not self.demo_mode:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            except Exception as e:
                print(f"Failed to initialize Razorpay client: {e}")

    def create_payment_link(self, amount_in_inr: float, customer_id: str, case_id: str) -> dict:
        """
        Creates a payment link. If in DEMO MODE or if credentials are not set,
        it simulates the creation of a payment link.
        """
        amount_in_paise = int(amount_in_inr * 100)
        
        if self.demo_mode or not self.client:
            # Simulate Payment Link Creation
            return {
                "id": f"plink_demo_{uuid.uuid4().hex[:8]}",
                "short_url": f"https://rzp.io/i/demo_{uuid.uuid4().hex[:6]}",
                "status": "created",
                "amount": amount_in_paise,
                "is_demo": True
            }

        try:
            # Create actual Test Mode Payment Link
            payment_link_data = {
                "amount": amount_in_paise,
                "currency": "INR",
                "accept_partial": False,
                "description": f"Payment Recovery for Case {case_id}",
                "customer": {
                    "name": f"Customer {customer_id}",
                    "email": f"{customer_id}@example.com",
                    "contact": "+919999999999" # Dummy phone for test mode
                },
                "notify": {
                    "sms": False,
                    "email": False
                },
                "reminder_enable": False,
                "notes": {
                    "case_id": case_id,
                    "customer_id": customer_id
                }
            }
            
            link = self.client.payment_link.create(payment_link_data)
            link['is_demo'] = False
            return link
            
        except Exception as e:
            print(f"Razorpay API Error: {e}")
            raise Exception(f"Failed to create Payment Link: {str(e)}")

    def check_payment_status(self, payment_link_id: str) -> str:
        """
        Checks the status of a payment link.
        Returns 'paid', 'created', 'expired', 'cancelled'
        """
        if self.demo_mode or not self.client or "demo" in payment_link_id:
            # In demo mode, we just return 'created' for simplicity,
            # or we could randomly simulate a success if needed, but 'created' is safe.
            return "created"
            
        try:
            link = self.client.payment_link.fetch(payment_link_id)
            return link.get('status', 'unknown')
        except Exception as e:
            print(f"Razorpay API Error checking status: {e}")
            return "error"
