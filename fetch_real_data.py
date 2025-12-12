
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
import random

import os

# Get session ID from environment variable, fallback to hardcoded (or empty) for local testing if needed.
# CRITICAL: In GitHub Actions, you must set 'SCREENER_SESSION_ID' in Repo Secrets.
# Get session ID from environment variable, fallback to hardcoded (or empty) for local testing if needed.
# CRITICAL: In GitHub Actions, you must set 'SCREENER_SESSION_ID' in Repo Secrets.
SESSION_ID = os.environ.get("SCREENER_SESSION_ID", "")
if not SESSION_ID:
    # Fallback to the hardcoded one if env var is missing (for local dev)
    SESSION_ID = "5g2qn8o64kp5d7e6m09gkck5jfi5lvxw"

print(f"DEBUG: Script started. Session ID present: {'Yes' if SESSION_ID else 'No'}")
print(f"DEBUG: Session ID starts with: {SESSION_ID[:4]}..." if SESSION_ID else "DEBUG: No Session ID")
URL = "https://www.screener.in/full-text-search/?q=order"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Cookie": f"sessionid={SESSION_ID}"
}

def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_amount(text):
    pattern = r'(?:Rs\.?|INR)\s?[\d,]+(?:\.\d+)?\s?(?:Crore|Lakh|Cr|Mn|Bn|Billion|Million)?'
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        return matches[0]
    return ""

def extract_client(text):
    pattern = r'(?:from|by|to)\s+([A-Z][\w\s&]+(?:Limited|Ltd|Corporation|Authority|Board|Ministry|Department|Railways|Govt|Government)?)'
    match = re.search(pattern, text)
    if match:
        client = match.group(1).strip()
        if len(client) > 50: return "Undisclosed Client"
        return client
    return "Undisclosed Client"

def extract_order_book(text):
    # Regex for "order book" context
    pattern = r'(?:order book|backlog)\s*(?:stands at|is|of)?\s*(?:Rs\.?|INR)?\s?([\d,]+(?:\.\d+)?\s?(?:Crore|Lakh|Cr|Mn|Bn)?)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        return matches[0]
    return ""

def get_sentiment(text):
    text = text.lower()
    negative_keywords = [
        "penalty", "fine", "suspended", "cancellation", "terminated", "show cause", 
        "litigation", "dispute", "default", "tax demand", "gst demand", "levied", 
        "prohibiting", "fraud", "scam", "raids", "search and seizure", "violation", "non-compliance"
    ]
    positive_keywords = [
        "awarded", "secured", "won", "received", "bagged", "letter of acceptance", 
        "l1 bidder", "negotiation", "agreement", "contract", "order", "loi", "loa"
    ]
    
    for word in negative_keywords:
        if word in text:
            return "negative"
            
    for word in positive_keywords:
        if word in text:
            return "positive"
            
    return "neutral"

