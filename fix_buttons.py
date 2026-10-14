
import re

file_path = '/app/applet/gullycric/src/handlers/solo.py'

with open(file_path, 'r') as f:
    content = f.read()

content = content.replace('InlineKeyboardButton("{emojis.BAT} Join Solo"', 'InlineKeyboardButton(f"{emojis.BAT_SYM} Join Solo"')
content = content.replace('InlineKeyboardButton("{emojis.CROSS} Leave"', 'InlineKeyboardButton(f"{emojis.CROSS_SYM} Leave"')
content = content.replace('InlineKeyboardButton("{emojis.BALL} Open bowling DM"', 'InlineKeyboardButton(f"{emojis.BALL_SYM} Open bowling DM"')
content = content.replace('InlineKeyboardButton("PLAY AGAIN {emojis.REFRESH}"', 'InlineKeyboardButton(f"PLAY AGAIN {emojis.REFRESH_SYM}"')
content = content.replace('InlineKeyboardButton(f"{emojis.CHECK} Accept', 'InlineKeyboardButton(f"{emojis.CHECK_SYM} Accept')
content = content.replace('InlineKeyboardButton("{emojis.CROSS} Deny"', 'InlineKeyboardButton(f"{emojis.CROSS_SYM} Deny"')
content = content.replace('InlineKeyboardButton("{emojis.CHECK} Yes, End Match"', 'InlineKeyboardButton(f"{emojis.CHECK_SYM} Yes, End Match"')
content = content.replace('InlineKeyboardButton("{emojis.CROSS} No, Keep Playing"', 'InlineKeyboardButton(f"{emojis.CROSS_SYM} No, Keep Playing"')

with open(file_path, 'w') as f:
    f.write(content)
