import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.request import HTTPXRequest
from .config import config
from .middlewares import error_handler

# Handlers
from .handlers.start import start_command, help_command
from .handlers.solo import (
    game_command,
    solo_command,
    join_command,
    leave_command,
    extend_command,
    forcestart_command,
    endsolo_command,
    replay_command,
    soloscore_command,
    solo_callback_handler,
    handle_chat_text_input,
)
from .handlers.team import (
    team_lobby_command,
    team_callback_handler,
    set_overs_command,
    toss_command,
    batting_command,
    bowling_command,
    force_add_command,
    team_command,
    score_command as team_score_command,
    change_cap_command,
    change_host_command,
    spamfree_command,
    end_match_command,
    handle_team_chat_input,
)
from .handlers.stats import (
    stats_command,
    leaderboard_command,
)
from .handlers.owner import (
    owner_command,
    broadcast_command,
    donate_command,
    addrubies_command,
)

logger = logging.getLogger("gullycric")

async def smart_score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat and chat.type in ("group", "supergroup"):
        from .services.team_match_service import team_match_service
        session = team_match_service.get_session(chat.id)
        if session:
            await team_score_command(update, context)
            return
    await soloscore_command(update, context)

def create_bot_application() -> Application:
    """Builds and registers only the active game commands requested."""
    request = HTTPXRequest(
        read_timeout=30.0,
        write_timeout=30.0,
        connect_timeout=30.0,
        pool_timeout=30.0
    )
    if not config.bot_token:
        raise ValueError("BOT_TOKEN must be configured before creating the Telegram application.")

    app = ApplicationBuilder().token(config.bot_token).request(request).build()

    # Core Navigation & Menus
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Match Creation & Solo Formats
    app.add_handler(CommandHandler("game", game_command))
    app.add_handler(CommandHandler("solo", solo_command))
    app.add_handler(CommandHandler("joinsolo", join_command))
    app.add_handler(CommandHandler("join", join_command))
    app.add_handler(CommandHandler("leavesolo", leave_command))
    app.add_handler(CommandHandler("leave", leave_command))
    app.add_handler(CommandHandler("extend", extend_command))
    app.add_handler(CommandHandler("forcestart", forcestart_command))
    app.add_handler(CommandHandler("endsolo", endsolo_command))
    app.add_handler(CommandHandler("restore", replay_command))
    app.add_handler(CommandHandler("replay", replay_command))
    app.add_handler(CommandHandler("soloscore", soloscore_command))

    # Team Match Commands
    app.add_handler(CommandHandler("team", team_command))
    app.add_handler(CommandHandler("teams", team_command))
    app.add_handler(CommandHandler("create_team", team_lobby_command))
    app.add_handler(CommandHandler("create_teams", team_lobby_command))
    app.add_handler(CommandHandler("setovers", set_overs_command))
    app.add_handler(CommandHandler("changeover", set_overs_command))
    app.add_handler(CommandHandler("toss", toss_command))
    app.add_handler(CommandHandler("batting", batting_command))
    app.add_handler(CommandHandler("bowling", bowling_command))
    app.add_handler(CommandHandler("forceadd", force_add_command))
    app.add_handler(CommandHandler("score", smart_score_command))
    app.add_handler(CommandHandler("teamscore", team_score_command))
    app.add_handler(CommandHandler("changecap", change_cap_command))
    app.add_handler(CommandHandler("changehost", change_host_command))
    app.add_handler(CommandHandler("spamfree", spamfree_command))
    app.add_handler(CommandHandler("endmatch", end_match_command))
    app.add_handler(CommandHandler("cancelteam", end_match_command))
    app.add_handler(CommandHandler("endteam", end_match_command))
    app.add_handler(CommandHandler("end_team", end_match_command))

    # Stats & Leaderboard Commands
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("profile", stats_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("top", leaderboard_command))

    # Owner & Admin Panel Commands
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("admin", owner_command))
    app.add_handler(CommandHandler("panel", owner_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("donate", donate_command))
    app.add_handler(CommandHandler("adddiamonds", donate_command))
    app.add_handler(CommandHandler("pay", donate_command))
    app.add_handler(CommandHandler("addrubies", addrubies_command))
    app.add_handler(CommandHandler("serverstats", owner_command))



    # Callback Query Dispatcher (Routing team vs solo callbacks)
    async def combined_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query:
            return
        data = query.data or ""
        if data.startswith("tbowl_") or data.startswith("team_") or data.startswith("setcap_") or data.startswith("tossdec_"):
            await team_callback_handler(update, context)
            return
        chat = update.effective_chat
        if chat:
            from .services.team_match_service import team_match_service
            if team_match_service.get_session(chat.id):
                await team_callback_handler(update, context)
                return
        await solo_callback_handler(update, context)

    app.add_handler(CallbackQueryHandler(combined_callback_handler))

    # Direct Text Replies (1-6 in chat)
    async def combined_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if chat and chat.type in ("group", "supergroup"):
            from .services.team_match_service import team_match_service
            if team_match_service.get_session(chat.id):
                await handle_team_chat_input(update, context)
                return
        await handle_chat_text_input(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, combined_text_handler))

    # Error Handler
    app.add_error_handler(error_handler)

    return app
