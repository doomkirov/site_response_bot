from pprint import pprint

from bot_operations.bot_support.keyboards import create_links_keyboard

links = ['abc','def']
awa = create_links_keyboard(links, 2)
pprint(awa.inline_keyboard)