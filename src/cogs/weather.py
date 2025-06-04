import os
import aiohttp
from datetime import datetime, timezone, timedelta
import discord
from discord import app_commands
from discord.ext import commands


class WeatherView(discord.ui.View):
    """Interactive view for weather command with buttons"""

    def __init__(self, weather_data, location_name, country, state, bot):
        super().__init__(timeout=300)  # 5 minute timeout
        self.weather_data = weather_data
        self.location_name = location_name
        self.country = country
        self.state = state
        self.bot = bot
        self.current_unit = 'metric'  # metric or imperial
        self.current_view = 'current'  # current, hourly, daily, details, activities, air_quality

    @discord.ui.button(label='°F/°C', style=discord.ButtonStyle.secondary, emoji='🌡️')
    async def toggle_units(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle between Celsius and Fahrenheit"""
        self.current_unit = 'imperial' if self.current_unit == 'metric' else 'metric'
        embed = await self.create_weather_embed(self.current_view)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Current', style=discord.ButtonStyle.success, emoji='🌤️')
    async def show_current(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show current weather"""
        self.current_view = 'current'
        embed = await self.create_weather_embed('current')
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Hourly', style=discord.ButtonStyle.primary, emoji='⏰')
    async def show_hourly(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show hourly forecast"""
        self.current_view = 'hourly'
        embed = await self.create_weather_embed('hourly')
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Daily', style=discord.ButtonStyle.primary, emoji='📅')
    async def show_daily(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show daily forecast"""
        self.current_view = 'daily'
        embed = await self.create_weather_embed('daily')
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Details', style=discord.ButtonStyle.secondary, emoji='📊')
    async def show_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed weather information"""
        self.current_view = 'details'
        embed = await self.create_weather_embed('details')
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Activities', style=discord.ButtonStyle.secondary, emoji='🎯', row=1)
    async def show_activities(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show activity recommendations"""
        self.current_view = 'activities'
        embed = await self.create_weather_embed('activities')
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Air Quality', style=discord.ButtonStyle.secondary, emoji='💨', row=1)
    async def show_air_quality(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show air quality information"""
        self.current_view = 'air_quality'
        embed = await self.create_weather_embed('air_quality')
        await interaction.response.edit_message(embed=embed, view=self)

    async def create_weather_embed(self, view_type):
        """Create weather embed based on view type"""
        weather_cog = self.bot.get_cog('Weather')
        if view_type == 'hourly':
            return await weather_cog.create_hourly_embed(self.weather_data, self.location_name, self.country, self.state, self.current_unit)
        elif view_type == 'air_quality':
            return await weather_cog.create_air_quality_embed(self.weather_data, self.location_name, self.country, self.state)
        elif view_type == 'daily':
            return await weather_cog.create_daily_embed(self.weather_data, self.location_name, self.country, self.state, self.current_unit)
        elif view_type == 'details':
            return await weather_cog.create_details_embed(self.weather_data, self.location_name, self.country, self.state, self.current_unit)
        elif view_type == 'activities':
            return await weather_cog.create_activities_embed(self.weather_data, self.location_name, self.country, self.state, self.current_unit)
        else:  # current
            return await weather_cog.create_weather_embed(self.weather_data, self.location_name, self.country, self.state, self.current_unit)


class Weather(commands.Cog):
    """Weather and atmospheric information commands"""

    def __init__(self, bot):
        self.bot = bot
        self.owm_api_key = os.getenv('OWM_API_KEY')

    def truncate_field_value(self, text, max_length=1020):
        """Truncate text to fit Discord's embed field value limit"""
        if len(text) <= max_length:
            return text

        # Truncate at word boundary if possible
        truncated = text[:max_length-15]  # Leave room for "... [truncated]"
        if ' ' in truncated:
            truncated = truncated.rsplit(' ', 1)[0]

        return f"{truncated}... [truncated]"

    @app_commands.command(name='weather', description='Get comprehensive weather information for a location')
    @app_commands.describe(location='City name, state/country (e.g., "London, UK" or "New York, NY")')
    async def weather(self, interaction: discord.Interaction, location: str):
        """Get comprehensive weather information for a location with interactive features"""
        if not self.owm_api_key:
            await interaction.response.send_message(
                "❌ Weather service is not configured. Please contact the bot owner.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            # Step 1: Get coordinates from location name using Geocoding API
            geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                'q': location,
                'limit': 1,
                'appid': self.owm_api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(geocoding_url, params=geocoding_params) as geo_response:
                    if geo_response.status != 200:
                        await interaction.followup.send("❌ Error accessing weather service. Please try again later.")
                        return

                    geo_data = await geo_response.json()

                    if not geo_data:
                        await interaction.followup.send(f"❌ Location '{location}' not found. Please try a different location.")
                        return

                    lat = geo_data[0]['lat']
                    lon = geo_data[0]['lon']
                    location_name = geo_data[0]['name']
                    country = geo_data[0].get('country', '')
                    state = geo_data[0].get('state', '')

                # Step 2: Get weather data using One Call 3.0 API
                weather_url = f"https://api.openweathermap.org/data/3.0/onecall"
                weather_params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.owm_api_key,
                    'units': 'metric',
                    'exclude': 'minutely'
                }

                async with session.get(weather_url, params=weather_params) as weather_response:
                    if weather_response.status != 200:
                        await interaction.followup.send("❌ Error fetching weather data. Please try again later.")
                        return

                    weather_data = await weather_response.json()

                # Step 3: Get air quality data
                air_quality_url = f"http://api.openweathermap.org/data/2.5/air_pollution"
                air_params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.owm_api_key
                }

                try:
                    async with session.get(air_quality_url, params=air_params) as air_response:
                        if air_response.status == 200:
                            air_data = await air_response.json()
                            weather_data['air_quality'] = air_data
                except:
                    pass  # Air quality is optional

            # Create interactive weather embed with buttons
            embed = await self.create_weather_embed(weather_data, location_name, country, state)
            view = WeatherView(weather_data, location_name, country, state, self.bot)

            await interaction.followup.send(embed=embed, view=view)

        except aiohttp.ClientError:
            await interaction.followup.send("❌ Network error occurred. Please try again later.")
        except Exception as e:
            self.bot.logger.error(f"Weather command error: {e}", exc_info=True)
            await interaction.followup.send("❌ An unexpected error occurred while fetching weather data.")

    def get_local_time(self, timestamp, timezone_offset):
        """Convert UTC timestamp to local time using timezone offset"""
        utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        local_time = utc_time + timedelta(seconds=timezone_offset)
        return local_time

    def convert_temp(self, temp_celsius, unit='metric'):
        """Convert temperature to the specified unit"""
        if unit == 'imperial':
            return round(temp_celsius * 9/5 + 32)
        return round(temp_celsius)

    def get_temp_unit(self, unit='metric'):
        """Get temperature unit symbol"""
        return '°F' if unit == 'imperial' else '°C'

    def convert_speed(self, speed_ms, unit='metric'):
        """Convert wind speed to appropriate unit"""
        if unit == 'imperial':
            return round(speed_ms * 2.237, 1)  # m/s to mph
        return round(speed_ms * 3.6, 1)  # m/s to km/h

    def get_speed_unit(self, unit='metric'):
        """Get speed unit"""
        return 'mph' if unit == 'imperial' else 'km/h'

    async def create_weather_embed(self, data, location_name, country, state, unit='metric'):
        """Create streamlined current weather embed focused on immediate practical info"""
        current = data['current']
        daily = data['daily']
        timezone_offset = data['timezone_offset']

        location_str = location_name
        if state:
            location_str += f", {state}"
        if country:
            location_str += f", {country}"

        # Temperature-based embed color
        temp_celsius = current['temp']
        embed_color = self.get_temperature_color(temp_celsius)

        temp = self.convert_temp(temp_celsius, unit)
        temp_unit = self.get_temp_unit(unit)
        feels_like = self.convert_temp(current['feels_like'], unit)

        # Main weather description
        weather_main = current['weather'][0]['main']
        weather_desc = current['weather'][0]['description']
        weather_emoji = self.get_weather_emoji(current['weather'][0]['id'])

        embed = discord.Embed(
            title=f"{weather_emoji} Current Weather",
            description=f"📍 **{location_str}**\n{weather_desc.title()}",
            color=embed_color,
            timestamp=datetime.now(timezone.utc)
        )

        # Current temperature with context
        temp_text = f"**{temp}{temp_unit}**"
        if abs(temp_celsius - current['feels_like']) > 1:
            temp_text += f" (feels like {feels_like}{temp_unit})"

        # Add smart clothing recommendation
        clothing_rec = self.get_clothing_recommendation(temp_celsius, current['weather'][0]['id'], current.get('wind_speed', 0))
        if clothing_rec:
            temp_text += f"\n👕 *{clothing_rec}*"

        embed.add_field(
            name="🌡️ Temperature",
            value=temp_text,
            inline=True
        )

        # Wind information
        wind_speed_raw = current.get('wind_speed', 0)
        wind_speed = self.convert_speed(wind_speed_raw, unit)
        speed_unit = self.get_speed_unit(unit)

        wind_text = f"Speed: {wind_speed} {speed_unit}"

        if 'wind_deg' in current:
            wind_dir = self.get_wind_direction(current['wind_deg'])
            wind_text += f"\nDirection: {wind_dir}"

        if 'wind_gust' in current:
            wind_gust = self.convert_speed(current['wind_gust'], unit)
            wind_text += f"\nGusts: {wind_gust} {speed_unit}"

        embed.add_field(
            name="💨 Wind",
            value=wind_text,
            inline=True
        )

        # Basic atmosphere info
        humidity = current['humidity']
        pressure = current['pressure']

        # Add pressure trend context
        pressure_trend = self.get_pressure_trend(pressure)
        atm_text = f"Humidity: {humidity}%\nPressure: {pressure} hPa {pressure_trend['emoji']}"
        if pressure_trend['context']:
            atm_text += f"\n*{pressure_trend['context']}*"

        embed.add_field(
            name="💧 Atmosphere",
            value=atm_text,
            inline=True
        )

        # UV Index
        uv_index = current.get('uvi', 0)
        uv_risk = self.get_uv_risk_level(uv_index)
        visibility = current.get('visibility', 0) / 1000 if 'visibility' in current else None

        uv_text = f"UV Index: {uv_index} ({uv_risk})"
        if visibility:
            uv_text += f"\nVisibility: {visibility:.1f} km"

        # Add UV timing advice
        if uv_index > 3:
            uv_text += f"\n☂️ *Use sun protection*"

        embed.add_field(
            name="☀️ UV & Visibility",
            value=uv_text,
            inline=True
        )

        # Precipitation (if any)
        if 'rain' in current or 'snow' in current:
            precip_text = ""
            if 'rain' in current:
                rain_1h = current['rain'].get('1h', 0)
                precip_text += f"Rain: {rain_1h}mm/h"
            if 'snow' in current:
                snow_1h = current['snow'].get('1h', 0)
                if precip_text:
                    precip_text += "\n"
                precip_text += f"Snow: {snow_1h}mm/h"

            embed.add_field(
                name="🌧️ Precipitation",
                value=precip_text,
                inline=True
            )

        # Today's forecast with context
        today = daily[0]
        temp_max = self.convert_temp(today['temp']['max'], unit)
        temp_min = self.convert_temp(today['temp']['min'], unit)
        pop = int(today.get('pop', 0) * 100)  # Probability of precipitation

        outlook_text = f"High: {temp_max}{temp_unit}\nLow: {temp_min}{temp_unit}\nRain chance: {pop}%"

        # Add day context
        if pop > 60:
            outlook_text += "\n☔ *Expect rain today*"
        elif pop > 30:
            outlook_text += "\n🌦️ *Possible showers*"

        embed.add_field(
            name="📊 Today's Outlook",
            value=outlook_text,
            inline=True
        )

        # Weather alerts (if any) - IMPORTANT: Keep safety info here
        if 'alerts' in data and data['alerts']:
            alert = data['alerts'][0]
            alert_text = f"⚠️ **{alert['event']}**\n{alert['description']}"

            # Ensure alert text doesn't exceed Discord's 1024 character limit
            if len(alert_text) > 1020:  # Leave some buffer
                # Truncate description but keep event name
                max_desc_length = 1020 - len(f"⚠️ **{alert['event']}**\n") - 10  # 10 chars for "... [more]"
                truncated_desc = alert['description'][:max_desc_length]

                # Try to break at a sentence or word boundary
                if '.' in truncated_desc:
                    truncated_desc = truncated_desc.rsplit('.', 1)[0] + '.'
                elif ' ' in truncated_desc:
                    truncated_desc = truncated_desc.rsplit(' ', 1)[0]

                alert_text = f"⚠️ **{alert['event']}**\n{truncated_desc}... [more details available]"

            embed.add_field(
                name="🚨 Weather Alert",
                value=alert_text,
                inline=False
            )

        # Check for severe weather conditions even without official alerts
        severe_conditions = self.detect_severe_weather(current, daily[0])
        if severe_conditions and 'alerts' not in data:
            embed.add_field(
                name="⚠️ Conditions Notice",
                value=self.truncate_field_value(severe_conditions),
                inline=False
            )

        # Footer with local time
        local_time = self.get_local_time(current['dt'], timezone_offset)
        embed.set_footer(
            text=f"🕒 {location_name} local time: {local_time.strftime('%H:%M')} • Use buttons for more details",
            icon_url="https://openweathermap.org/img/wn/10d@2x.png"
        )

        # Add activity recommendations based on current conditions
        activity_rec = self.get_current_activity_recommendation(
            temp_celsius, current['weather'][0]['id'], current.get('wind_speed', 0),
            uv_index, current['humidity'], daily[0].get('pop', 0)
        )
        if activity_rec:
            embed.add_field(
                name="🎯 Activity Suggestions",
                value=self.truncate_field_value(activity_rec),
                inline=False
            )

        # Footer with additional info and local time
        local_time = self.get_local_time(current['dt'], timezone_offset)
        embed.set_footer(
            text=f"🕒 {location_name} local time: {local_time.strftime('%H:%M')} • Last updated: {datetime.now(timezone.utc).strftime('%H:%M')} UTC",
            icon_url="https://openweathermap.org/img/wn/10d@2x.png"
        )

        return embed

    async def create_hourly_embed(self, data, location_name, country, state, unit='metric'):
        """Create enhanced hourly forecast embed with feels-like temps and wind"""
        hourly = data['hourly'][:12]  # Next 12 hours
        timezone_offset = data['timezone_offset']

        location_str = location_name
        if state:
            location_str += f", {state}"
        if country:
            location_str += f", {country}"

        embed = discord.Embed(
            title="⏰ 12-Hour Forecast",
            description=f"📍 **{location_str}**",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )

        forecast_text = ""
        temp_unit = self.get_temp_unit(unit)
        speed_unit = self.get_speed_unit(unit)

        for i, hour in enumerate(hourly):
            hour_time = self.get_local_time(hour['dt'], timezone_offset)
            temp = self.convert_temp(hour['temp'], unit)
            feels_like = self.convert_temp(hour['feels_like'], unit)
            emoji = self.get_weather_emoji(hour['weather'][0]['id'])
            pop = int(hour.get('pop', 0) * 100)
            wind_speed = self.convert_speed(hour.get('wind_speed', 0), unit)

            if i == 0:
                time_str = "Now"
            else:
                time_str = hour_time.strftime('%H:%M')

            # Enhanced hourly format with feels-like and wind
            forecast_text += f"**{time_str}**: {emoji} {temp}{temp_unit}"

            # Add feels-like if significantly different
            if abs(hour['temp'] - hour['feels_like']) > 2:
                forecast_text += f" (feels {feels_like}{temp_unit})"

            # Add wind if significant
            if wind_speed > 10:  # Only show wind if > 10 km/h or 6 mph
                forecast_text += f" • 💨 {wind_speed}{speed_unit}"

            # Add precipitation chance
            if pop > 0:
                forecast_text += f" • {pop}% ☔"

            forecast_text += "\n"

        embed.add_field(name="🕐 Next 12 Hours", value=forecast_text.strip(), inline=False)

        # Add interpretation footer
        embed.set_footer(text="💡 Feels-like temp shown when significantly different • Wind shown if >10km/h")

        return embed

    async def create_daily_embed(self, data, location_name, country, state, unit='metric'):
        """Create enhanced daily forecast embed with activity recommendations"""
        daily = data['daily'][:7]  # Next 7 days

        location_str = location_name
        if state:
            location_str += f", {state}"
        if country:
            location_str += f", {country}"

        embed = discord.Embed(
            title="📅 7-Day Forecast",
            description=f"📍 **{location_str}**",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )

        forecast_text = ""
        temp_unit = self.get_temp_unit(unit)

        for i, day in enumerate(daily):
            date = datetime.fromtimestamp(day['dt'], tz=timezone.utc)
            day_emoji = self.get_weather_emoji(day['weather'][0]['id'])
            temp_max = self.convert_temp(day['temp']['max'], unit)
            temp_min = self.convert_temp(day['temp']['min'], unit)
            pop = int(day.get('pop', 0) * 100)
            wind_speed = self.convert_speed(day.get('wind_speed', 0), unit)
            uv_index = day.get('uvi', 0)

            if i == 0:
                day_name = "Today"
            elif i == 1:
                day_name = "Tomorrow"
            else:
                day_name = date.strftime('%a')

            # Enhanced daily format with more context
            forecast_text += f"**{day_name}**: {day_emoji} {temp_max}°/{temp_min}°{temp_unit[1:]}"

            # Add weather context
            if pop > 60:
                forecast_text += f" • ☔ {pop}% rain"
            elif pop > 30:
                forecast_text += f" • 🌦️ {pop}% chance"

            # Add wind warning if significant
            if wind_speed > 20:  # Strong wind warning
                forecast_text += f" • 💨 Windy"

            # Add UV warning for high UV days
            if uv_index > 7:
                forecast_text += f" • ☀️ High UV"

            forecast_text += f"\n*{day['weather'][0]['description'].title()}*"

            # Add activity recommendation for first 3 days
            if i < 3:
                activity = self.get_daily_activity_recommendation(temp_max, temp_min, day['weather'][0]['id'], pop, wind_speed, uv_index)
                if activity:
                    forecast_text += f"\n🎯 *{activity}*"

            forecast_text += "\n\n"

        embed.add_field(name="🗓️ Extended Forecast", value=forecast_text.strip(), inline=False)

        # Add seasonal context if available
        current_month = datetime.now().month
        seasonal_note = self.get_seasonal_context(current_month, daily[0]['temp']['max'])
        if seasonal_note:
            embed.add_field(name="🍂 Seasonal Note", value=seasonal_note, inline=False)

        return embed

    async def create_air_quality_embed(self, data, location_name, country, state):
        """Create air quality embed"""
        location_str = location_name
        if state:
            location_str += f", {state}"
        if country:
            location_str += f", {country}"

        embed = discord.Embed(
            title="💨 Air Quality",
            description=f"📍 **{location_str}**",
            color=discord.Color.orange(),
            timestamp=datetime.now(timezone.utc)
        )

        if 'air_quality' not in data:
            embed.add_field(
                name="❌ No Data",
                value="Air quality information is not available for this location.",
                inline=False
            )
            return embed

        aqi = data['air_quality']['list'][0]
        main_aqi = aqi['main']['aqi']
        components = aqi['components']

        # AQI levels (OpenWeatherMap 1-5 scale)
        aqi_levels = {
            1: ("Good", "💚", discord.Color.green()),
            2: ("Fair", "💛", discord.Color.gold()),
            3: ("Moderate", "🧡", discord.Color.orange()),
            4: ("Poor", "❤️", discord.Color.red()),
            5: ("Very Poor", "💜", discord.Color.purple())
        }

        level_name, level_emoji, embed_color = aqi_levels.get(main_aqi, ("Unknown", "❓", discord.Color.light_grey()))
        embed.color = embed_color

        # Convert to standard 0-500 AQI scale for familiarity
        standard_aqi = self.convert_to_standard_aqi(main_aqi)
        standard_range = self.get_standard_aqi_range(standard_aqi)

        embed.add_field(
            name="🌍 Overall Air Quality",
            value=f"{level_emoji} **{level_name}**\n"
                  f"**Standard AQI: {standard_aqi}** {standard_range}\n"
                  f"*OpenWeatherMap Scale: {main_aqi}/5*",
            inline=False
        )

        # Main pollutants with better formatting
        embed.add_field(
            name="🏭 Key Pollutants (μg/m³)",
            value=f"**PM2.5:** {components.get('pm2_5', 'N/A')}\n"
                  f"**PM10:** {components.get('pm10', 'N/A')}\n"
                  f"**NO₂:** {components.get('no2', 'N/A')}",
            inline=True
        )

        embed.add_field(
            name="💨 Other Components (μg/m³)",
            value=f"**O₃:** {components.get('o3', 'N/A')}\n"
                  f"**CO:** {components.get('co', 'N/A')}\n"
                  f"**SO₂:** {components.get('so2', 'N/A')}",
            inline=True
        )

        # Health recommendations with AQI context
        recommendations = {
            1: "Air quality is excellent. Perfect for all outdoor activities! 🏃‍♂️🚴‍♀️",
            2: "Air quality is acceptable for most people. Enjoy outdoor activities! 🚶‍♀️",
            3: "Moderate air quality. Sensitive individuals should limit prolonged outdoor exertion. ⚠️",
            4: "Unhealthy air quality. Everyone should reduce outdoor activities. Consider wearing a mask. 😷",
            5: "Very unhealthy air quality. Avoid outdoor activities. Stay indoors and use air purifiers. 🏠"
        }

        embed.add_field(
            name="💡 Health Advice",
            value=recommendations.get(main_aqi, "Monitor air quality regularly."),
            inline=False
        )

        # Add AQI scale explanation
        embed.add_field(
            name="📊 About AQI Scale",
            value="Standard AQI: 0-50 Good • 51-100 Moderate • 101-150 Unhealthy for Sensitive • 151-200 Unhealthy • 201-300 Very Unhealthy • 301-500 Hazardous",
            inline=False
        )

        return embed

    def convert_to_standard_aqi(self, owm_aqi):
        """Convert OpenWeatherMap 1-5 scale to approximate standard 0-500 AQI scale"""
        # Health-focused conversion that properly utilizes the full 0-500 scale
        conversion_map = {
            1: 25,    # Good: 0-50 range (midpoint)
            2: 75,    # Moderate: 51-100 range (midpoint)
            3: 125,   # Unhealthy for Sensitive: 101-150 range (midpoint)
            4: 200,   # Unhealthy: 151-200 range (upper end)
            5: 400    # Hazardous: 301-500 range (middle) - reflects true severity
        }
        return conversion_map.get(owm_aqi, 100)

    def get_standard_aqi_range(self, aqi_value):
        """Get the range description for standard AQI"""
        if aqi_value <= 50:
            return "(0-50)"
        elif aqi_value <= 100:
            return "(51-100)"
        elif aqi_value <= 150:
            return "(101-150)"
        elif aqi_value <= 200:
            return "(151-200)"
        elif aqi_value <= 300:
            return "(201-300)"
        elif aqi_value <= 400:
            return "(301-400)"
        elif aqi_value <= 500:
            return "(401-500)"
        else:
            return "(500+)"

    def get_wind_direction(self, degrees):
        """Convert wind degrees to compass direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]

    def get_uv_risk_level(self, uv_index):
        """Get UV risk level based on UV index"""
        if uv_index < 3:
            return "Low"
        elif uv_index < 6:
            return "Moderate"
        elif uv_index < 8:
            return "High"
        elif uv_index < 11:
            return "Very High"
        else:
            return "Extreme"

    def get_temperature_color(self, temp_celsius):
        """Get embed color based on temperature"""
        if temp_celsius <= -10:
            return discord.Color.from_rgb(173, 216, 230)  # Light blue
        elif temp_celsius <= 0:
            return discord.Color.blue()
        elif temp_celsius <= 10:
            return discord.Color.teal()
        elif temp_celsius <= 20:
            return discord.Color.green()
        elif temp_celsius <= 30:
            return discord.Color.gold()
        elif temp_celsius <= 35:
            return discord.Color.orange()
        else:
            return discord.Color.red()

    def get_weather_emoji(self, weather_id):
        """Get appropriate emoji for weather condition ID"""
        if weather_id < 300:  # Thunderstorm
            return "⛈️"
        elif weather_id < 400:  # Drizzle
            return "🌦️"
        elif weather_id < 600:  # Rain
            return "🌧️"
        elif weather_id < 700:  # Snow
            return "❄️"
        elif weather_id < 800:  # Atmosphere (fog, haze, etc.)
            return "🌫️"
        elif weather_id == 800:  # Clear sky
            return "☀️"
        elif weather_id == 801:  # Few clouds
            return "🌤️"
        elif weather_id == 802:  # Scattered clouds
            return "⛅"
        else:  # Broken/overcast clouds
            return "☁️"

    def get_weather_color(self, weather_main):
        """Get color based on weather condition"""
        colors = {
            'Clear': discord.Color.gold(),
            'Clouds': discord.Color.light_grey(),
            'Rain': discord.Color.blue(),
            'Drizzle': discord.Color.blue(),
            'Thunderstorm': discord.Color.dark_purple(),
            'Snow': discord.Color.from_rgb(255, 255, 255),
            'Mist': discord.Color.light_grey(),
            'Fog': discord.Color.light_grey(),
            'Haze': discord.Color.orange()
        }
        return colors.get(weather_main, discord.Color.blurple())

    def get_clothing_recommendation(self, temp_celsius, weather_id, wind_speed):
        """Get smart clothing recommendation based on temperature and weather conditions"""
        # Basic temperature recommendations
        if temp_celsius >= 25:
            if weather_id in [800]:  # Clear sky
                return "Light clothing, sunglasses"
            elif weather_id in [801, 802, 803, 804]:  # Clouds
                return "Light clothing, maybe a light layer"
            elif weather_id >= 200 and weather_id < 600:  # Rain/storms
                return "Light clothing + waterproof jacket"
        elif temp_celsius >= 15:
            if weather_id >= 200 and weather_id < 600:  # Rain/storms
                return "Light jacket + waterproof layer"
            elif wind_speed > 5:  # Windy
                return "Light jacket, windbreaker recommended"
            else:
                return "Light jacket or sweater"
        elif temp_celsius >= 5:
            if weather_id >= 600 and weather_id < 700:  # Snow
                return "Warm coat, gloves, winter boots"
            elif weather_id >= 200 and weather_id < 600:  # Rain/storms
                return "Warm jacket + waterproof outer layer"
            else:
                return "Warm jacket, long pants"
        elif temp_celsius >= -5:
            return "Heavy coat, gloves, warm layers"
        else:
            return "Heavy winter gear, multiple layers"

        return None

    def get_pressure_trend(self, pressure):
        """Get pressure trend information and weather context"""
        # Standard atmospheric pressure ranges
        if pressure > 1020:
            return {
                'emoji': '🔼',
                'context': 'High pressure - clear skies likely'
            }
        elif pressure > 1013:
            return {
                'emoji': '↗️',
                'context': 'Rising - improving conditions'
            }
        elif pressure > 1000:
            return {
                'emoji': '➡️',
                'context': 'Stable conditions'
            }
        elif pressure > 980:
            return {
                'emoji': '↘️',
                'context': 'Falling - weather may worsen'
            }
        else:
            return {
                'emoji': '🔻',
                'context': 'Low pressure - storms possible'
            }

    def get_moon_phase_info(self, moon_phase):
        """Get detailed moon phase information"""
        # OpenWeatherMap moon_phase: 0 and 1 are 'new moon', 0.25 is 'first quarter',
        # 0.5 is 'full moon', 0.75 is 'last quarter'

        # Calculate illumination percentage (approximate)
        if moon_phase <= 0.5:
            illumination = int(moon_phase * 200)  # 0 to 100%
        else:
            illumination = int((1 - moon_phase) * 200)  # 100% back to 0%

        # Determine phase name and emoji
        if moon_phase < 0.0625:  # New moon
            return {
                'emoji': '🌑',
                'phase': 'New Moon',
                'illumination': 0
            }
        elif moon_phase < 0.1875:  # Waxing crescent
            return {
                'emoji': '🌒',
                'phase': 'Waxing Crescent',
                'illumination': illumination
            }
        elif moon_phase < 0.3125:  # First quarter
            return {
                'emoji': '🌓',
                'phase': 'First Quarter',
                'illumination': illumination
            }
        elif moon_phase < 0.4375:  # Waxing gibbous
            return {
                'emoji': '🌔',
                'phase': 'Waxing Gibbous',
                'illumination': illumination
            }
        elif moon_phase < 0.5625:  # Full moon
            return {
                'emoji': '🌕',
                'phase': 'Full Moon',
                'illumination': 100
            }
        elif moon_phase < 0.6875:  # Waning gibbous
            return {
                'emoji': '🌖',
                'phase': 'Waning Gibbous',
                'illumination': illumination
            }
        elif moon_phase < 0.8125:  # Last quarter
            return {
                'emoji': '🌗',
                'phase': 'Last Quarter',
                'illumination': illumination
            }
        else:  # Waning crescent
            return {
                'emoji': '🌘',
                'phase': 'Waning Crescent',
                'illumination': illumination
            }

    def detect_severe_weather(self, current, today):
        """Detect severe weather conditions based on current and today's weather"""
        warnings = []

        # Temperature extremes
        temp_celsius = current['temp']
        if temp_celsius <= -20:
            warnings.append("🥶 **Extreme Cold**: Dangerous conditions - limit outdoor exposure")
        elif temp_celsius >= 40:
            warnings.append("🔥 **Extreme Heat**: Heat emergency conditions - stay hydrated and cool")
        elif temp_celsius >= 35:
            warnings.append("🌡️ **Very Hot**: High heat stress risk - take frequent breaks")
        elif temp_celsius <= -10:
            warnings.append("❄️ **Very Cold**: Frostbite risk - dress warmly")

        # Wind conditions
        wind_speed = current.get('wind_speed', 0) * 3.6  # Convert to km/h
        if wind_speed >= 60:
            warnings.append("💨 **High Wind Warning**: Dangerous wind speeds - avoid outdoor activities")
        elif wind_speed >= 40:
            warnings.append("🌬️ **Strong Winds**: Use caution outdoors - secure loose objects")

        # Heat index / wind chill
        feels_like = current['feels_like']
        if feels_like >= 40:
            warnings.append("🔥 **Heat Index Warning**: Feels like {:.0f}°C - heat exhaustion risk".format(feels_like))
        elif feels_like <= -25:
            warnings.append("🧊 **Wind Chill Warning**: Feels like {:.0f}°C - frostbite risk".format(feels_like))

        # UV Index
        uv_index = current.get('uvi', 0)
        if uv_index >= 11:
            warnings.append("☀️ **Extreme UV**: Avoid sun exposure - use maximum protection")
        elif uv_index >= 8:
            warnings.append("🌞 **Very High UV**: Limit midday sun exposure")

        # Severe weather conditions
        weather_id = current['weather'][0]['id']
        if weather_id >= 200 and weather_id < 300:  # Thunderstorms
            warnings.append("⛈️ **Thunderstorms**: Lightning risk - seek shelter indoors")
        elif weather_id >= 600 and weather_id < 700:  # Snow
            snow_1h = current.get('snow', {}).get('1h', 0)
            if snow_1h > 5:
                warnings.append("❄️ **Heavy Snow**: Poor visibility and travel conditions")
        elif weather_id >= 500 and weather_id < 600:  # Rain
            rain_1h = current.get('rain', {}).get('1h', 0)
            if rain_1h > 10:
                warnings.append("🌧️ **Heavy Rain**: Flooding possible - avoid low-lying areas")

        # Humidity extremes
        humidity = current['humidity']
        if humidity >= 90 and temp_celsius >= 25:
            warnings.append("💧 **High Humidity**: Uncomfortable conditions - heat stress risk")
        elif humidity <= 20:
            warnings.append("🏜️ **Very Dry**: Fire risk elevated - stay hydrated")

        return "\n".join(warnings) if warnings else None

    def get_current_activity_recommendation(self, temp_celsius, weather_id, wind_speed, uv_index, humidity, pop):
        """Get activity recommendations based on current conditions"""
        recommendations = []

        # Perfect weather conditions
        if (15 <= temp_celsius <= 25 and weather_id == 800 and
            wind_speed < 15 and uv_index < 8):
            recommendations.append("Perfect for outdoor activities! 🌟")
            return "Perfect for outdoor activities! 🌟"

        # Good outdoor conditions
        if (10 <= temp_celsius <= 30 and weather_id in [800, 801, 802] and
            wind_speed < 20 and pop < 30):
            activities = []
            if temp_celsius >= 20:
                activities.extend(["swimming 🏊", "hiking 🥾", "cycling 🚴"])
            else:
                activities.extend(["walking 🚶", "jogging 🏃", "outdoor sports ⚽"])

            if uv_index > 6:
                activities.append("wear sunscreen ☂️")

            return f"Great for: {', '.join(activities)}"

        # Weather-specific recommendations
        if weather_id >= 500 and weather_id < 600:  # Rain
            if pop > 60:
                return "Indoor activities recommended ☔ - museums, shopping, reading 📚"
            else:
                return "Light rain possible - bring umbrella ☂️ for short outings"

        if weather_id >= 600 and weather_id < 700:  # Snow
            return "Winter activities! ❄️ - skiing, snowboarding, winter walks"

        if temp_celsius < 0:
            return "Bundle up! 🧥 - ice skating, winter sports, or cozy indoor time ☕"

        if temp_celsius > 30:
            if humidity > 70:
                return "Stay cool! 🧊 - swimming, air-conditioned spaces, early morning activities"
            else:
                return "Hot weather! 🌡️ - pool time, early/late outdoor activities, stay hydrated"

        if wind_speed > 25:
            return "Windy conditions 💨 - indoor activities or sheltered outdoor spots"

        if uv_index > 8:
            return "High UV! ☀️ - seek shade, wear protection, outdoor activities before 10am/after 4pm"

        # Default recommendation
        return "Check conditions and dress appropriately! 👕"

    def get_daily_activity_recommendation(self, temp_max, temp_min, weather_id, pop, wind_speed, uv_index):
        """Get daily activity recommendations for forecast days"""
        # Perfect day
        if (20 <= temp_max <= 28 and temp_min >= 15 and
            weather_id in [800, 801] and pop < 20):
            return "Perfect day for outdoor plans!"

        # Good weather day
        if (15 <= temp_max <= 30 and weather_id in [800, 801, 802] and pop < 40):
            return "Great day for outdoor activities"

        # Rainy day
        if weather_id >= 500 and weather_id < 600 or pop > 60:
            return "Plan indoor activities"

        # Hot day
        if temp_max > 32:
            return "Early morning/evening outdoor time"

        # Cold day
        if temp_max < 5:
            return "Winter activities or indoor plans"

        # Windy day
        if wind_speed > 25:
            return "Sheltered activities recommended"

        # High UV day
        if uv_index > 8:
            return "Sun protection essential"

        return None

    def get_seasonal_context(self, month, temp_max):
        """Get seasonal context for the weather"""
        # Northern hemisphere seasons
        if month in [12, 1, 2]:  # Winter
            season = "winter"
            if temp_max > 15:
                return f"🌡️ Unusually warm for {season} - enjoy the mild weather!"
            elif temp_max < -5:
                return f"❄️ Very cold {season} day - typical winter conditions"
        elif month in [3, 4, 5]:  # Spring
            season = "spring"
            if temp_max > 25:
                return f"🌸 Warm {season} day - great weather for outdoor activities!"
            elif temp_max < 5:
                return f"🌧️ Cool {season} day - still transitioning from winter"
        elif month in [6, 7, 8]:  # Summer
            season = "summer"
            if temp_max > 35:
                return f"☀️ Very hot {season} day - stay cool and hydrated!"
            elif temp_max < 20:
                return f"🌤️ Cool {season} day - pleasant break from the heat"
        elif month in [9, 10, 11]:  # Autumn/Fall
            season = "autumn"
            if temp_max > 25:
                return f"🍂 Warm {season} day - beautiful weather for outdoor activities!"
            elif temp_max < 10:
                return f"🍁 Cool {season} day - sweater weather begins"

        return None

    async def create_details_embed(self, data, location_name, country, state, unit='metric'):
        """Create detailed weather information embed with astronomy and extended data"""
        current = data['current']
        daily = data['daily']
        timezone_offset = data['timezone_offset']

        location_str = location_name
        if state:
            location_str += f", {state}"
        if country:
            location_str += f", {country}"

        embed = discord.Embed(
            title="📊 Weather Details",
            description=f"📍 **{location_str}**",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )

        # Enhanced Sun & Moon times with day length
        sunrise = self.get_local_time(current['sunrise'], timezone_offset)
        sunset = self.get_local_time(current['sunset'], timezone_offset)
        day_length = sunset - sunrise

        # Get moon phase info
        moon_info = self.get_moon_phase_info(daily[0].get('moon_phase', 0))

        sun_moon_text = f"🌅 **Sunrise:** {sunrise.strftime('%H:%M')}\n"
        sun_moon_text += f"🌇 **Sunset:** {sunset.strftime('%H:%M')}\n"
        sun_moon_text += f"⏰ **Day length:** {day_length.seconds//3600}h {(day_length.seconds//60)%60}m\n"
        sun_moon_text += f"{moon_info['emoji']} **{moon_info['phase']}** ({moon_info['illumination']}%)"

        embed.add_field(
            name="🌅 Astronomy",
            value=sun_moon_text,
            inline=False
        )

        # Extended atmospheric details
        temp_unit = self.get_temp_unit(unit)
        humidity = current['humidity']
        pressure = current['pressure']
        dew_point = self.convert_temp(current.get('dew_point', 0), unit) if 'dew_point' in current else None
        cloud_cover = current.get('clouds', 0)

        pressure_trend = self.get_pressure_trend(pressure)
        atm_text = f"**Humidity:** {humidity}%\n"
        atm_text += f"**Pressure:** {pressure} hPa {pressure_trend['emoji']}\n"
        if pressure_trend['context']:
            atm_text += f"*{pressure_trend['context']}*\n"
        if dew_point is not None:
            atm_text += f"**Dew Point:** {dew_point}{temp_unit}\n"
        atm_text += f"**Cloud Cover:** {cloud_cover}%"

        embed.add_field(
            name="🌫️ Atmospheric Details",
            value=atm_text,
            inline=True
        )

        # Extended UV and visibility info
        uv_index = current.get('uvi', 0)
        uv_risk = self.get_uv_risk_level(uv_index)
        visibility = current.get('visibility', 0) / 1000 if 'visibility' in current else None

        uv_text = f"**UV Index:** {uv_index}/11 ({uv_risk})\n"
        if visibility:
            uv_text += f"**Visibility:** {visibility:.1f} km\n"

        # UV safety recommendations
        if uv_index >= 11:
            uv_text += "🚨 *Extreme - avoid sun exposure*"
        elif uv_index >= 8:
            uv_text += "⚠️ *Very high - limit exposure*"
        elif uv_index >= 6:
            uv_text += "☂️ *High - use sun protection*"
        elif uv_index >= 3:
            uv_text += "🧴 *Moderate - consider protection*"
        else:
            uv_text += "✅ *Low - minimal protection needed*"

        embed.add_field(
            name="☀️ UV & Visibility Details",
            value=uv_text,
            inline=True
        )

        # Air pressure trends and weather insights
        trends_text = ""

        # Wind analysis
        wind_speed = current.get('wind_speed', 0) * 3.6  # Convert to km/h
        if wind_speed > 30:
            trends_text += "💨 **Strong winds** - outdoor activities affected\n"
        elif wind_speed > 15:
            trends_text += "🌬️ **Breezy conditions** - light items may blow around\n"
        else:
            trends_text += "🍃 **Calm winds** - favorable for outdoor activities\n"

        # Humidity analysis
        if humidity > 80:
            trends_text += "💧 **Very humid** - may feel uncomfortable\n"
        elif humidity > 60:
            trends_text += "💦 **Moderately humid** - typical comfort levels\n"
        elif humidity < 30:
            trends_text += "🏜️ **Dry air** - hydration important\n"
        else:
            trends_text += "💨 **Comfortable humidity** - ideal conditions\n"

        # Temperature comfort analysis
        temp_celsius = current['temp']
        feels_like = current['feels_like']
        temp_diff = abs(temp_celsius - feels_like)

        if temp_diff > 5:
            trends_text += f"🌡️ **Significant feel difference** - feels {temp_diff:.0f}°C different"
        elif temp_diff > 2:
            trends_text += "🌡️ **Noticeable feel difference** - dress accordingly"
        else:
            trends_text += "🌡️ **Temperature feels accurate** - minimal wind/humidity effect"

        embed.add_field(
            name="🔍 Weather Analysis",
            value=trends_text,
            inline=False
        )

        # Seasonal context
        current_month = datetime.now().month
        seasonal_note = self.get_seasonal_context(current_month, daily[0]['temp']['max'])
        if seasonal_note:
            embed.add_field(name="🍂 Seasonal Context", value=seasonal_note, inline=False)

        # Footer
        local_time = self.get_local_time(current['dt'], timezone_offset)
        embed.set_footer(
            text=f"🕒 {location_name} local time: {local_time.strftime('%H:%M')} • Detailed weather analysis",
            icon_url="https://openweathermap.org/img/wn/10d@2x.png"
        )

        return embed

    async def create_activities_embed(self, data, location_name, country, state, unit='metric'):
        """Create activity recommendations embed"""
        current = data['current']
        daily = data['daily']
        timezone_offset = data['timezone_offset']

        location_str = location_name
        if state:
            location_str += f", {state}"
        if country:
            location_str += f", {country}"

        embed = discord.Embed(
            title="🎯 Activity Recommendations",
            description=f"📍 **{location_str}**",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )

        # Current activity recommendations
        temp_celsius = current['temp']
        uv_index = current.get('uvi', 0)
        activity_rec = self.get_current_activity_recommendation(
            temp_celsius, current['weather'][0]['id'], current.get('wind_speed', 0),
            uv_index, current['humidity'], daily[0].get('pop', 0)
        )

        if activity_rec:
            embed.add_field(
                name="🕐 Right Now",
                value=activity_rec,
                inline=False
            )

        # Daily activity planning for next 3 days
        planning_text = ""
        temp_unit = self.get_temp_unit(unit)

        for i, day in enumerate(daily[:3]):
            date = datetime.fromtimestamp(day['dt'], tz=timezone.utc)
            day_emoji = self.get_weather_emoji(day['weather'][0]['id'])
            temp_max = self.convert_temp(day['temp']['max'], unit)
            temp_min = self.convert_temp(day['temp']['min'], unit)
            pop = int(day.get('pop', 0) * 100)
            wind_speed = self.convert_speed(day.get('wind_speed', 0), unit)
            uv_index = day.get('uvi', 0)

            if i == 0:
                day_name = "Today"
            elif i == 1:
                day_name = "Tomorrow"
            else:
                day_name = date.strftime('%A')

            planning_text += f"**{day_name}** {day_emoji} {temp_max}°/{temp_min}°{temp_unit[1:]}\n"

            activity = self.get_daily_activity_recommendation(temp_max, temp_min, day['weather'][0]['id'], pop, wind_speed, uv_index)
            if activity:
                planning_text += f"🎯 *{activity}*\n"
            else:
                planning_text += f"🎯 *Check conditions and plan accordingly*\n"

            planning_text += "\n"

        if planning_text:
            embed.add_field(
                name="📅 3-Day Planning",
                value=planning_text.strip(),
                inline=False
            )

        # Safety and comfort recommendations
        safety_text = ""

        # Temperature safety
        if temp_celsius >= 35:
            safety_text += "🔥 **Heat Warning:** Stay hydrated, seek shade, limit outdoor time\n"
        elif temp_celsius <= -10:
            safety_text += "❄️ **Cold Warning:** Bundle up, limit skin exposure, watch for ice\n"

        # UV safety
        if uv_index >= 8:
            safety_text += "☀️ **UV Warning:** Use SPF 30+, seek shade 10am-4pm, wear hat\n"
        elif uv_index >= 6:
            safety_text += "🧴 **UV Caution:** Apply sunscreen, consider hat and sunglasses\n"

        # Wind safety
        wind_speed_kmh = current.get('wind_speed', 0) * 3.6
        if wind_speed_kmh >= 40:
            safety_text += "💨 **Wind Warning:** Secure loose items, avoid tall trees\n"

        # Precipitation safety
        if 'rain' in current and current['rain'].get('1h', 0) > 5:
            safety_text += "🌧️ **Heavy Rain:** Watch for flooding, drive carefully\n"
        elif 'snow' in current:
            safety_text += "❄️ **Snow Conditions:** Icy roads possible, allow extra time\n"

        # Thunderstorm safety
        weather_id = current['weather'][0]['id']
        if weather_id >= 200 and weather_id < 300:
            safety_text += "⛈️ **Storm Safety:** Stay indoors, avoid metal objects, unplug electronics\n"

        if safety_text:
            embed.add_field(
                name="⚠️ Safety Reminders",
                value=safety_text.strip(),
                inline=False
            )

        # Optimal timing suggestions
        timing_text = ""

        # Best times for outdoor activities based on conditions
        local_time = self.get_local_time(current['dt'], timezone_offset)
        current_hour = local_time.hour

        # UV-based timing
        if uv_index > 6:
            timing_text += "☀️ **Best UV times:** Before 10am or after 4pm\n"

        # Temperature-based timing
        if temp_celsius > 28:
            timing_text += "🌡️ **Coolest times:** Early morning (6-9am) or evening (7-9pm)\n"
        elif temp_celsius < 5:
            timing_text += "🌡️ **Warmest times:** Midday (11am-2pm) when sun is highest\n"

        # Wind-based timing
        if wind_speed_kmh > 20:
            timing_text += "💨 **Calmer times:** Early morning typically has less wind\n"

        # Rain probability timing
        today_pop = int(daily[0].get('pop', 0) * 100)
        if today_pop > 40:
            timing_text += f"🌧️ **Rain chance:** {today_pop}% today - check hourly forecast\n"

        if timing_text:
            embed.add_field(
                name="⏰ Optimal Timing",
                value=timing_text.strip(),
                inline=False
            )

        # Activity-specific recommendations
        activities_text = ""

        # Outdoor sports
        if (10 <= temp_celsius <= 25 and wind_speed_kmh < 25 and
            current['weather'][0]['id'] in [800, 801, 802]):
            activities_text += "⚽ **Sports:** Great conditions for outdoor sports!\n"

        # Photography
        if current['weather'][0]['id'] in [801, 802, 803]:  # Some clouds
            activities_text += "📸 **Photography:** Nice lighting with some clouds\n"
        elif current['weather'][0]['id'] == 800:  # Clear
            activities_text += "📸 **Photography:** Clear skies - great for landscapes\n"

        # Water activities
        if temp_celsius >= 22 and current['weather'][0]['id'] in [800, 801, 802]:
            activities_text += "🏊 **Water activities:** Good conditions for swimming/water sports\n"

        # Hiking
        if (5 <= temp_celsius <= 30 and wind_speed_kmh < 30 and
            not (weather_id >= 200 and weather_id < 600)):
            activities_text += "🥾 **Hiking:** Good conditions for trail activities\n"

        # Gardening
        if (10 <= temp_celsius <= 30 and wind_speed_kmh < 20 and
            current['weather'][0]['id'] != 500):  # Not rain
            activities_text += "🌱 **Gardening:** Good conditions for outdoor garden work\n"

        if activities_text:
            embed.add_field(
                name="🎨 Activity Suggestions",
                value=activities_text.strip(),
                inline=False
            )

        # Footer
        embed.set_footer(
            text=f"🕒 {location_name} local time: {local_time.strftime('%H:%M')} • Activity planning guide",
            icon_url="https://openweathermap.org/img/wn/10d@2x.png"
        )

        return embed


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(Weather(bot))
