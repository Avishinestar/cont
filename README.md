# Nifty 500 Bids & Contracts Dashboard 💠

An animated, glassmorphism-styled dashboard that tracks live **Order Wins, Bids, and Contracts** for Nifty 500 companies.

![Dashboard Preview](dashboard_preview.png)

## Features
- **Real-Time Data**: Scrapes live announcements from [Screener.in](https://www.screener.in).
- **Sentiment Analysis**: Automatically detects positive (👍 Wins) and negative (👎 Penalties) news.
- **Visual Stats**: Displays "Deal Value" and "Total Order Book" stats in pill badges.
- **Sorting**: "This Week" vs "Archive" tabs.
- **Direct Links**: One-click access to official BSE/NSE PDF filings.

## Setup & Running smoothly

### Prerequisites
- Python 3.x
- A modern web browser

### Installation
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Update Session Cookie (Optional)**:
    - The script uses a hardcoded session ID for Screener.in.
    - If data fetching fails, log in to Screener.in, get your `sessionid` cookie, and update `SESSION_ID` in `fetch_real_data.py`.

### How to Run
1.  **Fetch Latest Data**:
    ```bash
    python fetch_real_data.py
    ```
    *This generates `data.json` with the latest 5 pages of orders.*

2.  **Start the Server**:
    One-liner to host the dashboard:
    ```bash
    python -m http.server 8000
    ```

3.  **View Dashboard**:
    Open [http://localhost:8000](http://localhost:8000) in your browser.

## Technologies
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (ES6).
- **Backend**: Python (BeautifulSoup4) for scraping.
- **Data**: JSON storage.
