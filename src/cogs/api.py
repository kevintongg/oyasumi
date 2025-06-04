import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
import aiohttp
import random


class API(commands.Cog):
    """Commands that use external APIs"""

    def __init__(self, bot):
        self.bot = bot

    async def language_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete function for translation languages"""
        languages = [
            'english', 'spanish', 'french', 'german', 'italian', 'portuguese', 'russian',
            'japanese', 'chinese', 'korean', 'arabic', 'hindi', 'dutch', 'swedish',
            'norwegian', 'danish', 'finnish', 'polish', 'turkish', 'greek', 'hebrew',
            'thai', 'vietnamese', 'czech', 'hungarian', 'auto'
        ]

        # Filter based on current input
        if current:
            filtered_langs = [lang for lang in languages if current.lower() in lang.lower()]
        else:
            filtered_langs = languages

        # Return as app_commands.Choice objects (max 25)
        return [
            app_commands.Choice(name=lang.title(), value=lang)
            for lang in sorted(filtered_langs)[:25]
        ]

    @app_commands.command(name='crypto', description='Get cryptocurrency price information')
    @app_commands.describe(coin='Cryptocurrency name or symbol (e.g., "bitcoin", "ethereum", "btc", "eth")')
    async def crypto_price(self, interaction: discord.Interaction, coin: str):
        """Get cryptocurrency price and information"""
        await interaction.response.defer()

        # Clean up the coin input
        coin = coin.lower().strip()

        try:
            async with aiohttp.ClientSession() as session:
                # First, search for the coin to get the correct ID
                search_url = f"https://api.coingecko.com/api/v3/search?query={coin}"

                async with session.get(search_url) as response:
                    if response.status == 200:
                        search_data = await response.json()
                        coins = search_data.get('coins', [])

                        if not coins:
                            await interaction.followup.send(f"❌ Cryptocurrency '{coin}' not found. Try using the full name or common symbol (e.g., 'bitcoin', 'ethereum', 'btc', 'eth').")
                            return

                        # Get the first match (most relevant)
                        coin_id = coins[0]['id']
                        coin_name = coins[0]['name']
                        coin_symbol = coins[0]['symbol'].upper()

                        # Get detailed price information
                        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"

                        async with session.get(price_url) as price_response:
                            if price_response.status == 200:
                                price_data = await price_response.json()

                                if coin_id not in price_data:
                                    await interaction.followup.send("❌ Price data not available for this cryptocurrency.")
                                    return

                                data = price_data[coin_id]

                                # Format price
                                price = data['usd']
                                if price >= 1:
                                    price_str = f"${price:,.2f}"
                                elif price >= 0.01:
                                    price_str = f"${price:.4f}"
                                else:
                                    price_str = f"${price:.8f}"

                                # Format market cap
                                market_cap = data.get('usd_market_cap')
                                if market_cap:
                                    if market_cap >= 1e12:
                                        market_cap_str = f"${market_cap/1e12:.2f}T"
                                    elif market_cap >= 1e9:
                                        market_cap_str = f"${market_cap/1e9:.2f}B"
                                    elif market_cap >= 1e6:
                                        market_cap_str = f"${market_cap/1e6:.2f}M"
                                    else:
                                        market_cap_str = f"${market_cap:,.0f}"
                                else:
                                    market_cap_str = "N/A"

                                # Format 24h volume
                                volume = data.get('usd_24h_vol')
                                if volume:
                                    if volume >= 1e9:
                                        volume_str = f"${volume/1e9:.2f}B"
                                    elif volume >= 1e6:
                                        volume_str = f"${volume/1e6:.2f}M"
                                    else:
                                        volume_str = f"${volume:,.0f}"
                                else:
                                    volume_str = "N/A"

                                # 24h change
                                change_24h = data.get('usd_24h_change', 0)
                                change_emoji = "📈" if change_24h >= 0 else "📉"
                                change_color = discord.Color.green() if change_24h >= 0 else discord.Color.red()

                                embed = discord.Embed(
                                    title=f"💰 {coin_name} ({coin_symbol})",
                                    color=change_color,
                                    timestamp=datetime.now(timezone.utc)
                                )

                                embed.add_field(name="💵 Price", value=price_str, inline=True)
                                embed.add_field(name=f"{change_emoji} 24h Change", value=f"{change_24h:+.2f}%", inline=True)
                                embed.add_field(name="📊 Market Cap", value=market_cap_str, inline=True)
                                embed.add_field(name="📈 24h Volume", value=volume_str, inline=True)

                                # Add trend indicator
                                if abs(change_24h) >= 10:
                                    trend = "🚀 Mooning!" if change_24h > 0 else "💥 Crashing!"
                                elif abs(change_24h) >= 5:
                                    trend = "📈 Strong move" if change_24h > 0 else "📉 Strong drop"
                                else:
                                    trend = "📊 Stable"

                                embed.add_field(name="🎯 Trend", value=trend, inline=True)

                                # Add disclaimer
                                embed.add_field(name="⚠️ Disclaimer", value="This is not financial advice. DYOR!", inline=False)

                                embed.set_footer(text=f"Requested by {interaction.user} • Data from CoinGecko", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

                                await interaction.followup.send(embed=embed)
                            else:
                                await interaction.followup.send("❌ Failed to fetch price data. Please try again later.")
                    else:
                        await interaction.followup.send("❌ Failed to search for cryptocurrency. Please try again later.")

        except Exception as e:
            await interaction.followup.send("❌ Error fetching cryptocurrency data. Please try again later.")

    @app_commands.command(name='translate', description='Translate text to another language')
    @app_commands.describe(
        text='The text to translate',
        target_language='Target language (e.g., "spanish", "french", "japanese", "auto" to detect)'
    )
    @app_commands.autocomplete(target_language=language_autocomplete)
    async def translate_text(self, interaction: discord.Interaction, text: str, target_language: str = "english"):
        """Translate text using MyMemory API"""
        if len(text) > 500:
            await interaction.response.send_message("❌ Text too long! Maximum 500 characters.", ephemeral=True)
            return

        await interaction.response.defer()

        # Enhanced language code mapping (MyMemory uses ISO codes)
        language_map = {
            'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de', 'italian': 'it',
            'portuguese': 'pt', 'russian': 'ru', 'japanese': 'ja', 'chinese': 'zh-cn', 'korean': 'ko',
            'arabic': 'ar', 'hindi': 'hi', 'dutch': 'nl', 'swedish': 'sv', 'norwegian': 'no',
            'danish': 'da', 'finnish': 'fi', 'polish': 'pl', 'turkish': 'tr', 'greek': 'el',
            'hebrew': 'he', 'thai': 'th', 'vietnamese': 'vi', 'czech': 'cs', 'hungarian': 'hu',
            'auto': 'auto'
        }

        # Get language code
        target_lang = target_language.lower()
        if target_lang not in language_map:
            await interaction.followup.send(
                f"❌ Unsupported language: `{target_language}`\n"
                f"**Supported languages:** {', '.join(language_map.keys())}",
                ephemeral=True
            )
            return

        target_code = language_map[target_lang]

        # Simple language detection based on character patterns
        def detect_language(text):
            # Check for common patterns
            if any('\u4e00' <= char <= '\u9fff' for char in text):  # Chinese characters
                return 'zh-cn'
            elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):  # Japanese
                return 'ja'
            elif any('\uac00' <= char <= '\ud7af' for char in text):  # Korean
                return 'ko'
            elif any('\u0600' <= char <= '\u06ff' for char in text):  # Arabic
                return 'ar'
            elif any('\u0900' <= char <= '\u097f' for char in text):  # Hindi
                return 'hi'
            elif any('\u0400' <= char <= '\u04ff' for char in text):  # Cyrillic (Russian)
                return 'ru'
            else:
                # Try to detect common European languages by patterns
                text_lower = text.lower()

                # French detection (improved)
                french_patterns = ['ici', 'est', 'c\'est', 'le ', 'la ', 'les ', 'des ', 'dans', 'avec', 'pour', 'sur', 'par', 'sans', 'sous', 'entre']
                if any(pattern in text_lower for pattern in french_patterns):
                    return 'fr'

                # Spanish detection
                spanish_patterns = ['el ', 'la ', 'los ', 'las ', 'es ', 'en ', 'de ', 'del ', 'con', 'por', 'para', 'desde', 'hasta', 'donde', 'que']
                if any(pattern in text_lower for pattern in spanish_patterns):
                    return 'es'

                # German detection
                german_patterns = ['der ', 'die ', 'das ', 'ist ', 'und ', 'mit ', 'von ', 'zu ', 'auf ', 'für ', 'bei', 'nach', 'über', 'unter']
                if any(pattern in text_lower for pattern in german_patterns):
                    return 'de'

                # Italian detection
                italian_patterns = ['il ', 'la ', 'gli ', 'le ', 'è ', 'di ', 'del ', 'con ', 'per ', 'da ', 'in ', 'su ', 'tra', 'fra']
                if any(pattern in text_lower for pattern in italian_patterns):
                    return 'it'

                # Portuguese detection
                portuguese_patterns = ['o ', 'a ', 'os ', 'as ', 'é ', 'de ', 'do ', 'da ', 'com ', 'para ', 'por ', 'em ', 'no ', 'na']
                if any(pattern in text_lower for pattern in portuguese_patterns):
                    return 'pt'

                # English detection (last, as fallback)
                english_patterns = ['the ', 'and ', 'is ', 'are ', 'you ', 'this ', 'that ', 'with ', 'for ', 'from ', 'to ', 'of ', 'in ', 'on ', 'at']
                if any(pattern in text_lower for pattern in english_patterns):
                    return 'en'

                # If no patterns match, try to guess based on common letter frequencies
                if 'ç' in text_lower or 'ñ' in text_lower:
                    return 'es' if 'ñ' in text_lower else 'fr'
                elif 'ä' in text_lower or 'ö' in text_lower or 'ü' in text_lower:
                    return 'de'
                elif 'à' in text_lower or 'è' in text_lower or 'ù' in text_lower:
                    return 'it'
                elif 'ã' in text_lower or 'õ' in text_lower:
                    return 'pt'

                return 'en'  # Default to English if unsure

        # Detect source language
        detected_source = detect_language(text)

        try:
            async with aiohttp.ClientSession() as session:
                # MyMemory API endpoint with explicit language pair
                url = "https://api.mymemory.translated.net/get"
                params = {
                    'q': text,
                    'langpair': f'{detected_source}|{target_code}' if target_code != 'auto' else f'{detected_source}|en'
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data['responseStatus'] == 200:
                            translated_text = data['responseData']['translatedText']

                            # Find language names from codes
                            source_name = next((name for name, code in language_map.items() if code == detected_source), detected_source)

                            embed = discord.Embed(
                                title="🌐 Translation",
                                color=discord.Color.blue(),
                                timestamp=datetime.now(timezone.utc)
                            )

                            embed.add_field(name="📝 Original", value=f"```{text}```", inline=False)
                            embed.add_field(name="✨ Translation", value=f"```{translated_text}```", inline=False)
                            embed.add_field(name="🔍 Detected Language", value=source_name.title(), inline=True)
                            embed.add_field(name="🎯 Target Language", value=target_language.title(), inline=True)
                            embed.add_field(name="🔧 Language Pair", value=f"{detected_source}→{target_code}", inline=True)

                            embed.set_footer(text=f"Requested by {interaction.user} • Powered by MyMemory", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

                            await interaction.followup.send(embed=embed)
                        else:
                            # More detailed error information
                            error_msg = data.get('responseDetails', 'Unknown error')
                            await interaction.followup.send(
                                f"❌ Translation failed.\n"
                                f"**Error:** {error_msg}\n"
                                f"**Language pair tried:** {detected_source}→{target_code}\n"
                                f"**Tip:** Try a different target language or simpler text."
                            )
                    else:
                        await interaction.followup.send(f"❌ Translation service unavailable (HTTP {response.status}). Please try again later.")

        except Exception as e:
            await interaction.followup.send(f"❌ Error during translation: {str(e)}")

    @app_commands.command(name='meme', description='Get a random meme from Reddit')
    async def random_meme(self, interaction: discord.Interaction):
        """Get a random meme from popular subreddits"""
        await interaction.response.defer()

        # List of meme subreddits
        subreddits = ['memes', 'dankmemes', 'wholesomememes', 'programmerhumor', 'funny']

        try:
            async with aiohttp.ClientSession() as session:
                # Try each subreddit until we get a good meme
                for subreddit in subreddits:
                    try:
                        url = f'https://www.reddit.com/r/{subreddit}/hot.json?limit=50'
                        headers = {'User-Agent': 'DiscordBot:OyasumiBot:v1.0 (by /u/discordbot)'}

                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                posts = data['data']['children']

                                # Filter for image posts that aren't videos or galleries
                                image_posts = [
                                    post['data'] for post in posts
                                    if not post['data'].get('is_video', False)
                                    and post['data'].get('url', '').lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
                                    and not post['data'].get('over_18', False)  # No NSFW
                                    and not post['data'].get('spoiler', False)   # No spoilers
                                ]

                                if image_posts:
                                    meme = random.choice(image_posts)

                                    embed = discord.Embed(
                                        title=f"😂 {meme['title'][:250]}",  # Limit title length
                                        url=f"https://reddit.com{meme['permalink']}",
                                        color=discord.Color.orange(),
                                        timestamp=datetime.now(timezone.utc)
                                    )
                                    embed.set_image(url=meme['url'])
                                    embed.add_field(name="👍 Upvotes", value=meme['ups'], inline=True)
                                    embed.add_field(name="💬 Comments", value=meme['num_comments'], inline=True)
                                    embed.add_field(name="📱 Subreddit", value=f"r/{meme['subreddit']}", inline=True)
                                    embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

                                    await interaction.followup.send(embed=embed)
                                    return
                    except Exception as e:
                        continue  # Try next subreddit

                # If we get here, no memes were found
                await interaction.followup.send("😅 Couldn't fetch a meme right now. Reddit might be having issues. Try again later!")

        except Exception as e:
            await interaction.followup.send("❌ Error fetching meme. Please try again later.")


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(API(bot))
