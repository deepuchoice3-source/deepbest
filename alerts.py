"""
Smart Alerts module for Email/SMS/Telegram notifications
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class AlertService:
    """Handle alert notifications for trading signals"""
    
    def __init__(self):
        """Initialize alert service with configuration"""
        self.email_enabled = os.getenv('ENABLE_EMAIL_ALERTS', 'False') == 'True'
        self.telegram_enabled = os.getenv('ENABLE_TELEGRAM_ALERTS', 'False') == 'True'
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_from = os.getenv('EMAIL_FROM', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.email_to = os.getenv('EMAIL_TO', '').split(',')
        
        # Telegram configuration
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        # Alert thresholds
        self.signal_strength_threshold = int(os.getenv('SIGNAL_STRENGTH_THRESHOLD', '70'))
    
    def should_send_alert(self, signal: str, strength: int) -> bool:
        """Determine if alert should be sent based on signal and strength"""
        if signal == 'HOLD':
            return False
        return strength >= self.signal_strength_threshold
    
    def send_email_alert(self, subject: str, body: str):
        """Send email alert"""
        if not self.email_enabled or not self.email_from or not self.email_password:
            print("Email alerts not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_from, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_from, self.email_to, text)
            server.quit()
            
            print(f"Email alert sent: {subject}")
            return True
        except Exception as e:
            print(f"Error sending email alert: {e}")
            return False
    
    def send_telegram_alert(self, message: str):
        """Send Telegram alert"""
        if not self.telegram_enabled or not self.telegram_bot_token or not self.telegram_chat_id:
            print("Telegram alerts not configured")
            return False
        
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"Telegram alert sent successfully")
                return True
            else:
                print(f"Telegram alert failed: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
            return False
    
    def format_signal_alert(self, stock_data: Dict) -> tuple:
        """Format signal data for alert"""
        symbol = stock_data.get('symbol', 'Unknown')
        signal = stock_data.get('signal', 'HOLD')
        strength = stock_data.get('signal_strength', 0)
        price = stock_data.get('price', 0)
        change_percent = stock_data.get('change_percent', 0)
        reasons = stock_data.get('signal_reasons', [])
        
        # Email subject
        signal_icon = '📈' if signal == 'BUY' else '📉' if signal == 'SELL' else '⏸️'
        subject = f"{signal_icon} {signal} Signal: {symbol} ({strength}%)"
        
        # Email/Telegram body
        body_html = f"""
        <h2>{signal_icon} Trading Signal Alert</h2>
        <h3>{symbol}</h3>
        <p><strong>Signal:</strong> {signal} ({strength}% strength)</p>
        <p><strong>Price:</strong> ₹{price:,.2f}</p>
        <p><strong>Change:</strong> {change_percent:+.2f}%</p>
        <p><strong>Analysis:</strong></p>
        <ul>
        {''.join([f'<li>{reason}</li>' for reason in reasons])}
        </ul>
        <p><em>Generated at: {stock_data.get('timestamp', 'N/A')}</em></p>
        """
        
        telegram_text = f"""
<b>{signal_icon} Trading Signal Alert</b>

<b>{symbol}</b>
Signal: {signal} ({strength}% strength)
Price: ₹{price:,.2f}
Change: {change_percent:+.2f}%

<b>Analysis:</b>
{chr(10).join(['• ' + reason for reason in reasons])}

Generated at: {stock_data.get('timestamp', 'N/A')}
        """
        
        return subject, body_html, telegram_text
    
    def send_signal_alert(self, stock_data: Dict):
        """Send alert for trading signal"""
        signal = stock_data.get('signal', 'HOLD')
        strength = stock_data.get('signal_strength', 0)
        
        if not self.should_send_alert(signal, strength):
            return
        
        subject, body_html, telegram_text = self.format_signal_alert(stock_data)
        
        # Send email
        if self.email_enabled:
            self.send_email_alert(subject, body_html)
        
        # Send Telegram
        if self.telegram_enabled:
            self.send_telegram_alert(telegram_text)
    
    def send_portfolio_update(self, pnl_data: Dict):
        """Send portfolio P&L update"""
        subject = f"📊 Portfolio Update: {pnl_data.get('pnl_percent', 0):+.2f}%"
        
        body_html = f"""
        <h2>📊 Portfolio Performance Update</h2>
        <p><strong>Total Investment:</strong> ₹{pnl_data.get('total_investment', 0):,.2f}</p>
        <p><strong>Current Value:</strong> ₹{pnl_data.get('current_value', 0):,.2f}</p>
        <p><strong>Realized P&L:</strong> ₹{pnl_data.get('realized_pnl', 0):+,.2f}</p>
        <p><strong>Unrealized P&L:</strong> ₹{pnl_data.get('unrealized_pnl', 0):+,.2f}</p>
        <p><strong>Total P&L:</strong> ₹{pnl_data.get('total_pnl', 0):+,.2f} ({pnl_data.get('pnl_percent', 0):+.2f}%)</p>
        """
        
        telegram_text = f"""
<b>📊 Portfolio Performance Update</b>

Total Investment: ₹{pnl_data.get('total_investment', 0):,.2f}
Current Value: ₹{pnl_data.get('current_value', 0):,.2f}

Realized P&L: ₹{pnl_data.get('realized_pnl', 0):+,.2f}
Unrealized P&L: ₹{pnl_data.get('unrealized_pnl', 0):+,.2f}

<b>Total P&L: ₹{pnl_data.get('total_pnl', 0):+,.2f} ({pnl_data.get('pnl_percent', 0):+.2f}%)</b>
        """
        
        if self.email_enabled:
            self.send_email_alert(subject, body_html)
        
        if self.telegram_enabled:
            self.send_telegram_alert(telegram_text)
