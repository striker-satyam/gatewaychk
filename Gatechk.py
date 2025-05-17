import requests
from bs4 import BeautifulSoup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update
import asyncio

class WebsiteAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

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

            if not has_captcha and not has_cloudflare and not has_graphql:
                specific_chat_id = 6775748231
                await bot.send_message(
                    chat_id=specific_chat_id,
                    text=f"🚨 Website {url} has no Captcha, Cloudflare, or GraphQL detected.",
                    parse_mode="HTML"
                )

        except Exception as e:
            await bot.send_message(chat_id=chat_id, text=f"❌ Error analyzing {url}:\n<code>{str(e)}</code>", parse_mode="HTML")

    def format_results(self, url, gateways, captcha, cloudflare, graphql, platform, status):
        return f"""
🔍 <b>Website Analysis Result</b>
━━━━━━━━━━━━━
🌐 <b>URL:</b> <code>{url}</code>
💳 <b>Payment Gateways:</b> <code>{', '.join(gateways) if gateways else 'None detected'}</code>
🧠 <b>Captcha:</b> <code>{captcha}</code>
🛡️ <b>Cloudflare:</b> <code>{cloudflare}</code>
🔗 <b>GraphQL:</b> <code>{graphql}</code>
📦 <b>Platform:</b> <code>{platform}</code>
📶 <b>Status Code:</b> <code>{status}</code>
♨️ <b>Dev:</b> @CODExHYPER
"""

# === Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
👋 Welcome to Website Analyzer Bot!

I can analyze websites for:
- Payment gateways
- Security (Captcha, Cloudflare)
- Platform detection

📌 Send /url <website> or .url <website>

🔍 Example: /url shopify.com
BOT BY -> @CODExHYPER
""")


async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    analyzer = WebsiteAnalyzer()
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text("❗ Please provide a URL. Example: /url example.com")
        return

    url = context.args[0]
    await analyzer.analyze_website(url, context.bot, chat_id)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    chat_id = update.effective_chat.id
    analyzer = WebsiteAnalyzer()

    if message_text.lower().startswith('.url'):
        parts = message_text.split('.url', 1)
        if len(parts) > 1 and parts[1].strip():
            url = parts[1].strip()
            await analyzer.analyze_website(url, context.bot, chat_id)
        else:
            await update.message.reply_text("❗ Please provide a URL after .url")

def main():
    BOT_TOKEN = "7309442212:AAEsAXmr-QUrHrvEiiWzpHGbz2XSgCsnSwM"
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("url", url_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