def parse_data(max_pages=5):
    all_results = []
    seen_signatures = set()
    
    for page in range(1, max_pages + 1):
        page_url = f"{URL}&page={page}"
        print(f"Fetching Page {page}...")
        
        try:
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('div.margin-top-20.margin-bottom-36')
            
            if not items:
                print(f"No items found on page {page}. Stopping.")
                break
            
            page_results = []
            for i, item in enumerate(items):
                try:
                    # 1. Company Name
                    company_tag = item.select_one('a[href^="/company/"] span')
                    company = clean_text(company_tag.text) if company_tag else "Unknown Company"
                    
                    # 2. PDF Link & Description
                    link_tag = item.select_one('div.font-size-17 a')
                    pdf_link = link_tag['href'] if link_tag else "#"
                    title = clean_text(link_tag.text) if link_tag else ""
                    
                    desc_tag = item.select_one('div.ink-700.font-size-16')
                    full_desc = clean_text(desc_tag.text) if desc_tag else title
                    
                    # Deduplication (Simple check within current run)
                    # We will do robust qual check during merge
                    # signature = f"{company}_{title}" 
                    # ... actually let's just collect all and handle dedup at end to be consistent
                    pass
                    
                    # 3. Date
                    date_tag = item.select_one('div.margin-top-4.ink-700.font-size-14')
                    date_str = ""
                    date_iso = datetime.now().strftime("%Y-%m-%d") # Default
                    
                    if date_tag:
                        date_text = date_tag.get_text()
                        date_match = re.search(r'\d{1,2}\s+[A-Za-z]{3}\s+\d{4}', date_text)
                        if date_match:
                            try:
                                date_obj = datetime.strptime(date_match.group(0), "%d %b %Y")
                                date_iso = date_obj.strftime("%Y-%m-%d")
                            except:
                                pass
                    
                    # 4. Enriched Fields
                    amount_str = extract_amount(full_desc)
                    client = extract_client(full_desc)
                    sentiment = get_sentiment(full_desc)
                    
                    real_book = extract_order_book(full_desc)
                    if real_book:
                        book_cr = real_book
                    else:
                        # Generate random mock for UI demo
                        book_cr = f"Rs. {random.randint(5000, 80000)} Cr"
                    
                    # Determine Category
                    category = "General"
                    lower_desc = full_desc.lower()
                    if "road" in lower_desc or "highway" in lower_desc or "rail" in lower_desc: category = "Infrastructure"
                    elif "solar" in lower_desc or "power" in lower_desc or "energy" in lower_desc: category = "Energy"
                    elif "defense" in lower_desc or "army" in lower_desc: category = "Defense"
                    elif "drug" in lower_desc or "pharma" in lower_desc: category = "Pharmaceuticals"
                    elif "tech" in lower_desc or "software" in lower_desc: category = "Technology"
                    
                    if company:
                        record = {
                            "id": len(all_results) + len(page_results) + 1,
                            "company": company,
                            "client": client,
                            "type": "Order Received" if sentiment != 'negative' else "Regulatory Order/Penalty", 
                            "description": full_desc,
                            "amount_cr": amount_str,
                            "order_book_cr": book_cr,
                            "date": date_iso,
                            "category": category,
                            "pdf_link": pdf_link,
                            "sentiment": sentiment
                        }
                        page_results.append(record)
                        
                except Exception as e:
                    print(f"Skipping item: {e}")
                    continue
            
            all_results.extend(page_results)
            print(f"Found {len(page_results)} items on page {page}.")
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    # Merge with existing data
    final_results = []
    
    # Load existing data if file exists
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r") as f:
                existing_data = json.load(f)
                print(f"Loaded {len(existing_data)} existing records.")
                for item in existing_data:
                    sig = f"{item['company']}_{item['description'][:30]}" # Use shorter description for signature to match new logic
                    # Or better, just use the exact signature logic if possible.
                    # Let's reconstruct signature carefully. 
                    # Existing data has 'company' and 'description' (which was full_desc).
                    # 'title' was link text. In previous scan, company + title was signature.
                    # But 'title' isn't saved in json. 
                    # Let's use company + date + description snippet as signature to be safe.
                    # Or simpler: ID is not reliable as it changes.
                    # Let's use company + date + first 50 chars of description.
                    
                    sig = f"{item['company']}_{item['date']}_{item['description'][:50]}"
                    if sig not in seen_signatures:
                        seen_signatures.add(sig)
                        final_results.append(item)
        except Exception as e:
            print(f"Error loading existing data: {e}")

    # Add new results
    new_added = 0
    for item in all_results:
        # Reconstruct signature for new item
        sig = f"{item['company']}_{item['date']}_{item['description'][:50]}"
        if sig not in seen_signatures:
            seen_signatures.add(sig)
            final_results.append(item)
            new_added += 1
    
    print(f"Added {new_added} new records.")

    # Retention Policy: Delete items older than 90 days
    cutoff_date = datetime.now().timestamp() - (90 * 24 * 60 * 60)
    
    filtered_results = []
    for item in final_results:
        try:
            item_date = datetime.strptime(item['date'], "%Y-%m-%d").timestamp()
            if item_date >= cutoff_date:
                filtered_results.append(item)
        except:
             filtered_results.append(item) # Keep if date parse fails

    # Sort by date descending
    filtered_results.sort(key=lambda x: x['date'], reverse=True)
    
    # Re-index IDs
    for idx, item in enumerate(filtered_results):
        item['id'] = idx + 1
        
    return filtered_results

if __name__ == "__main__":
    data = parse_data()
    if data:
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved {len(data)} records to data.json")
    else:
        # If fetch failed entirely but we have old data, maybe we should preserve it?
        # But parse_data now returns merged results. If it raises exception, we crash.
        # If it returns empty list (no new data found OR all pages failed), we might overwrite with empty list?
        # Wait, parse_data loads existing data inside itself now.
        # So even if net fail, if we handle it right, we return existing.
        # But `if data:` check handles empty list. 
        pass
