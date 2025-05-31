import discord
from discord.ext import commands
import logging
import json
from botToken import TOKEN  # Tuo token erillisestä tiedostosta

# Lokituksen konfiguraatio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Lataa asetukset tiedostosta
def load_settings():
    try:
        with open('asetukset.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("asetukset.json tiedostoa ei löytynyt.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Virhe luettaessa asetuksia: {e}")
        return {}

settings = load_settings()

# Asetetaan botin komento-prefiksi
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Ilmoitustoiminto, joka lähettää viestin kanavalle, kun joku liittyy puhekanavalle
@client.event
async def on_ready():
    logging.info(f"{client.user} on nyt käynnissä!")

    for guild_id, guild_settings in settings.get("kanavat", {}).items():
        ilmoituskanava_id = guild_settings.get("ilmoituskanava_id")
        ilmoituskanava = client.get_channel(ilmoituskanava_id)
        
        if ilmoituskanava is not None:
            await ilmoituskanava.send(f"Botti on käynnissä palvelimella {guild_id}.")
        else:
            logging.warning(f"Ilmoituskanavaa ei löytynyt palvelimella {guild_id}. Tarkista asetukset.")

# Ilmoittaa, kun joku liittyy puhekanavalle
@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if member.bot:  # Jos kanavalle liittyy botti, älä tee mitään
            return

        # Hae palvelimen ID ja liittyvän puhekanavan nimi
        guild_id = str(after.channel.guild.id)
        puhekanava_nimi = after.channel.name

        # Hae palvelimen asetukset
        guild_settings = settings.get("kanavat", {}).get(guild_id)

        if guild_settings:
            # Hae ilmoituskanavan ID asetuksista
            ilmoituskanava_id = guild_settings.get("ilmoituskanava_id")
            ilmoituskanava = client.get_channel(ilmoituskanava_id)

            if ilmoituskanava:
                message = f'Jahas, {member.name} on liittynyt puhekanavalle {puhekanava_nimi}.'
                await ilmoituskanava.send(message)
                logging.info(f"Ilmoitus lähetetty: {message}")
            else:
                logging.warning(f"Ilmoituskanavaa ei löytynyt palvelimelta {guild_id}.")
        else:
            logging.warning(f"Asetuksia ei löytynyt palvelimelle {guild_id}.")

# Käynnistä botti
def run_discord_bot():
    client.run(TOKEN)  # Käytä tuotu TOKEN

# Suorita botti
run_discord_bot()

