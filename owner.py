import logging
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select, func
from ..db.session import async_session_factory
from ..db.models import User, Match
from ..config import config

logger = logging.getLogger("gullycric.owner")

OWNER_ID = 8445198778


def _is_owner(user) -> bool:
    return bool(user and (user.id == OWNER_ID or user.id in config.owner_ids))


async def owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_owner(user):
        if update.message:
            await update.message.reply_html("❌ <b>Access Denied:</b> Owner privileges required.")
        return

    async with async_session_factory() as session:
        user_count = (await session.execute(select(func.count(User.user_id)))).scalar() or 0
        match_count = (await session.execute(select(func.count(Match.match_id)))).scalar() or 0
        total_runs = (await session.execute(select(func.sum(User.total_runs)))).scalar() or 0

    text = (
        f"👑 <b>ULTIMATE CRICKET • OWNER CONTROL PANEL</b> 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Owner ID: <code>{user.id} ({user.first_name})</code>\n"
        f"📊 Registered Users: <b>{user_count:,}</b>\n"
        f"🏏 Total Matches Recorded: <b>{match_count:,}</b>\n"
        f"⚡ Total Career Runs: <b>{total_runs:,}</b>\n\n"
        f"🛠️ <b>Quick Admin Commands:</b>\n"
        f"• <code>/broadcast &lt;text&gt;</code> - Broadcast message to users\n"
        f"• <code>/donate &lt;user_id or @username&gt; &lt;amount&gt;</code> - Add diamonds\n"
        f"• <code>/serverstats</code> - System diagnostics"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast", callback_data="owner_broadcast_help")],
        [InlineKeyboardButton("🔄 Refresh Stats", callback_data="owner_refresh")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_home")]
    ])

    if update.message:
        await update.message.reply_html(text, reply_markup=kb)
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_owner(user):
        return

    args = context.args
    if not args:
        await update.message.reply_html("⚠️ Usage: <code>/broadcast Your message here</code>")
        return

    msg = " ".join(args)
    async with async_session_factory() as session:
        users = (await session.execute(select(User))).scalars().all()

    sent = 0
    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u.user_id,
                text=f"📢 <b>ULTIMATE CRICKET ANNOUNCEMENT</b>\n━━━━━━━━━━━━━━━━━━━━━━\n{msg}",
                parse_mode="HTML"
            )
            sent += 1
        except Exception:
            pass

    await update.message.reply_html(f"✅ Broadcast sent successfully to <b>{sent}</b> users!")

async def addrubies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _donate_command(update, context)


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _donate_command(update, context)


async def _donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_owner(user):
        return

    message = update.message
    if not message:
        return

    args = context.args or []
    reply_user = (
        message.reply_to_message.from_user
        if message.reply_to_message and message.reply_to_message.from_user
        else None
    )
    target_id = None
    target_username = None
    target_name = "Player"
    username_not_found = False

    mention_entity = next(
        (entity for entity in (message.entities or []) if entity.type == "text_mention" and entity.user),
        None,
    )
    amount_text = args[-1] if args else None
    if reply_user:
        target_id = reply_user.id
        target_username = reply_user.username
        target_name = reply_user.first_name
    elif mention_entity:
        mentioned_user = mention_entity.user
        target_id = mentioned_user.id
        target_username = mentioned_user.username
        target_name = mentioned_user.first_name
    elif len(args) >= 2 and args[0].isdigit():
        target_id = int(args[0])
    elif len(args) >= 2 and args[0].startswith("@"):
        target_username = args[0][1:]
        async with async_session_factory() as session:
            target = (
                await session.execute(
                    select(User).where(func.lower(User.username) == target_username.lower())
                )
            ).scalar_one_or_none()
            if target:
                target_id = target.user_id
                target_name = target.first_name or "Player"
                target_username = target.username
            else:
                username_not_found = True

    if not target_id or not amount_text:
        if username_not_found:
            await message.reply_html("❌ That @username is not registered. Ask them to start the bot first.")
            return
        await message.reply_html(
            "⚠️ Use <code>/donate &lt;user_id or @username&gt; &lt;amount&gt;</code>, "
            "or reply to a user's message with <code>/donate &lt;amount&gt;</code>."
        )
        return

    try:
        amount = int(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.reply_html("❌ Amount must be a positive whole number of diamonds.")
        return

    async with async_session_factory() as session:
        db_u = await session.get(User, target_id)
        if not db_u:
            db_u = User(
                user_id=target_id,
                username=target_username,
                first_name=target_name,
                diamonds=100,
            )
            session.add(db_u)
        db_u.diamonds = (db_u.diamonds or 0) + amount
        await session.commit()

    display_name = html.escape(target_name or f"User {target_id}")
    await message.reply_html(
        f"✅ Added <b>{amount:,}</b> 💎 to <b>{display_name}</b>."
    )
