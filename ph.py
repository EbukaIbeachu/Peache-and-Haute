import json
import nest_asyncio
nest_asyncio.apply()

import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

BOT_TOKEN = 'insert bot token'
ADMIN_CHAT_ID = 'insert admin user id'  # Replace with your real admin ID

# Load products from products.json
with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("👠 View Shoes & Bags", callback_data="view_products")],
        [InlineKeyboardButton("📞 Contact Us", callback_data="contact")],
        [InlineKeyboardButton("📱 Instagram", url="https://www.instagram.com/peachandhaute")]
    ]
    welcome_text = (
        "*Welcome to Peache&Hautes 👠*\n"
        "Your go-to store for classy, affordable female shoes and bags.\n\n"
        "Explore our collection and order in one click!"
    )
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='Markdown'
    )

# Show product gallery
async def view_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    for idx, product in enumerate(PRODUCTS, start=1):
        media_group = [InputMediaPhoto(media=url) for url in product['photo_urls']]

        sent_messages = await context.bot.send_media_group(
            chat_id=query.message.chat_id,
            media=media_group
        )

        if product['sizes']:
            size_buttons = [
                InlineKeyboardButton(f"Size {size}", callback_data=f"select|{product['name']}|{size}")
                for size in product['sizes']
            ]
            keyboard = InlineKeyboardMarkup(
                [size_buttons[i:i + 3] for i in range(0, len(size_buttons), 3)]
            )
        else:
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🛒 Order Now", callback_data=f"order|{product['name']}")]]
            )

        caption = f"*{product['name']} (Style {idx})*\nPrice: {product['price']}"

        await context.bot.edit_message_caption(
            chat_id=query.message.chat_id,
            message_id=sent_messages[0].message_id,
            caption=caption,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

# Handle button selections
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")

    if data[0] == "select":
        _, product_name, size = data
        response = (
            f"✅ You've selected *{product_name}* - Size {size}.\n"
            "A team member will contact you shortly!"
        )
        await notify_admin(context, query.from_user, product_name, size)

    elif data[0] == "order":
        _, product_name = data
        response = (
            f"✅ You've ordered *{product_name}*.\n"
            "A team member will contact you shortly!"
        )
        await notify_admin(context, query.from_user, product_name)

    else:
        response = "⚠️ Unknown action."

    await query.edit_message_caption(caption=response, parse_mode='Markdown')

# Notify admin about order
async def notify_admin(context, user, product_name, size=None):
    if not ADMIN_CHAT_ID:
        return

    username = f"@{user.username}" if user.username else user.full_name
    if size:
        msg = f"📦 *New Order!*\nProduct: {product_name}\nSize: {size}\nUser: {username}"
    else:
        msg = f"📦 *New Order!*\nProduct: {product_name}\nUser: {username}"

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode='Markdown')

# Contact Info
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    contact_info = (
        "📞 *Contact Us*\n"
        "Phone: 08122650784\n"
        "Alt: +2347048618798\n"
        "Instagram: @peachandhaute"
    )
    await context.bot.send_message(chat_id=query.message.chat_id, text=contact_info, parse_mode='Markdown')

# Main function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(view_products, pattern="^view_products$"))
    app.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(handle_selection, pattern="^(select|order)\\|"))

    print("🚀 Bot is running...")
    await app.run_polling()

# Run the bot
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
