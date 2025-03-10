import telebot
import subprocess
import time
import ipaddress
import logging
import threading
import requests
from variables import bot, admin_id

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def switch_warp_ip():
    """Switch IP by disconnecting and reconnecting WARP."""
    try:
        subprocess.run(["warp-cli", "disconnect"], check=True)
        time.sleep(2)
        subprocess.run(["warp-cli", "connect"], check=True)
        time.sleep(5)
        return "WARP IP switched successfully."
    except subprocess.CalledProcessError as e:
        return f"Error switching WARP IP: {e}"
    except FileNotFoundError:
        return "WARP CLI is not installed or not found in PATH."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def connect_warp_cli():
    """Connect WARP-cli."""
    try:
        subprocess.run(["warp-cli", "connect"], check=True)
        time.sleep(5)
        return "WARP Connected successfully."
    except subprocess.CalledProcessError as e:
        return f"Error Connect WARP: {e}"
    except FileNotFoundError:
        return "WARP CLI is not installed or not found in PATH."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def disconnect_warp_cli():
    """Disconnect WARP-cli."""
    try:
        subprocess.run(["warp-cli", "disconnect"], check=True)
        time.sleep(5)
        return "WARP disconnected successfully."
    except subprocess.CalledProcessError as e:
        return f"Error disconnecting WARP: {e}"
    except FileNotFoundError:
        return "WARP CLI is not installed or not found in PATH."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def add_ip_to_warp_tunnel(add_ip):
    """Add an IP to the WARP tunnel."""
    try:
        subprocess.run(["warp-cli", "tunnel", "ip", "add", add_ip], check=True)
        time.sleep(2)
        return f"IP {add_ip} added to WARP tunnel successfully."
    except subprocess.CalledProcessError as e:
        return f"Error adding IP to WARP tunnel: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def is_valid_ip(ip):
    """Check if the provided IP address is valid."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

@bot.message_handler(commands=['switchip'])
def handle_switch_ip(message):
    logger.info(f"User {message.from_user.id} issued /switchip command.")
    if message.from_user.id not in admin_id:
        bot.reply_to(message, "You are not authorized to use this command.")
        return
    
    def switch_ip_async():
        result = switch_warp_ip()
        bot.reply_to(message, result)
    
    threading.Thread(target=switch_ip_async).start()
    bot.reply_to(message, "Switching IP... Please wait.")

@bot.message_handler(commands=['addip'])
def handle_add_ip(message):
    logger.info(f"User {message.from_user.id} issued /addip command.")
    if message.from_user.id not in admin_id:
        bot.reply_to(message, "You are not authorized to use this command.")
        return
    
    try:
        add_ip = message.text.split(' ', 1)[1]
        if not is_valid_ip(add_ip):
            bot.reply_to(message, "Invalid IP address.")
            return
    except IndexError:
        bot.reply_to(message, "Please provide an IP address. Usage: /addip <IP>")
        return
    
    result = add_ip_to_warp_tunnel(add_ip)
    bot.reply_to(message, result)

@bot.message_handler(commands=['connect'])
def handle_add_ip(message):
    logger.info(f"User {message.from_user.id} issued /connect command.")
    if message.from_user.id not in admin_id:
        bot.reply_to(message, "You are not authorized to use this command.")
        return
    
    def connect_func():
        result = switch_warp_ip()
        bot.reply_to(message, result)
    
    threading.Thread(target=connect_func).start()
    bot.reply_to(message, "Connecting WARP... Please wait.")

@bot.message_handler(commands=['disconnect'])
def handle_add_ip(message):
    logger.info(f"User {message.from_user.id} issued /disconnect command.")
    if message.from_user.id not in admin_id:
        bot.reply_to(message, "You are not authorized to use this command.")
        return
    
    def disconnect_func():
        result = switch_warp_ip()
        bot.reply_to(message, result)
    
    threading.Thread(target=disconnect_func).start()
    bot.reply_to(message, "Disconnecting WARP... Please wait.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
    Available commands:
    /switchip - Switch WARP IP.
    /connect - Connect WARP-cli.
    /disconnect - Disconnect WARP-cli.
    /addip <IP> - Add an IP to the WARP tunnel.
    """
    bot.reply_to(message, help_text)

def start_bot_with_retry():
    retry_count = 0
    max_retries = 5
    retry_delay = 10  # Delay between retries in seconds

    while retry_count < max_retries:
        try:
            logger.info("Starting bot polling...")
            bot.polling(timeout=60, long_polling_timeout=60)
        except requests.exceptions.ReadTimeout as e:
            logger.error(f"ReadTimeout error: {e}. Retrying in {retry_delay} seconds...")
            retry_count += 1
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break

    if retry_count >= max_retries:
        logger.error("Max retries reached. Exiting...")

# Start the bot with retry logic
start_bot_with_retry()