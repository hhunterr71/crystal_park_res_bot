# Crystal Mountain Parking Reservation Bot

## Overview
This project automates parking reservations for Crystal Mountain Resort using Selenium WebDriver. It's available in two versions:

1. **Web Service** (Recommended) - Access from any device via a web browser
2. **CLI Script** - Command-line tool for local use

## Web Service (NEW!)

### Features
- Access from your phone, laptop, or any device with a browser
- Real-time status updates during reservation process
- Simple web form interface
- Runs 24/7 on cloud platform (no need to keep your computer on)
- Credentials are NOT stored on the server
- Automatically polls for availability

### Deployment to Render (Free)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy web service"
   git push origin main
   ```

2. **Create Render account**
   - Go to [render.com](https://render.com)
   - Sign up for free account

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the Dockerfile

4. **Configure Service**
   - Name: `crystal-parking-bot`
   - Region: Choose closest to you
   - Branch: `main`
   - Plan: **Free**
   - Click "Create Web Service"

5. **Wait for Deployment**
   - First build takes 5-10 minutes
   - You'll get a URL like: `https://crystal-parking-bot.onrender.com`

6. **Access Your Bot**
   - Visit the URL from any device
   - Enter credentials and date
   - Watch real-time status updates!

### Important Notes About Free Tier
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds (cold start)
- Perfectly fine for personal use
- No credit card required

### Local Testing (Web Service)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Flask app**
   ```bash
   python app.py
   ```

3. **Access locally**
   - Open browser to `http://localhost:5000`

### Docker Testing (Local)

```bash
# Build the image
docker build -t parking-bot .

# Run the container
docker run -p 5000:5000 parking-bot

# Access at http://localhost:5000
```

## CLI Script (Original)

The original command-line version is still available as `crystal_parking_reservation_bot.py`.

### Prerequisites
- Python 3.x
- Google Chrome
- ChromeDriver (automatically managed)

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/hhunterr71/crystal_park_res_bot.git
   cd crystal_park_res_bot
   ```

2. **Install dependencies**
   ```bash
   pip install selenium webdriver-manager
   ```

### Usage

Run the script:
```bash
python crystal_parking_reservation_bot.py
```

Follow the prompts:
- Enter username
- Enter password (hidden)
- Enter license plate
- Enter date (YYYY/MM/DD format)

The bot will:
1. Log in to your account
2. Navigate to parking reservation system
3. Poll for availability (checks every 5 seconds)
4. Automatically reserve when date becomes available

## How It Works

### Web Service Architecture
```
User Browser → Flask App → Background Thread → Selenium Bot
                   ↓
            Server-Sent Events (SSE)
                   ↓
           Real-time Status Updates
```

- Flask handles HTTP requests
- Bot runs in background thread
- SSE streams live updates to browser
- Session management with unique IDs

### Bot Workflow
1. **Login** - Sign in to Crystal Mountain account
2. **Select License Plate** - Fuzzy matching from dropdown
3. **Navigate to Calendar** - Click "Add More Days"
4. **Poll for Availability** - Check every 5 seconds, refresh if unavailable
5. **Reserve Parking** - Click date when available
6. **Complete Checkout** - Finalize reservation

## Project Structure

```
crystal_park_res_bot/
├── app.py                                  # Flask web application
├── bot/
│   ├── __init__.py
│   ├── reservation_bot.py                  # Core bot logic
│   └── driver_manager.py                   # Chrome driver setup
├── templates/
│   ├── index.html                          # Input form
│   └── status.html                         # Status display with SSE
├── static/
│   └── css/
│       └── style.css                       # Styling
├── crystal_parking_reservation_bot.py      # Original CLI script
├── Dockerfile                              # Container configuration
├── requirements.txt                        # Python dependencies
├── render.yaml                             # Render deployment config
└── README.md                               # This file
```

## Troubleshooting

### Web Service Issues

**Q: First load is very slow (30-60 seconds)**
A: This is normal - free tier services sleep after inactivity. Subsequent requests are fast.

**Q: Connection error or timeout**
A: Refresh the page. The bot may still be running in the background.

**Q: Can't see status updates**
A: Check browser console for errors. Ensure JavaScript is enabled.

### CLI Script Issues

**Q: ChromeDriver not found**
A: The script automatically downloads ChromeDriver. Ensure you have internet connection.

**Q: Element not found errors**
A: Website structure may have changed. Check XPath selectors in code.

**Q: Date not being found**
A: Ensure date format is YYYY/MM/DD. The bot uses wildcard matching for timestamps.

## Security Notes

- **Credentials NOT Stored**: Web service requires credentials each time
- **Headless Mode**: Cloud deployment runs Chrome without GUI
- **No Logging**: Credentials are not logged anywhere
- **HTTPS**: Render provides free SSL certificates

## Contributing

This is a personal automation tool. Use at your own risk. Crystal Mountain may update their website, which could break the automation.

## License

This project is for educational and personal use only. Respect the terms of service of Crystal Mountain's parking reservation system.

## Support

For issues or questions:
- Check troubleshooting section above
- Review bot logic in `bot/reservation_bot.py`
- Test locally before deploying

## Version History

- **v2.0** - Web service with SSE, Docker support, cloud deployment
- **v1.1** - Fixed date matching with wildcard approach
- **v1.0** - Initial CLI script with Selenium automation
