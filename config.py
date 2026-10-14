import os
from dataclasses import dataclass, field
from typing import List

# Load environment variables safely
def _load_env_file():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        for path in [".env", "../.env", "../../.env"]:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
                    break
                except Exception:
                    pass

_load_env_file()

@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///gullycric.db")
    owner_ids: List[int] = field(default_factory=lambda: [
        int(x.strip()) for x in os.getenv("OWNER_IDS", "8445198778").split(",") if x.strip().isdigit()
    ])
    # IMPORTANT: Part 3 - 3-Ball Default Behavior as observed in screen recording
    default_solo_balls_per_over: int = int(os.getenv("DEFAULT_SOLO_BALLS_PER_OVER", "3"))
    default_solo_overs: int = int(os.getenv("DEFAULT_SOLO_OVERS", "1"))
    
    # Team match defaults
    default_team_balls_per_over: int = int(os.getenv("DEFAULT_TEAM_BALLS_PER_OVER", "6"))
    default_team_overs: int = int(os.getenv("DEFAULT_TEAM_OVERS", "2"))
    
    # Timers
    afk_timeout_seconds: int = int(os.getenv("AFK_TIMEOUT_SECONDS", "50"))
    lobby_timeout_seconds: int = int(os.getenv("LOBBY_TIMEOUT_SECONDS", "120"))
    
    # Media
    enable_media: bool = os.getenv("ENABLE_MEDIA", "true").lower() in ("true", "1", "yes")
    media_base_url: str = os.getenv("MEDIA_BASE_URL", "")

config = Config()
