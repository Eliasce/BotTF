import discord
from discord.ext import commands
from discord import app_commands

# Configuración básica (Esto se guardaría en un JSON en el host)
config = {
    "canal_envio": None,
    "canal_moderacion": None,
    "canal_memes": None,
    "rol_mod": None
}

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync() # Sincroniza los comandos /

bot = MyBot()

# --- COMANDO DE CONFIGURACIÓN ---
@bot.tree.command(name="configurar", description="Configura los canales del bot")
@app_commands.checks.has_permissions(administrator=True)
async def configurar(interaction: discord.Interaction, envio: discord.TextChannel, mod: discord.TextChannel, memes: discord.TextChannel):
    config["canal_envio"] = envio.id
    config["canal_moderacion"] = mod.id
    config["canal_memes"] = memes.id
    await interaction.response.send_message(f"✅ Configuración guardada:\nEnvíos: {envio.mention}\nModeración: {mod.mention}\nMemes: {memes.mention}", ephemeral=True)

# --- LÓGICA DE FILTRO INVISIBLE ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    if message.channel.id == config["canal_envio"]:
        # Verificamos si tiene imagen, video o link
        if message.attachments or "http" in message.content:
            canal_mod = bot.get_channel(config["canal_moderacion"])
            
            # Crear el panel para los moderadores
            embed = discord.Embed(title="Nuevo contenido para revisar", description=f"Enviado por: {message.author.mention}", color=discord.Color.blue())
            if message.attachments:
                embed.set_image(url=message.attachments[0].url)
            
            # Botones de Aprobación
            view = ApprovalView(message.author.id, message.content, message.attachments)
            
            await canal_mod.send(embed=embed, view=view)
            
            # Borrar el original para que sea invisible para los demás
            await message.delete()
            
            # Consejo Pro: Mensaje efímero (solo lo ve el autor)
            try:
                await message.author.send("¡Gracias! Tu meme ha sido enviado a los moderadores. Si es aprobado, aparecerá en el canal de memes pronto.")
            except:
                pass # Por si tiene MDs cerrados

# --- VISTA DE BOTONES ---
class ApprovalView(discord.ui.View):
    def __init__(self, author_id, content, attachments):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.content = content
        self.attachments = attachments

    @discord.ui.button(label="Aprobar", style=discord.ButtonStyle.green, custom_id="approve_btn")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal_memes = bot.get_channel(config["canal_memes"])
        
        # Enviar al canal de memes
        files = [await a.to_file() for a in self.attachments]
        await canal_memes.send(content=f"Meme enviado por <@{self.author_id}>\n{self.content}", files=files)
        
        await interaction.response.edit_message(content="✅ Aprobado y publicado.", embed=None, view=None)

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, custom_id="deny_btn")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Rechazado.", embed=None, view=None)

bot.run("MTUwNDU1NzIwOTI4NjA4MjY0MA.GC-JYE.7n_V4YglplztG-GJQg0vlA2L066qr-Dv8OZ7i4")