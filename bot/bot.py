from variables import Varibles
db = Varibles()

from config import MSG
from aiogram import executor
from dispatcher import dp
import handlers

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True) # Don't skip updates, if your bot will process payments or other important stuff
    MSG = '👋 The session is over.\nWith ❤️ AlyExpress™'

print(MSG)
