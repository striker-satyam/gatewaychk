import requests
from bs4 import BeautifulSoup
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio

class WebsiteAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Payment gateway indicators
        self.payment_gateways = {
            "paypal": ["paypal.com", "paypalobjects.com", "paypal"],
            "stripe": ["stripe.com", "stripe.js", "stripe"],
            "braintree": ["braintreepayments.com", "braintree-api", "braintree"],
            "square": ["squareup.com", "squarecdn.com", "square"],
            "magento": ["magento.com", "mage", "magentopayments"],
            "convergepay": ["converge-NDpay.com", "converge"],
            "paysimple": ["paysimple.com", "paysimple"],
            "oceanpayments": ["oceanpayment.com", "oceanpayments"],
            "eprocessing": ["eprocessingnetwork.com", "eprocessing"],
            "hipay": ["hipay.com", "hipay"],
            "worldpay": ["worldpay.com", "worldpay"],
            "cybersource": ["cybersource.com", "cybersource"],
            "payjunction": ["payjunction.com", "payjunction"],
            "authorize.net": ["authorize.net", "auth.net", "authorizenet"],
            "2checkout": ["2checkout.com", "2co.com", "2checkout"],
            "adyen": ["adyen.com", "adyen"],
            "checkout.com": ["checkout.com", "cko"],
            "payflow": ["payflow", "payflowlink", "paypal.com/payflow"],
            "payeezy": ["payeezy", "firstdata.com", "payeezy"],
            "usaepay": ["usaepay.com", "usaepay"],
            "creo": ["creopay", "creo"],
            "squareup": ["squareup.com", "square"],
            "authnet": ["authorize.net", "authnet"],
            "ebizcharge": ["ebizcharge.com", "ebiz"],
            "cpay": ["cpay.com", "cpay"],
            "moneris": ["moneris.com", "moneris"],
            "recurly": ["recurly.com", "recurly"],
            "cardknox": ["cardknox.com", "cardknox"],
            "chargify": ["chargify.com", "chargify"],
            "paytrace": ["paytrace.com", "paytrace"],
            "securepay": ["securepay.com", "securepay"],
            "eway": ["ewaypayments.com", "eway"],
            "blackbaud": ["blackbaud.com", "blackbaud"],
            "lawpay": ["lawpay.com", "lawpay"],
            "clover": ["clover.com", "clover"],
            "cardconnect": ["cardconnect.com", "cardconnect"],
            "bluepay": ["bluepay.com", "bluepay"],
            "fluidpay": ["fluidpay.com", "fluidpay"],
            "chasepaymentech": ["chasepaymentech.com", "chase"],
            "auruspay": ["auruspay.com", "aurus"],
            "sagepayments": ["sagepay.com", "sagepayments"],
            "paycomet": ["paycomet.com", "paycomet"],
            "geomerchant": ["geomerchant.com", "geomerchant"],
            "realexpayments": ["realexpayments.com", "realex"],
            "rocketgateway": ["rocketgateway.com", "rocketgate"],
            "shopify": ["shopify.com", "shopifycdn", "shop"],
            "woocommerce": ["woocommerce.com", "wp-content", "woo"],
            "bigcommerce": ["bigcommerce.com", "bigcommerce"],
            "opencart": ["opencart.com", "opencart"],
            "prestashop": ["prestashop.com", "presta"],
            "razorpay": ["razorpay.com", "razorpay"],
        }
        
        self.security_indicators = {
            'captcha': ['captcha', 'protected by recaptcha', "i'm not a robot", 'recaptcha/api.js'],
            'cloudflare': ['cloudflare', 'cdnjs.cloudflare.com', 'challenges.cloudflare.com']
        }
        
        self.platform_indicators = {
            'woocommerce': ['wp-content', 'woocommerce', 'woo'],
            'shopify': ['shopify.com', 'shopifycdn', 'shop'],
            'magento': ['magento', 'mage'],
            'bigcommerce': ['bigcommerce.com', 'bigcommerce'],
            'opencart': ['opencart.com', 'opencart'],
            'prestashop': ['prestashop.com', 'presta']
        }

    async def analyze_website(self, url, bot, chat_id):
        """Analyze a website for payment gateways, security, and platform indicators."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            status_code = response.status_code
            scripts = [script.get('src') for script in soup.find_all('script') if script.get('src')]
            content = response.text.lower()
            
            detected_gateways = []
            for gateway, indicators in self.payment_gateways.items():
                if any(indicator in content for indicator in indicators) or \
                   any(script and any(indicator in script for indicator in indicators) for script in scripts):
                    detected_gateways.append(gateway.capitalize())
            
            has_captcha = any(captcha in content for captcha in self.security_indicators['captcha'])
            has_cloudflare = any(cf in content for cf in self.security_indicators['cloudflare']) or \
                             'cf-ray' in str(response.headers).lower()
            has_graphql = 'graphql' in content
            
            detected_platform = 'Unknown'
            for platform, indicators in self.platform_indicators.items():
                if any(indicator in content for indicator in indicators):
                    detected_platform = platform.capitalize()
                    break
            
            result_message = self.format_results(
                url=url,
                gateways=detected_gateways,
                captcha=has_captcha,
                cloudflare=has_cloudflare,
                graphql=has_graphql,
                platform=detected_platform,
                status=status_code
            )
            
            await bot.send_message(chat_id=chat_id, text=result_message, parse_mode="HTML")
            
            # Check if captcha, cloudflare, and graphql are all False
            if not has_captcha and not has_cloudflare and not has_graphql:
                specific_chat_id = 6775748231
                additional_message = f"🚨 Website {url} has no Captcha, Cloudflare, or GraphQL detected."
                await bot.send_message(chat_id=specific_chat_id, text=additional_message, parse_mode="HTML")
            
        except Exception as e:
            error_message = f"Error analyzing {url}: {str(e)}"
            await bot.send_message(chat_id=chat_id, text=error_message, parse_mode="HTML")

    def format_results(self, url, gateways, captcha, cloudflare, graphql, platform, status):
        return f"""
