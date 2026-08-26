"""
Bot Telegram com cotações BTC/ETH/EUR em tempo real.
Configure o TELEGRAM_BOT_TOKEN no .env antes de iniciar.
"""
import os, requests, logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

COINS = {'btc': 'bitcoin', 'eth': 'ethereum', 'sol': 'solana', 'ada': 'cardano', 'dot': 'polkadot'}

def get_prices(coins: list[str]) -> dict:
    ids = ','.join([COINS.get(c.lower(), c.lower()) for c in coins])
    try:
        r = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur,usd&include_24hr_change=true', timeout=10)
        return r.json()
    except Exception as e:
        return {}

def format_price(data: dict, coin_id: str) -> str:
    if coin_id not in data:
        return f"❌ `{coin_id}` não encontrado"
    d = data[coin_id]
    change = d.get('eur_24h_change', 0)
    arrow = '📈' if change >= 0 else '📉'
    return f"{arrow} *{coin_id.upper()}*\n   EUR: `€{d.get('eur', 0):,.2f}` ({change:+.2f}%)\n   USD: `${d.get('usd', 0):,.2f}`"

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *VibeCrypto Bot* — Cotações em Tempo Real\n\n"
        "📋 *Comandos:*\n"
        "/btc — Bitcoin\n/eth — Ethereum\n/sol — Solana\n"
        "/cripto btc eth sol — Várias moedas\n/top — Top 5 moedas\n/alerta — Alertas de preço",
        parse_mode='Markdown'
    )

async def btc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = get_prices(['bitcoin'])
    await update.message.reply_text(format_price(data, 'bitcoin'), parse_mode='Markdown')

async def eth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = get_prices(['ethereum'])
    await update.message.reply_text(format_price(data, 'ethereum'), parse_mode='Markdown')

async def sol(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = get_prices(['solana'])
    await update.message.reply_text(format_price(data, 'solana'), parse_mode='Markdown')

async def cripto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    coins = ctx.args if ctx.args else ['bitcoin', 'ethereum', 'solana']
    coin_ids = [COINS.get(c.lower(), c.lower()) for c in coins]
    data = get_prices(coin_ids)
    lines = [format_price(data, cid) for cid in coin_ids]
    await update.message.reply_text('\n\n'.join(lines), parse_mode='Markdown')

async def top(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&order=market_cap_desc&per_page=5&page=1', timeout=10)
        coins = r.json()
        lines = ['🏆 *Top 5 Criptomoedas por Market Cap*\n']
        for i, c in enumerate(coins, 1):
            change = c.get('price_change_percentage_24h', 0)
            arrow = '📈' if change >= 0 else '📉'
            lines.append(f"{i}. {arrow} *{c['symbol'].upper()}* — `€{c['current_price']:,.2f}` ({change:+.2f}%)")
        await update.message.reply_text('\n'.join(lines), parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("❌ Erro ao obter dados. Tente novamente.")

def main():
    if not TOKEN:
        print("❌ Configure TELEGRAM_BOT_TOKEN no .env")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('btc', btc))
    app.add_handler(CommandHandler('eth', eth))
    app.add_handler(CommandHandler('sol', sol))
    app.add_handler(CommandHandler('cripto', cripto))
    app.add_handler(CommandHandler('top', top))
    print('🤖 Bot iniciado! Pressione Ctrl+C para parar.')
    app.run_polling()

if __name__ == '__main__':
    main()
