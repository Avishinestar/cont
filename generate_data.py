
import json
import random
from datetime import datetime, timedelta

# List of ~50 major Nifty 500 companies for demonstration
COMPANIES = [
    "Reliance Industries", "TCS", "HDFC Bank", "Infosys", "ICICI Bank", 
    "Hindustan Unilever", "SBI", "Bharti Airtel", "ITC", "Kotak Mahindra Bank",
    "Larsen & Toubro", "Axis Bank", "HCL Technologies", "Bajaj Finance", "Asian Paints",
    "Maruti Suzuki", "Titan Company", "Sun Pharma", "Wipro", "UltraTech Cement",
    "Nestle India", "Power Grid Corp", "Tata Motors", "NTPC", "JSW Steel",
    "Tata Steel", "Adani Enterprises", "Mahindra & Mahindra", "Coal India", "ONGC",
    "Bajaj Finserv", "Adani Ports", "Hindalco Industries", "Grasim Industries", "Tech Mahindra",
    "Britannia Industries", "Cipla", "Dr Reddys Labs", "Divis Labs", "Apollo Hospitals",
    "Eicher Motors", "Tata Consumer Products", "SBI Life Insurance", "BPCL", "Hero MotoCorp",
    "UPL", "IndusInd Bank", "Bajaj Auto", "Berger Paints"
]

CLIENTS = [
    "Indian Railways", "NHAI", "Ministry of Defence", "ONGC", "Saudi Aramco",
    "Tata Projects", "BHEL", "NTPC", "Infosys", "Government of India",
    "Reliance Jio", "Adani Green", "Delhi Metro", "ISRO", "DRDO"
]

CATEGORIES = ["Infrastructure", "Defense", "Technology", "Energy", "Telecommunications", "Pharmaceuticals"]
TYPES = ["Contract Won", "Bid Placed", "L1 Bidder", "Order Received", "Tender Submitted"]

def generate_data(num_records=100):
    data = []
    today = datetime.now()
    
    for i in range(num_records):
        company = random.choice(COMPANIES)
        event_type = random.choice(TYPES)
        client = random.choice(CLIENTS)
        
        # Random date between 0 and 30 days ago
        days_ago = random.randint(0, 30)
        date = today - timedelta(days=days_ago)
        
        # Weighted amount generation (in Crores)
        amount = round(random.uniform(10, 5000), 2)
        
        description = ""
        if event_type in ["Contract Won", "Order Received", "L1 Bidder"]:
            description = f"{company} has secured a major order from {client} for a {random.choice(CATEGORIES).lower()} project."
        else:
            description = f"{company} has submitted a bid to {client} for a new tender."
            
        if event_type == "Contract Won" or event_type == "Order Received":
            description += f" The value of the order is approximately ₹{amount} Cr."
        
        record = {
            "id": i + 1,
            "company": company,
            "client": client,
            "type": event_type,
            "description": description,
            "amount_cr": amount,
            "date": date.strftime("%Y-%m-%d"),
            "category": random.choice(CATEGORIES),
            "pdf_link": "#"  # Mock link
        }
        data.append(record)
    
    # Sort by date (newest first)
    data.sort(key=lambda x: x['date'], reverse=True)
    return data

if __name__ == "__main__":
    records = generate_data(100)
    with open("data.json", "w") as f:
        json.dump(records, f, indent=4)
    print(f"Generated {len(records)} records in data.json")
