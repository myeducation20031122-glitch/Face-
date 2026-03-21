@bot.message_handler(commands=['social_check'])
def social_check(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "අංකය දාන්න බොසා! (Ex: /social_check 94771402910)")
        return
    
    num = args[1].replace('+', '')
    bot.send_message(message.chat.id, f"🔍 Hunting Social Media footprint for: {num}...")

    # Google Search for the number (Quotes පාවිච්චි කරලා exact match බලනවා)
    google_search = f"https://www.google.com/search?q=%22{num}%22+OR+%22{num.replace('947', '07')}%22"
    
    # Facebook Search Link
    fb_search = f"https://www.facebook.com/search/top/?q={num}"
    
    # Truecaller Web (මේකෙන් නම අහුවෙන්න ඉඩ වැඩියි)
    true_url = f"https://www.truecaller.com/search/lk/{num}"

    bot.send_message(message.chat.id, f"✅ Intel Links Generated:\n\n🌍 Google Deep Search: {google_search}\n👤 Facebook Check: {fb_search}\n📞 Truecaller Info: {true_url}\n\n(බොසා, Truecaller ලින්ක් එක ක්ලික් කරලා නම මොකක්ද කියලා බලන්න!)")
