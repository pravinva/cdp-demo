"""
Generate realistic demo data for CDP platform
Creates customers, events, campaigns, decisions for testing
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime, timedelta
import random
import uuid

def generate_demo_data(spark, tenant_id="demo_tenant", num_customers=100):
    """Generate realistic demo data"""
    
    print(f"Generating demo data for tenant: {tenant_id}")
    
    # 1. Generate Customers
    print("Generating customers...")
    
    segments = ["VIP", "Active", "AtRisk", "Dormant"]
    channels = ["email", "sms", "push"]
    
    customers_data = []
    for i in range(num_customers):
        customer_id = f"cust_{uuid.uuid4().hex[:8]}"
        segment = random.choices(segments, weights=[10, 40, 30, 20])[0]
        
        # Segment-based attributes
        if segment == "VIP":
            ltv = random.randint(5000, 20000)
            purchases = random.randint(20, 100)
            churn_risk = random.uniform(0.1, 0.3)
        elif segment == "Active":
            ltv = random.randint(500, 5000)
            purchases = random.randint(5, 20)
            churn_risk = random.uniform(0.2, 0.4)
        elif segment == "AtRisk":
            ltv = random.randint(300, 2000)
            purchases = random.randint(2, 10)
            churn_risk = random.uniform(0.6, 0.8)
        else:  # Dormant
            ltv = random.randint(100, 500)
            purchases = random.randint(1, 3)
            churn_risk = random.uniform(0.8, 0.95)
        
        customers_data.append({
            "customer_id": customer_id,
            "tenant_id": tenant_id,
            "email": f"customer{i}@example.com",
            "phone": f"+1555{i:07d}",
            "first_name": f"Customer{i}",
            "last_name": f"Demo{i}",
            "segment": segment,
            "lifetime_value": float(ltv),
            "total_purchases": purchases,
            "avg_order_value": float(ltv / purchases if purchases > 0 else 0),
            "days_since_purchase": random.randint(1, 180) if segment != "Dormant" else random.randint(60, 365),
            "churn_risk_score": float(churn_risk),
            "purchase_propensity_score": float(random.uniform(0.3, 0.9)),
            "email_engagement_score": float(random.uniform(0.4, 0.9)),
            "preferred_channel": random.choice(channels),
            "email_consent": True,
            "sms_consent": random.choice([True, False]),
            "push_consent": random.choice([True, False]),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
    
    customers_df = spark.createDataFrame(customers_data)
    customers_df.write.format("delta").mode("overwrite").saveAsTable("cdp_platform.core.customers")
    print(f"✓ Created {num_customers} customers")
    
    # 2. Generate Clickstream Events
    print("Generating clickstream events...")
    
    event_types = ["page_view", "product_view", "cart_add", "cart_remove", "purchase", "search"]
    events_data = []
    
    for customer in customers_data:
        # Generate 5-50 events per customer
        num_events = random.randint(5, 50)
        
        for j in range(num_events):
            event_id = f"evt_{uuid.uuid4().hex}"
            event_timestamp = datetime.now() - timedelta(days=random.randint(0, 90))
            
            # Some events are anonymous (no login_id)
            is_anonymous = j < num_events * 0.3  # 30% anonymous
            
            events_data.append({
                "event_id": event_id,
                "tenant_id": tenant_id,
                "login_id": None if is_anonymous else customer["customer_id"],
                "email": None if is_anonymous else customer["email"],
                "cookie_id": f"cookie_{customer['customer_id']}",
                "session_id": f"session_{uuid.uuid4().hex[:8]}",
                "event_type": random.choice(event_types),
                "event_timestamp": event_timestamp,
                "page_url": f"/products/{random.randint(1, 100)}",
                "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "device_family": random.choice(["Desktop", "Mobile", "Tablet"]),
                "ingested_at": datetime.now()
            })
    
    if events_data:
        events_df = spark.createDataFrame(events_data)
        events_df.write.format("delta").mode("overwrite").saveAsTable("cdp_platform.core.clickstream_events")
        print(f"✓ Created {len(events_data)} events")
    
    # 3. Generate Sample Campaign
    print("Generating sample campaign...")
    
    campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
    campaign_data = [{
        "campaign_id": campaign_id,
        "tenant_id": tenant_id,
        "name": "Q4 Retention Campaign",
        "description": "Re-engage at-risk customers",
        "goal": "retention",
        "status": "active",
        "agent_mode": True,
        "agent_instructions": "Focus on personalized offers based on past purchases",
        "channels": ["email", "sms"],
        "start_date": datetime.now(),
        "created_by": "system",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }]
    
    campaign_df = spark.createDataFrame(campaign_data)
    campaign_df.write.format("delta").mode("append").saveAsTable("cdp_platform.core.campaigns")
    print("✓ Created sample campaign")
    
    # 4. Generate Sample Agent Decisions
    print("Generating agent decisions...")
    
    decisions_data = []
    for customer in customers_data[:20]:  # First 20 customers
        decision_id = f"dec_{uuid.uuid4().hex}"
        
        # Agent decides based on segment
        if customer["segment"] == "AtRisk":
            action = "contact"
            channel = "email"
            subject = f"We miss you, {customer['first_name']}! Here's 20% off"
            body = f"Hi {customer['first_name']}, we noticed you haven't shopped recently..."
            reasoning = "Customer shows high churn risk but good historical engagement"
        else:
            action = "skip"
            channel = None
            subject = None
            body = None
            reasoning = "Customer recently contacted, avoiding fatigue"
        
        decisions_data.append({
            "decision_id": decision_id,
            "tenant_id": tenant_id,
            "campaign_id": campaign_id,
            "customer_id": customer["customer_id"],
            "timestamp": datetime.now(),
            "action": action,
            "channel": channel,
            "message_subject": subject,
            "message_body": body,
            "reasoning_summary": reasoning,
            "confidence_score": float(random.uniform(0.7, 0.95)),
            "customer_segment": customer["segment"],
            "churn_risk": customer["churn_risk_score"],
            "model_version": "v1.0",
            "execution_time_ms": random.randint(800, 2000)
        })
    
    if decisions_data:
        decisions_df = spark.createDataFrame(decisions_data)
        decisions_df.write.format("delta").mode("append").saveAsTable("cdp_platform.core.agent_decisions")
        print(f"✓ Created {len(decisions_data)} agent decisions")
    
    # 5. Generate Sample Deliveries
    print("Generating sample deliveries...")
    
    deliveries_data = []
    for decision in decisions_data:
        if decision["action"] == "contact":
            delivery_id = f"del_{uuid.uuid4().hex[:8]}"
            deliveries_data.append({
                "delivery_id": delivery_id,
                "tenant_id": tenant_id,
                "decision_id": decision["decision_id"],
                "customer_id": decision["customer_id"],
                "campaign_id": campaign_id,
                "channel": decision["channel"],
                "sent_at": datetime.now() - timedelta(days=random.randint(0, 7)),
                "to_address": customers_data[decisions_data.index(decision)]["email"],
                "subject": decision["message_subject"],
                "message_preview": decision["message_body"][:100] if decision["message_body"] else None,
                "status": "sent",
                "delivered": True,
                "opened": random.choice([True, False]),
                "clicked": random.choice([True, False]) if random.choice([True, False]) else False,
                "converted": random.choice([True, False]) if random.choice([True, False]) else False,
                "cost_usd": float(random.uniform(0.01, 0.05))
            })
    
    if deliveries_data:
        deliveries_df = spark.createDataFrame(deliveries_data)
        deliveries_df.write.format("delta").mode("append").saveAsTable("cdp_platform.core.deliveries")
        print(f"✓ Created {len(deliveries_data)} deliveries")
    
    print("\n✓ Demo data generation complete!")
    print(f"  - {num_customers} customers")
    print(f"  - {len(events_data)} events")
    print(f"  - 1 campaign")
    print(f"  - {len(decisions_data)} agent decisions")
    print(f"  - {len(deliveries_data)} deliveries")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("CDP Demo Data") \
        .getOrCreate()
    
    generate_demo_data(spark, tenant_id="demo_tenant", num_customers=100)