🔍 Website Analysis Result
━━━━━━━━━━━━━
🚀 URL: <code>{url}</code>
🚀 Payment Gateways: <code>{', '.join(gateways) if gateways else 'None detected'}</code>
🚀 Captcha: <code>{captcha}</code>
🚀 Cloudflare: <code>{cloudflare}</code>
🚀 GraphQL: <code>{graphql}</code>
🚀 Platform: <code>{platform}</code>
🚀 Status: <code>{status}</code>
♨️ Dev -> @CODExHYPER
"""

# Bot handlers
async def start(update, context):
    welcome_message = f"""
    👋 Welcome to Website Analyzer Bot!

I can analyze websites for:
- Payment gateways
- Security measures (Captcha, Cloudflare)
- Platform detection
- And more!

📌 How to use:
1. Send /url example.com to analyze a website

🔍 Examples: /url shopify.com

BOT BY -> @CODExHYPER
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_message
    )

async def url_command(update, context):
    analyzer = WebsiteAnalyzer()
    chat_id = update.effective_chat.id
    
    if not context.args:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please provide a URL. Usage: /url <website> or .url <website>"
        )
        return
        
    url = context.args[0]
    await analyzer.analyze_website(url, context.bot, chat_id)

async def handle_message(update, context):
    message_text = update.message.text
    chat_id = update.effective_chat.id
    analyzer = WebsiteAnalyzer()
    
    if message_text.startswith('.url'):
        try:
            url = message_text.split('.url')[1].strip()
            if url:
                await analyzer.analyze_website(url, context.bot, chat_id)
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Please provide a URL after .url"
                )
        except IndexError:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Please provide a URL after .url"
            )

def main():
    BOT_TOKEN = "7309442212:AAEsAXmr-QUrHrvEiiWzpHGbz2XSgCsnSwM"
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("url", url_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
