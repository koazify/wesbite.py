import discord
from discord.ext import tasks, commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import datetime
import os
import time
import random
import string

TOKEN = "authtokens_MTM5MjkxNDQzOTI2Njc2NzAwOQ.GSa1Nx.iQf5c4274Dwc00mBKQmFBzhZNDkmE84E7ddmuo"
TOKEN = TOKEN.split("_", 1)[1]
CHANNEL_ID = 1386901509974917151

URL = "https://www.meta.com/experiences/animal-company/7190422614401072/"
CSS_SELECTOR = "div.xeuugli.x2lwn1j.x78zum5.x19xhxss.xx6i8ya.xie8wau.x1r0jzty.x17zd0t2.x1a02dak"
HISTORY_FILE = "update-history.json"
STATUS_FILE = "status.json"

start_time = time.time()

def write_status(is_online: bool):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "lastOnline": is_online,
            "lastSeen": datetime.utcnow().isoformat() + "Z"
        }, f)

class UpdateTrackerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.last_version = None
        self.update_history = []
        if os.path.isfile(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    self.update_history = json.load(f)
                    if self.update_history:
                        self.last_version = self.update_history[-1]['version']
                except json.JSONDecodeError:
                    self.update_history = []

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        write_status(True)
        if not self.check_version.is_running():
            self.check_version.start()

    async def on_disconnect(self):
        write_status(False)

    def fetch_version(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager(version="138.0.7204.92").install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(URL)
        driver.implicitly_wait(5)
        try:
            elem = driver.find_element(By.CSS_SELECTOR, CSS_SELECTOR)
            version = elem.text.strip()
        except Exception as e:
            version = None
            print(f"Failed to find version element: {e}")
        driver.quit()
        return version

    async def perform_update_check(self, manual=False, ctx=None):
        version = self.fetch_version()
        if not version:
            msg = "Could not fetch version."
            if manual and ctx:
                await ctx.send(f"❌ {msg}")
            print(msg)
            return
        if version != self.last_version:
            self.last_version = version
            update_entry = {
                "version": version,
                "date": datetime.utcnow().isoformat() + "Z"
            }
            self.update_history.append(update_entry)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.update_history, f, indent=4)
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title="Animal Company Update Detected!",
                    description=f"A new update has been found: **{version}**",
                    color=0x00bfff
                )
                embed.set_footer(text="Auto-update powered by Animal Tracker Bot")
                await channel.send(embed=embed)
                print(f"Update sent: {version}")
        else:
            print("No new update.")
            if manual and ctx:
                await ctx.send(f"✅ Checked: No new update. Current version is still **{version}**")

    @tasks.loop(minutes=1)
    async def check_version(self):
        await self.perform_update_check()

bot = UpdateTrackerBot()

@bot.command(name="checknow")
async def checknow_command(ctx):
    await ctx.send("🔍 Checking for updates...")
    await bot.perform_update_check(manual=True, ctx=ctx)

@bot.command(name="uptime")
async def uptime_command(ctx):
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(f"⏱ Bot has been running for: **{hours}h {minutes}m {seconds}s**")

if __name__ == "__main__":
    write_status(True)
    bot.run(TOKEN)
