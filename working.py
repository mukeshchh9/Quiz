
import os
import json
import time
import random
import telebot
import qrcode
from telebot import types
from datetime import datetime, timedelta

# Initialize bot with token
TOKEN = '7592626547:AAFCPLs9IluxsjDrsLrHiZkvvJT-EDiky4U'
bot = telebot.TeleBot(TOKEN)

# Admin ID
ADMIN_ID = 6696347739

# UPI ID for payments
UPI_ID = "6376302899@superyes"

# Initialize files if they don't exist
if not os.path.exists('users.json'):
    with open('users.json', 'w') as f:
        json.dump({}, f)
    print("Created users.json file")

if not os.path.exists('names.json'):
    with open('names.json', 'w') as f:
        json.dump({}, f)
    print("Created names.json file")

if not os.path.exists('quizzes.json'):
    with open('quizzes.json', 'w') as f:
        json.dump({"Agriculture": [], "GK": [], "Hindi": []}, f)
    print("Created quizzes.json file")

# Data handling functions
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

def load_names():
    try:
        with open('names.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_names(names):
    with open('names.json', 'w') as f:
        json.dump(names, f, indent=4)

def load_quizzes():
    try:
        with open('quizzes.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"Agriculture": [], "GK": [], "Hindi": []}

def save_quizzes(quizzes):
    with open('quizzes.json', 'w') as f:
        json.dump(quizzes, f, indent=4)

# User state tracking
user_state = {}
user_captcha = {}
user_quiz = {}
user_data = {}

# Function to generate a simple math CAPTCHA
def generate_captcha():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operation = random.choice(['+', '-', '*'])

    if operation == '+':
        result = num1 + num2
    elif operation == '-':
        result = num1 - num2
    else:
        result = num1 * num2

    question = f"{num1} {operation} {num2} = ?"
    return question, str(result)

# Function to create payment QR code
def create_qr_code(amount):
    try:
        # Use the provided static QR code that works with all amounts
        # The user can specify the amount in their payment app
        img_path = "assets/payment_qr.jpg"  # Changed path

        # Check if file exists
        if not os.path.exists(img_path):
            print(f"QR image not found at {img_path}, trying to create dynamic QR")
            # Fallback to dynamic generation
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            # Create UPI payment string
            upi_string = f"upi://pay?pa={UPI_ID}&cu=INR&pn=Quiz%20Master%20Bot"
            qr.add_data(upi_string)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Save the QR code
            os.makedirs("assets", exist_ok=True)  # Ensure directory exists
            img_path = f"assets/payment_qr_{int(time.time())}.png"
            img.save(img_path)
            print(f"Generated dynamic QR code: {img_path}")
        else:
            print(f"Using static QR code: {img_path}")

        return img_path
    except Exception as e:
        print(f"Error with QR code: {e}")
        return None

# Function to generate subscription keyboard
def get_subscription_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("1 Day Free Trial (Only Once)", callback_data="trial_1day"),
        types.InlineKeyboardButton("1 Day ₹10", callback_data="pay_1day"),
        types.InlineKeyboardButton("7 Days ₹50", callback_data="pay_7days"),
        types.InlineKeyboardButton("1 Month ₹200", callback_data="pay_1month"),
        types.InlineKeyboardButton("6 Months ₹500", callback_data="pay_6months"),
        types.InlineKeyboardButton("1 Year ₹1000", callback_data="pay_1year")
    )

    # Add contact information as a separate button
    markup.add(types.InlineKeyboardButton("📞 Contact Admin", url="https://t.me/Mukeshchh999"))

    return markup

# Function to check if user is approved
def is_user_approved(user_id):
    users = load_users()
    str_user_id = str(user_id)

    if str_user_id in users and "approved" in users[str_user_id]:
        if users[str_user_id]["approved"]:
            # Check if subscription has expired
            expiry_time = users[str_user_id].get("expiry_time", 0)
            if expiry_time > time.time():
                return True
            else:
                # Subscription expired
                users[str_user_id]["approved"] = False
                save_users(users)
                return False
    return False

# Function to check if the user has used free trial
def has_used_free_trial(user_id):
    users = load_users()
    str_user_id = str(user_id)

    if str_user_id in users and "used_free_trial" in users[str_user_id]:
        return users[str_user_id]["used_free_trial"]
    return False

# Function to check if user has completed captcha verification
def has_verified_captcha(user_id):
    users = load_users()
    str_user_id = str(user_id)

    if str_user_id in users and "captcha_verified" in users[str_user_id]:
        return users[str_user_id]["captcha_verified"]
    return False

# Function to get user name from names.json
def get_user_name(user_id):
    names = load_names()
    str_user_id = str(user_id)

    if str_user_id in names:
        return names[str_user_id]["name"]
    return None

# Function to generate subject selection keyboard
def get_subject_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Agriculture", callback_data="subject_Agriculture"),
        types.InlineKeyboardButton("GK", callback_data="subject_GK"),
        types.InlineKeyboardButton("Hindi", callback_data="subject_Hindi"),
        types.InlineKeyboardButton("Mix", callback_data="subject_Mix")
    )
    return markup

# Function to generate quiz question count keyboard
def get_quiz_count_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=5)
    markup.add(
        types.InlineKeyboardButton("10", callback_data="count_10"),
        types.InlineKeyboardButton("20", callback_data="count_20"),
        types.InlineKeyboardButton("30", callback_data="count_30"),
        types.InlineKeyboardButton("40", callback_data="count_40"),
        types.InlineKeyboardButton("50", callback_data="count_50")
    )
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_subjects"))
    return markup

# Function to generate MCQ options keyboard
def get_mcq_keyboard(question_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("A", callback_data=f"answer_{question_id}_A"),
        types.InlineKeyboardButton("B", callback_data=f"answer_{question_id}_B"),
        types.InlineKeyboardButton("C", callback_data=f"answer_{question_id}_C"),
        types.InlineKeyboardButton("D", callback_data=f"answer_{question_id}_D")
    )
    return markup

# Start Command - Initial bot interaction
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    str_user_id = str(user_id)

    # Check if user has already verified CAPTCHA and provided name
    if has_verified_captcha(user_id) and get_user_name(user_id):
        # User is already registered, show subscription plans
        subscription_text = (
            "📌 *Subscription Plans* 📌\n\n"
            "Please select a subscription plan:\n\n"
            "📞 Contact: +917410810528\n\n"
            "For Free Trial → Contact Admin (@Mukeshchh999)"
        )

        bot.send_message(chat_id, subscription_text, parse_mode="Markdown", reply_markup=get_subscription_keyboard())
        return

    # New user flow - first CAPTCHA verification
    if not has_verified_captcha(user_id):
        # Generate CAPTCHA
        captcha_question, captcha_answer = generate_captcha()
        user_captcha[user_id] = captcha_answer
        user_state[user_id] = "verify_captcha"

        # Send welcome message with CAPTCHA
        welcome_text = "🎓 *Welcome to Quiz Master Bot* 🎓\n\nPlease solve this verification problem first:\n\n" + captcha_question
        bot.send_message(chat_id, welcome_text, parse_mode="Markdown")
    else:
        # Ask for name if CAPTCHA already verified but name not provided
        user_state[user_id] = "input_name"
        bot.send_message(chat_id, "Please enter your name to continue:")

# Handle CAPTCHA verification
@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == "verify_captcha")
def verify_captcha(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    answer = message.text.strip()

    if answer == user_captcha.get(user_id):
        # CAPTCHA verified, save verification status
        users = load_users()
        str_user_id = str(user_id)

        if str_user_id not in users:
            users[str_user_id] = {}

        users[str_user_id]["captcha_verified"] = True
        users[str_user_id]["username"] = message.from_user.username or "None"
        users[str_user_id]["join_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)

        # Ask for name
        user_state[user_id] = "input_name"
        bot.send_message(chat_id, "Verification successful! Please enter your name to continue:")
    else:
        bot.send_message(chat_id, "❌ Incorrect answer. Please try again.")

# Handle user name input
@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == "input_name")
def process_name(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    name = message.text.strip()

    if len(name) < 2:
        bot.send_message(chat_id, "Please enter a valid name (at least 2 characters).")
        return

    # Store user name in names.json
    names = load_names()
    str_user_id = str(user_id)

    if str_user_id not in names:
        names[str_user_id] = {}

    names[str_user_id]["name"] = name
    names[str_user_id]["username"] = message.from_user.username or "None"
    names[str_user_id]["join_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_names(names)

    # Update user state
    user_state[user_id] = "subscription"

    # Show subscription plans
    subscription_text = (
        "📌 *Subscription Plans* 📌\n\n"
        "Please select a subscription plan:\n\n"
        "📞 Contact: +917410810528\n\n"
        "For Free Trial → Contact Admin (@Mukeshchh999)"
    )

    bot.send_message(chat_id, subscription_text, parse_mode="Markdown", reply_markup=get_subscription_keyboard())

    # Notify admin about new user
    admin_message = f"🔔 *New User Registration*\n\nName: {name}\nUsername: @{message.from_user.username or 'None'}\nUser ID: `{user_id}`"
    try:
        bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Failed to notify admin: {e}")

# Handle subscription selection
@bot.callback_query_handler(func=lambda call: call.data.startswith(("trial_", "pay_")))
def handle_subscription(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Acknowledge the callback query first to prevent timeouts
    bot.answer_callback_query(call.id)

    # Delete previous message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

    if call.data == "trial_1day":
        # Check if user already used free trial
        if has_used_free_trial(user_id):
            bot.send_message(chat_id, "❌ You have already used your free trial. Please select a paid plan.", reply_markup=get_subscription_keyboard())
        else:
            # Activate free trial
            users = load_users()
            str_user_id = str(user_id)

            users[str_user_id]["used_free_trial"] = True
            users[str_user_id]["approved"] = True
            users[str_user_id]["subscription"] = "1 Day Free Trial"
            users[str_user_id]["expiry_time"] = time.time() + 86400  # 1 day in seconds
            save_users(users)

            confirmation = (
                "✅ *Free Trial Activated!*\n\n"
                "You now have access to quizzes for 1 day.\n"
                "Use /quiz to start practicing."
            )
            bot.send_message(chat_id, confirmation, parse_mode="Markdown")
    else:
        # Handle paid subscriptions
        plan = call.data.replace("pay_", "")
        amount = {
            "1day": 10,
            "7days": 50,
            "1month": 200,
            "6months": 500,
            "1year": 1000
        }.get(plan, 0)

        days = {
            "1day": 1,
            "7days": 7,
            "1month": 30,
            "6months": 180,
            "1year": 365
        }.get(plan, 0)

        # Store subscription details for later verification
        if user_id not in user_data:
            user_data[user_id] = {}
            
        user_data[user_id]["plan"] = plan
        user_data[user_id]["amount"] = amount
        user_data[user_id]["days"] = days

        try:
            # Get QR code (either static or dynamically generated)
            qr_path = create_qr_code(amount)

            # Prepare payment text with clear instructions
            payment_text = (
                f"💰 *Payment: ₹{amount}*\n\n"
                f"1. Scan the QR code or pay to UPI ID: `{UPI_ID}`\n"
                f"2. *Enter amount: ₹{amount}* manually if needed\n"
                "3. After payment, upload the screenshot\n"
                "4. Provide the UTR/Reference number\n\n"
                "Your subscription will be activated after verification.\n\n"
                f"*UPI ID:* `{UPI_ID}`\n"
                "*Bank:* PNB 4060"
            )

            if not qr_path or not os.path.exists(qr_path):
                # If QR not available, send text-only instructions
                bot.send_message(chat_id, payment_text, parse_mode="Markdown")
            else:
                # Send QR code with instructions
                try:
                    with open(qr_path, 'rb') as qr_file:
                        bot.send_photo(chat_id, qr_file, caption=payment_text, parse_mode="Markdown")

                    # Don't delete the static QR file if it's our saved one
                    if not qr_path.startswith("assets/payment_qr.jpg"):
                        try:
                            os.remove(qr_path)
                        except:
                            pass
                except Exception as e:
                    print(f"Error sending QR photo: {e}")
                    # Fallback to text-only if sending photo fails
                    bot.send_message(chat_id, payment_text, parse_mode="Markdown")

            # Update user state
            user_state[user_id] = "awaiting_screenshot"

        except Exception as e:
            print(f"Error in payment handling: {e}")
            # Fallback to text-only payment instructions if anything fails
            payment_text = (
                f"💰 *Payment: ₹{amount}*\n\n"
                f"Please pay to UPI ID: `{UPI_ID}`\n"
                "After payment, upload the screenshot and provide the UTR/Reference number.\n\n"
                f"*UPI ID:* `{UPI_ID}`"
            )
            bot.send_message(chat_id, payment_text, parse_mode="Markdown")
            user_state[user_id] = "awaiting_screenshot"

# Handle payment screenshot upload
@bot.message_handler(content_types=['photo'], func=lambda message: user_state.get(message.from_user.id) == "awaiting_screenshot")
def process_screenshot(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Initialize user_data[user_id] if it doesn't exist
    if user_id not in user_data:
        user_data[user_id] = {}

    # Save the photo ID for verification
    user_data[user_id]["screenshot_id"] = message.photo[-1].file_id

    # Update state and ask for UTR
    user_state[user_id] = "awaiting_utr"
    bot.send_message(chat_id, "Please enter the UTR/Reference number of your payment:")

# Handle UTR input
@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == "awaiting_utr")
def process_utr(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    utr = message.text.strip()

    # Initialize user_data[user_id] if it doesn't exist
    if user_id not in user_data:
        user_data[user_id] = {}

    # Store UTR
    user_data[user_id]["utr"] = utr

    # Update state
    user_state[user_id] = "awaiting_verification"

    # Send wait message
    wait_message = bot.send_message(chat_id, "⏳ Please wait while your payment is being verified...")

    # Get user name for admin notification
    name = get_user_name(user_id) or "Unknown"

    # Ensure all required data exists in user_data
    if "plan" not in user_data[user_id]:
        user_data[user_id]["plan"] = "unknown"
    if "amount" not in user_data[user_id]:
        user_data[user_id]["amount"] = "unknown"
    if "screenshot_id" not in user_data[user_id]:
        # Handle missing screenshot
        bot.send_message(chat_id, "❌ Error: Screenshot not found. Please try the payment process again.")
        if user_id in user_state:
            del user_state[user_id]
        return

    # Send verification request to admin
    admin_text = (
        f"🔔 *Payment Verification Required*\n\n"
        f"Name: {name}\n"
        f"User: @{message.from_user.username or 'None'}\n"
        f"User ID: `{user_id}`\n"
        f"Plan: {user_data[user_id]['plan']}\n"
        f"Amount: ₹{user_data[user_id]['amount']}\n"
        f"UTR: {utr}"
    )

    # Create admin verification keyboard
    verify_markup = types.InlineKeyboardMarkup(row_width=2)
    verify_markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    )

    # Send screenshot to admin
    try:
        bot.send_photo(ADMIN_ID, user_data[user_id]["screenshot_id"], caption=admin_text, parse_mode="Markdown", reply_markup=verify_markup)
    except Exception as e:
        print(f"Failed to send verification to admin: {e}")
        bot.send_message(chat_id, "❌ Error sending verification to admin. Please contact support.")

# Handle admin verification
@bot.callback_query_handler(func=lambda call: call.data.startswith(("approve_", "reject_")))
def handle_verification(call):
    admin_id = call.from_user.id

    if admin_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "You are not authorized to perform this action.")
        return

    parts = call.data.split("_", 1)  # Split at first underscore only
    action = parts[0]
    user_id = int(parts[1]) if len(parts) > 1 else 0

    if action == "approve":
        # Approve the payment
        users = load_users()
        str_user_id = str(user_id)

        if str_user_id not in users:
            users[str_user_id] = {}

        # Check if user_data exists for the user
        if user_id not in user_data or "days" not in user_data[user_id]:
            # Fallback to default values if missing
            days = 1
            plan = "1day"
            amount = 10
        else:
            # Calculate expiry time
            days = user_data[user_id]["days"]
            plan = user_data[user_id].get("plan", "unknown")
            amount = user_data[user_id].get("amount", 0)

        expiry_time = time.time() + (days * 86400)  # Convert days to seconds

        # Update user information
        users[str_user_id]["approved"] = True
        users[str_user_id]["subscription"] = plan
        users[str_user_id]["payment_amount"] = amount
        users[str_user_id]["payment_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users[str_user_id]["expiry_time"] = expiry_time
        users[str_user_id]["payment_utr"] = user_data[user_id].get("utr", "N/A")
        save_users(users)

        # Send confirmation to user
        confirmation = (
            "✅ *Payment Verified Successfully!*\n\n"
            f"Your subscription has been activated for {days} day(s).\n"
            "Use /quiz to start practicing."
        )
        try:
            bot.send_message(user_id, confirmation, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to send confirmation to user {user_id}: {e}")

        # Notify admin about successful approval
        bot.answer_callback_query(call.id, "Payment approved successfully.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    elif action == "reject":
        # Reject the payment
        try:
            bot.send_message(user_id, "❌ Your payment could not be verified. Please try again or contact the admin.", reply_markup=get_subscription_keyboard())
        except Exception as e:
            print(f"Failed to send rejection to user {user_id}: {e}")

        # Notify admin about rejection
        bot.answer_callback_query(call.id, "Payment rejected.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    # Clean up user data
    if user_id in user_state:
        del user_state[user_id]
    if user_id in user_data:
        del user_data[user_id]

# Quiz Command - Start a quiz
@bot.message_handler(commands=['quiz'])
def start_quiz(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Check if user is approved
    if not is_user_approved(user_id):
        bot.send_message(chat_id, "❌ You don't have an active subscription. Please subscribe to access quizzes.", reply_markup=get_subscription_keyboard())
        return

    # Ask for subject selection
    subject_text = "📚 *Choose a Subject*\n\nSelect a subject for your quiz:"
    bot.send_message(chat_id, subject_text, parse_mode="Markdown", reply_markup=get_subject_keyboard())

# Handle subject selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("subject_"))
def handle_subject_selection(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Acknowledge the callback
    bot.answer_callback_query(call.id)

    # Delete previous message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

    subject = call.data.replace("subject_", "")

    # Store subject selection
    if user_id not in user_quiz:
        user_quiz[user_id] = {}

    user_quiz[user_id]["subject"] = subject

    # Ask for question count
    count_text = f"🔢 *Select Number of Questions*\n\nHow many questions would you like for {subject}?"
    bot.send_message(chat_id, count_text, parse_mode="Markdown", reply_markup=get_quiz_count_keyboard())

# Handle back to subjects
@bot.callback_query_handler(func=lambda call: call.data == "back_to_subjects")
def back_to_subjects(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Acknowledge the callback
    bot.answer_callback_query(call.id)

    # Delete previous message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

    # Ask for subject selection again
    subject_text = "📚 *Choose a Subject*\n\nSelect a subject for your quiz:"
    bot.send_message(chat_id, subject_text, parse_mode="Markdown", reply_markup=get_subject_keyboard())

# Handle question count selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("count_"))
def handle_count_selection(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Acknowledge the callback
    bot.answer_callback_query(call.id)

    # Delete previous message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

    count = int(call.data.replace("count_", ""))
    
    # Make sure user_quiz exists for this user
    if user_id not in user_quiz or "subject" not in user_quiz[user_id]:
        # Something went wrong, redirect to subject selection
        subject_text = "📚 *Choose a Subject*\n\nSelect a subject for your quiz:"
        bot.send_message(chat_id, subject_text, parse_mode="Markdown", reply_markup=get_subject_keyboard())
        return
        
    subject = user_quiz[user_id]["subject"]

    # Load questions
    quizzes = load_quizzes()

    if subject == "Mix":
        # Combine questions from all subjects
        all_questions = []
        for sub in ["Agriculture", "GK", "Hindi"]:
            if sub in quizzes and quizzes[sub]:  # Only add if there are questions for this subject
                all_questions.extend(quizzes[sub])

        if not all_questions:
            bot.send_message(chat_id, "❌ No questions available in any subject. Please add questions first.", reply_markup=get_subject_keyboard())
            return

        # Make sure we don't try to select more questions than are available
        if len(all_questions) < count:
            bot.send_message(chat_id, f"⚠️ Only {len(all_questions)} questions available. Proceeding with all available questions.", parse_mode="Markdown")
            selected_questions = all_questions.copy()
            random.shuffle(selected_questions)
        else:
            # Shuffle and select questions
            selected_questions = random.sample(all_questions, count)
    else:
        # Check if subject exists in quizzes
        if subject not in quizzes:
            bot.send_message(chat_id, f"❌ Subject '{subject}' not found. Please try another subject.", reply_markup=get_subject_keyboard())
            return
        
        # Select questions from specific subject
        subject_questions = quizzes[subject]

        if not subject_questions:
            bot.send_message(chat_id, f"❌ No questions available for {subject}. Please try another subject.", reply_markup=get_subject_keyboard())
            return

        # Check if there are enough questions
        if len(subject_questions) < count:
            bot.send_message(chat_id, f"⚠️ Only {len(subject_questions)} questions available for {subject}. Proceeding with available questions.", parse_mode="Markdown")
            selected_questions = subject_questions.copy()
            random.shuffle(selected_questions)
        else:
            # Shuffle and select questions
            selected_questions = random.sample(subject_questions, count)

    # Store quiz data
    user_quiz[user_id]["questions"] = selected_questions
    user_quiz[user_id]["current_question"] = 0
    user_quiz[user_id]["correct_answers"] = 0
    user_quiz[user_id]["answers"] = []  # Track all answers, not showing results immediately

    # Start the quiz
    send_quiz_question(user_id, chat_id)

# Function to send a quiz question
def send_quiz_question(user_id, chat_id):
    try:
        # Check if user_quiz exists for this user
        if user_id not in user_quiz or "questions" not in user_quiz[user_id]:
            bot.send_message(chat_id, "❌ No quiz in progress. Please use /quiz to start a new quiz.")
            return
            
        quiz_data = user_quiz[user_id]
        current_index = quiz_data["current_question"]
        total_questions = len(quiz_data["questions"])

        if current_index < total_questions:
            question_data = quiz_data["questions"][current_index]

            # Ensure question has the required fields
            if "question" not in question_data:
                question_data["question"] = "Missing question text"
                
            # Ensure 'options' dictionary exists
            if 'options' not in question_data:
                question_data['options'] = {}
                
            # Ensure all options exist
            for option in ['A', 'B', 'C', 'D']:
                if option not in question_data['options']:
                    question_data['options'][option] = f"Option {option} (Missing)"

            # Format the question with options
            question_text = (
                f"*Question {current_index + 1}/{total_questions}*\n\n"
                f"{question_data['question']}\n\n"
                f"A. {question_data['options']['A']}\n"
                f"B. {question_data['options']['B']}\n"
                f"C. {question_data['options']['C']}\n"
                f"D. {question_data['options']['D']}"
            )

            # Send question with options
            bot.send_message(chat_id, question_text, parse_mode="Markdown", reply_markup=get_mcq_keyboard(current_index))
        else:
            # All questions answered, show results
            show_quiz_results(user_id, chat_id)
    except Exception as e:
        print(f"Error in send_quiz_question: {e}")
        bot.send_message(chat_id, "❌ An error occurred while displaying the question. Please try again with /quiz.")

        # Reset user quiz state
        if user_id in user_quiz:
            del user_quiz[user_id]

# Handle user answer selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def handle_answer(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Acknowledge the callback
    bot.answer_callback_query(call.id)

    # Delete previous message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

    try:
        parts = call.data.split("_")
        if len(parts) != 3:
            raise ValueError(f"Invalid answer format: {call.data}")
            
        _, question_id, selected_option = parts
        question_id = int(question_id)

        # Check if user_quiz exists for this user
        if user_id not in user_quiz or "questions" not in user_quiz[user_id]:
            bot.send_message(chat_id, "❌ No quiz in progress. Please use /quiz to start a new quiz.")
            return
            
        # Check answer
        quiz_data = user_quiz[user_id]
        
        # Verify question_id is valid
        if question_id >= len(quiz_data["questions"]) or question_id < 0:
            raise ValueError(f"Invalid question_id: {question_id}")
            
        question_data = quiz_data["questions"][question_id]
        
        # Ensure question has all necessary fields
        if "question" not in question_data:
            question_data["question"] = "Missing question text"
            
        if "options" not in question_data:
            question_data["options"] = {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}
            
        # Verify question has a correct answer defined
        if "correct" not in question_data:
            # Default to option A if no correct answer is defined
            question_data["correct"] = "A"
            print(f"Warning: Question has no correct answer defined: {question_data}. Using 'A' as default.")
            
        correct_option = question_data["correct"]
        current_index = quiz_data["current_question"]
        total_questions = len(quiz_data["questions"])

        # Store the answer (don't show result yet)
        if "answers" not in quiz_data:
            quiz_data["answers"] = []
            
        quiz_data["answers"].append({
            "question": question_data["question"],
            "selected": selected_option,
            "correct": correct_option,
            "options": question_data["options"],
            "is_correct": selected_option == correct_option
        })

        # Update correct answer count
        if "correct_answers" not in quiz_data:
            quiz_data["correct_answers"] = 0
            
        if selected_option == correct_option:
            quiz_data["correct_answers"] += 1

        # Show "Answer recorded" message instead of immediate feedback
        bot.send_message(chat_id, f"✓ Answer recorded ({current_index + 1}/{total_questions})")

        # Move to next question
        quiz_data["current_question"] += 1
        send_quiz_question(user_id, chat_id)
    except Exception as e:
        print(f"Error in handle_answer: {e}")
        bot.send_message(chat_id, "❌ An error occurred while processing your answer. Please try again with /quiz.")
        
        # Reset user quiz state
        if user_id in user_quiz:
            del user_quiz[user_id]

# Function to show quiz results
def show_quiz_results(user_id, chat_id):
    try:
        # Check if user_quiz exists for this user
        if user_id not in user_quiz or "questions" not in user_quiz[user_id]:
            bot.send_message(chat_id, "❌ No quiz results available. Please use /quiz to start a new quiz.")
            return
            
        quiz_data = user_quiz[user_id]
        
        # Initialize missing fields if necessary
        if "correct_answers" not in quiz_data:
            quiz_data["correct_answers"] = 0
        if "answers" not in quiz_data:
            quiz_data["answers"] = []
            
        total_questions = len(quiz_data["questions"])
        correct_answers = quiz_data["correct_answers"]
        wrong_answers = total_questions - correct_answers

        # Calculate percentage (avoid division by zero)
        if total_questions > 0:
            percentage = (correct_answers / total_questions) * 100
        else:
            percentage = 0

        # Format result message
        result_text = (
            f"📊 *Quiz Results*\n\n"
            f"Subject: {quiz_data.get('subject', 'Unknown')}\n"
            f"Total Questions: {total_questions}\n"
            f"Correct Answers: {correct_answers}\n"
            f"Wrong Answers: {wrong_answers}\n"
            f"Score: {correct_answers}/{total_questions}\n"
            f"Percentage: {percentage:.2f}%\n\n"
        )

        # Add wrong answers with corrections - with error handling
        if wrong_answers > 0 and quiz_data["answers"]:
            result_text += "*Wrong Answers:*\n\n"

            wrong_count = 0
            for i, answer in enumerate(quiz_data["answers"]):
                try:
                    if not answer.get("is_correct", False):
                        wrong_count += 1
                        
                        # Get options dictionary safely
                        options = answer.get("options", {})
                        if not isinstance(options, dict):
                            options = {}
                            
                        selected = answer.get("selected", "?")
                        correct = answer.get("correct", "?")
                        
                        result_text += (
                            f"❌ *Question {i+1}:* {answer.get('question', 'Missing question')}\n"
                            f"Your Answer: {selected} ({options.get(selected, 'Unknown')})\n"
                            f"Correct Answer: {correct} ({options.get(correct, 'Unknown')})\n\n"
                        )
                except Exception as e:
                    print(f"Error formatting wrong answer {i}: {e}")
                    continue

        # Limit message length to avoid Telegram API limits
        if len(result_text) > 4000:
            result_text = result_text[:3950] + "...\n\n(Result truncated due to length)"

        # Create result keyboard
        result_markup = types.InlineKeyboardMarkup(row_width=2)
        result_markup.add(
            types.InlineKeyboardButton("🔄 Reattempt", callback_data="reattempt"),
            types.InlineKeyboardButton("📚 New Quiz", callback_data="new_quiz")
        )

        # Send results
        bot.send_message(chat_id, result_text, parse_mode="Markdown", reply_markup=result_markup)

        # Get user name
        name = get_user_name(user_id) or "Unknown"

        # Update user history
        users = load_users()
        str_user_id = str(user_id)

        if str_user_id in users:
            if "quiz_history" not in users[str_user_id]:
                users[str_user_id]["quiz_history"] = []

            # Add quiz result to history
            users[str_user_id]["quiz_history"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "subject": quiz_data.get('subject', 'Unknown'),
                "total": total_questions,
                "correct": correct_answers,
                "percentage": f"{percentage:.2f}%"
            })

            save_users(users)

        # Send result to admin
        admin_result = (
            f"🔔 *Quiz Completed*\n\n"
            f"Name: {name}\n"
            f"User: @{users.get(str_user_id, {}).get('username', 'None')}\n"
            f"User ID: `{user_id}`\n"
            f"Subject: {quiz_data.get('subject', 'Unknown')}\n"
            f"Score: {correct_answers}/{total_questions}\n"
            f"Percentage: {percentage:.2f}%"
        )

        try:
            bot.send_message(ADMIN_ID, admin_result, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to send quiz result to admin: {e}")

    except Exception as e:
        print(f"Error in show_quiz_results: {e}")
        bot.send_message(chat_id, "❌ An error occurred while displaying quiz results. Please try again with /quiz.")

        # Reset user quiz state
        if user_id in user_quiz:
            del user_quiz[user_id]

# Handle reattempt or new quiz
@bot.callback_query_handler(func=lambda call: call.data in ["reattempt", "new_quiz"])
def handle_quiz_action(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Acknowledge the callback
    bot.answer_callback_query(call.id)

    # Delete previous message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

    try:
        # Check if user_quiz exists for this user
        if user_id not in user_quiz:
            # Start a new quiz
            subject_text = "📚 *Choose a Subject*\n\nSelect a subject for your quiz:"
            bot.send_message(chat_id, subject_text, parse_mode="Markdown", reply_markup=get_subject_keyboard())
            return

        if call.data == "reattempt" and "questions" in user_quiz[user_id]:
            # Reset quiz progress for reattempt
            user_quiz[user_id]["current_question"] = 0
            user_quiz[user_id]["correct_answers"] = 0
            user_quiz[user_id]["answers"] = []

            # Start the quiz again
            send_quiz_question(user_id, chat_id)
        else:
            # Start a new quiz
            subject_text = "📚 *Choose a Subject*\n\nSelect a subject for your quiz:"
            bot.send_message(chat_id, subject_text, parse_mode="Markdown", reply_markup=get_subject_keyboard())
    except Exception as e:
        print(f"Error in handle_quiz_action: {e}")
        bot.send_message(chat_id, "❌ An error occurred. Please try again with /quiz.")
        
        # Reset user quiz state to be safe
        if user_id in user_quiz:
            del user_quiz[user_id]

# Reattempt command
@bot.message_handler(commands=['reattempt'])
def reattempt_quiz(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id in user_quiz and "questions" in user_quiz[user_id]:
        # Reset quiz progress
        user_quiz[user_id]["current_question"] = 0
        user_quiz[user_id]["correct_answers"] = 0
        user_quiz[user_id]["answers"] = []

        # Start the quiz again
        send_quiz_question(user_id, chat_id)
    else:
        bot.send_message(chat_id, "❌ No recent quiz found to reattempt. Please use /quiz to start a new quiz.")

# Admin Commands
# View user logs
@bot.message_handler(commands=['logs'], func=lambda message: message.from_user.id == ADMIN_ID)
def view_logs(message):
    chat_id = message.chat.id

    try:
        # Extract user_id from command
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(chat_id, "❌ Please provide a user ID. Usage: /logs <user_id>")
            return
            
        user_id = parts[1]
        users = load_users()
        names = load_names()

        if user_id in users:
            user_data = users[user_id]
            name = names.get(user_id, {}).get("name", "Not available")

            # Format user logs
            log_text = (
                f"📋 *User Logs*\n\n"
                f"*User ID:* `{user_id}`\n"
                f"*Name:* {name}\n"
                f"*Username:* @{user_data.get('username', 'None')}\n"
                f"*Join Date:* {user_data.get('join_date', 'Not available')}\n"
                f"*Subscription:* {user_data.get('subscription', 'None')}\n"
                f"*Approved:* {'Yes' if user_data.get('approved', False) else 'No'}\n"
                f"*Used Free Trial:* {'Yes' if user_data.get('used_free_trial', False) else 'No'}\n"
            )

            # Add payment info if available
            if "payment_date" in user_data:
                log_text += (
                    f"*Payment Date:* {user_data['payment_date']}\n"
                    f"*Payment Amount:* ₹{user_data.get('payment_amount', 'N/A')}\n"
                    f"*UTR:* {user_data.get('payment_utr', 'N/A')}\n"
                )

            # Add expiry time if available
            if "expiry_time" in user_data:
                expiry_date = datetime.fromtimestamp(user_data["expiry_time"]).strftime("%Y-%m-%d %H:%M:%S")
                log_text += f"*Expiry Date:* {expiry_date}\n\n"

            # Add quiz history if available
            if "quiz_history" in user_data and user_data["quiz_history"]:
                log_text += "*Quiz History:*\n\n"

                for i, quiz in enumerate(user_data["quiz_history"][-5:], 1):  # Show last 5 quizzes
                    log_text += (
                        f"{i}. Date: {quiz['date']}\n"
                        f"   Subject: {quiz['subject']}\n"
                        f"   Score: {quiz['correct']}/{quiz['total']} ({quiz['percentage']})\n\n"
                    )

            bot.send_message(chat_id, log_text, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "❌ User not found.")
    except Exception as e:
        print(f"Error in view_logs: {e}")
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

# Approve user with custom duration
@bot.message_handler(commands=['approve'], func=lambda message: message.from_user.id == ADMIN_ID)
def approve_user(message):
    chat_id = message.chat.id

    try:
        # Extract user_id and days from command
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(chat_id, "❌ Incorrect format. Usage: /approve <user_id> <days>")
            return

        user_id = parts[1]
        days = int(parts[2])

        if days <= 0:
            bot.send_message(chat_id, "❌ Days must be a positive number.")
            return

        users = load_users()

        if user_id not in users:
            users[user_id] = {}

        # Calculate expiry time
        expiry_time = time.time() + (days * 86400)  # Convert days to seconds

        # Update user information
        users[user_id]["approved"] = True
        users[user_id]["subscription"] = f"{days} Day(s) Admin Approval"
        users[user_id]["payment_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users[user_id]["expiry_time"] = expiry_time
        save_users(users)

        bot.send_message(chat_id, f"✅ User {user_id} has been approved for {days} day(s).")

        # Notify user
        try:
            bot.send_message(int(user_id), f"✅ Your subscription has been approved for {days} day(s). Use /quiz to start practicing.")
        except Exception as e:
            print(f"Failed to notify user {user_id}: {e}")
            
    except ValueError as e:
        print(f"Error in approve_user: {e}")
        bot.send_message(chat_id, "❌ Days must be a valid number. Usage: /approve <user_id> <days>")
    except Exception as e:
        print(f"Error in approve_user: {e}")
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

# Disapprove user
@bot.message_handler(commands=['disapprove'], func=lambda message: message.from_user.id == ADMIN_ID)
def disapprove_user(message):
    chat_id = message.chat.id

    try:
        # Extract user_id from command
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(chat_id, "❌ Please provide a user ID. Usage: /disapprove <user_id>")
            return
            
        user_id = parts[1]
        users = load_users()

        if user_id in users:
            # Disapprove user
            users[user_id]["approved"] = False
            save_users(users)

            bot.send_message(chat_id, f"✅ User {user_id} has been disapproved.")

            # Notify user
            try:
                bot.send_message(int(user_id), "❌ Your subscription has been revoked by the admin. Please contact support for more information.")
            except Exception as e:
                print(f"Failed to notify user {user_id}: {e}")
        else:
            bot.send_message(chat_id, "❌ User not found.")
    except Exception as e:
        print(f"Error in disapprove_user: {e}")
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

# View all approved users
@bot.message_handler(commands=['view'], func=lambda message: message.from_user.id == ADMIN_ID)
def view_approved_users(message):
    chat_id = message.chat.id
    
    try:
        users = load_users()
        names = load_names()

        approved_users = []

        for user_id, user_data in users.items():
            if user_data.get("approved", False):
                username = user_data.get("username", "None")
                name = names.get(user_id, {}).get("name", "Unknown")
                expiry_time = user_data.get("expiry_time", 0)
                expiry_date = datetime.fromtimestamp(expiry_time).strftime("%Y-%m-%d") if expiry_time > 0 else "N/A"

                approved_users.append(f"👤 ID: `{user_id}`\n   Name: {name}\n   Username: @{username}\n   Expiry: {expiry_date}\n")

        if approved_users:
            # Split into chunks if there are many users
            chunk_size = 20
            for i in range(0, len(approved_users), chunk_size):
                chunk = approved_users[i:i + chunk_size]
                text = f"📋 *Approved Users ({i+1}-{min(i+chunk_size, len(approved_users))} of {len(approved_users)})*\n\n" + "\n".join(chunk)
                bot.send_message(chat_id, text, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "❌ No approved users found.")
    except Exception as e:
        print(f"Error in view_approved_users: {e}")
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

# Broadcast message to all users
@bot.message_handler(commands=['broadcast'], func=lambda message: message.from_user.id == ADMIN_ID)
def broadcast_message(message):
    chat_id = message.chat.id

    try:
        # Extract broadcast message
        broadcast_text = message.text.replace("/broadcast", "", 1).strip()

        if not broadcast_text:
            bot.send_message(chat_id, "❌ Please provide a message to broadcast. Usage: /broadcast <message>")
            return

        # Get all users
        users = load_users()
        success_count = 0
        failed_count = 0

        # Send confirmation
        confirm_msg = bot.send_message(chat_id, f"Broadcasting message to {len(users)} users...")

        # Send broadcast
        for user_id in users:
            try:
                bot.send_message(int(user_id), f"📢 *Announcement*\n\n{broadcast_text}", parse_mode="Markdown")
                success_count += 1
            except Exception as e:
                print(f"Failed to send broadcast to user {user_id}: {e}")
                failed_count += 1

        # Update confirmation message
        bot.edit_message_text(f"✅ Broadcast completed:\n• Sent to {success_count} users\n• Failed: {failed_count} users", chat_id, confirm_msg.message_id)
    except Exception as e:
        print(f"Error in broadcast_message: {e}")
        bot.send_message(chat_id, f"❌ Error broadcasting message: {str(e)}")

# Add questions
@bot.message_handler(commands=['add'], func=lambda message: message.from_user.id == ADMIN_ID)
def request_quiz_file(message):
    chat_id = message.chat.id

    instruction = (
        "📝 *Upload Quiz Questions*\n\n"
        "Please upload a text file with questions for one of the following subjects:\n"
        "• Agriculture\n"
        "• GK\n"
        "• Hindi\n\n"
        "File should be named as <subject>.txt (e.g., agriculture.txt)\n\n"
        "Format for each question:\n"
        "Q: Question text\n"
        "A: Option A\n"
        "B: Option B\n"
        "C: Option C\n"
        "D: Option D\n"
        "ANS: Correct option (A/B/C/D)\n\n"
        "Separate questions with a blank line."
    )

    bot.send_message(chat_id, instruction, parse_mode="Markdown")

# Handle quiz file upload
@bot.message_handler(content_types=['document'], func=lambda message: message.from_user.id == ADMIN_ID)
def process_quiz_file(message):
    chat_id = message.chat.id
    
    try:
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name.lower()

        # Check if file is for a valid subject
        valid_subjects = ["agriculture.txt", "gk.txt", "hindi.txt"]

        if file_name not in valid_subjects:
            bot.send_message(chat_id, "❌ Invalid file name. Please name your file as agriculture.txt, gk.txt, or hindi.txt.")
            return

        # Download file
        downloaded_file = bot.download_file(file_info.file_path)

        # Process file content
        content = downloaded_file.decode('utf-8')
        questions = parse_questions(content)

        if not questions:
            bot.send_message(chat_id, "❌ No valid questions found in the file. Please check the format.")
            return

        # Get subject name
        subject = file_name.replace(".txt", "").capitalize()
        if subject == "Gk":
            subject = "GK"

        # Add questions to the database
        quizzes = load_quizzes()

        # Ensure subject exists in quizzes
        if subject not in quizzes:
            quizzes[subject] = []

        # Check for duplicates and add new questions
        current_questions = quizzes[subject]
        added_count = 0
        duplicate_count = 0

        for new_question in questions:
            # Check if question already exists
            if not any(q.get("question") == new_question.get("question") for q in current_questions):
                current_questions.append(new_question)
                added_count += 1
            else:
                duplicate_count += 1

        # Save updated questions
        quizzes[subject] = current_questions
        save_quizzes(quizzes)

        # Send confirmation
        confirmation = (
            f"✅ *File Processed Successfully*\n\n"
            f"Subject: {subject}\n"
            f"Total questions in file: {len(questions)}\n"
            f"New questions added: {added_count}\n"
            f"Duplicates skipped: {duplicate_count}\n"
            f"Total questions now: {len(current_questions)}"
        )

        bot.send_message(chat_id, confirmation, parse_mode="Markdown")

        # Create updated file
        updated_file_content = ""
        for q in current_questions:
            if "question" in q and "options" in q and "correct" in q:
                updated_file_content += f"Q: {q['question']}\n"
                for option in ["A", "B", "C", "D"]:
                    if option in q['options']:
                        updated_file_content += f"{option}: {q['options'][option]}\n"
                updated_file_content += f"ANS: {q['correct']}\n\n"

        # Send updated file
        with open(f"updated_{file_name}", "w") as f:
            f.write(updated_file_content)

        with open(f"updated_{file_name}", "rb") as f:
            bot.send_document(chat_id, f, caption=f"📄 Updated {subject} questions file with {len(current_questions)} questions.")

        # Clean up
        os.remove(f"updated_{file_name}")
    except Exception as e:
        print(f"Error in process_quiz_file: {e}")
        bot.send_message(chat_id, f"❌ Error processing quiz file: {str(e)}")

# Function to parse questions from file
def parse_questions(content):
    questions = []
    current_question = None

    try:
        # Split content by lines
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                # Empty line, finish current question if exists
                if current_question and all(key in current_question for key in ["question", "options", "correct"]):
                    questions.append(current_question)
                current_question = None
            elif line.startswith("Q:"):
                # Start new question
                current_question = {
                    "question": line[2:].strip(),
                    "options": {}
                }
            elif current_question and line.startswith("A:"):
                if "options" not in current_question:
                    current_question["options"] = {}
                current_question["options"]["A"] = line[2:].strip()
            elif current_question and line.startswith("B:"):
                if "options" not in current_question:
                    current_question["options"] = {}
                current_question["options"]["B"] = line[2:].strip()
            elif current_question and line.startswith("C:"):
                if "options" not in current_question:
                    current_question["options"] = {}
                current_question["options"]["C"] = line[2:].strip()
            elif current_question and line.startswith("D:"):
                if "options" not in current_question:
                    current_question["options"] = {}
                current_question["options"]["D"] = line[2:].strip()
            elif current_question and line.startswith("ANS:"):
                correct = line[4:].strip()
                if correct in ["A", "B", "C", "D"]:
                    current_question["correct"] = correct

        # Add the last question if exists
        if current_question and all(key in current_question for key in ["question", "options", "correct"]):
            questions.append(current_question)
    except Exception as e:
        print(f"Error parsing questions: {e}")

    return questions

# Error handling
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        if user_id in user_state:
            if user_state[user_id] == "awaiting_utr":
                process_utr(message)
            elif user_state[user_id] == "input_name":
                process_name(message)
            elif user_state[user_id] == "verify_captcha":
                verify_captcha(message)
        else:
            # Check if user has already verified captcha and provided name
            if has_verified_captcha(user_id) and get_user_name(user_id):
                bot.send_message(chat_id, "Please use /start to access subscription options or /quiz to practice questions.")
            else:
                # Redirect to start
                start(message)
    except Exception as e:
        print(f"Error in handle_all_messages: {e}")
        bot.send_message(chat_id, "❌ An error occurred. Please try again.")

# Make sure assets directory exists
os.makedirs("assets", exist_ok=True)

# Start the bot
if __name__ == "__main__":
    print("Starting Quiz Master Bot...")
    try:
        # Make sure all required files exist
        if not os.path.exists('users.json'):
            with open('users.json', 'w') as f:
                json.dump({}, f)
            print("Created users.json file")

        if not os.path.exists('names.json'):
            with open('names.json', 'w') as f:
                json.dump({}, f)
            print("Created names.json file")

        if not os.path.exists('quizzes.json'):
            with open('quizzes.json', 'w') as f:
                json.dump({"Agriculture": [], "GK": [], "Hindi": []}, f)
            print("Created quizzes.json file")

        # Make sure the assets directory exists
        os.makedirs("assets", exist_ok=True)

        print("Bot is running...")
        bot.polling(none_stop=True, interval=1, timeout=30)
    except Exception as e:
        print(f"Error starting bot: {e}")
        # Try one more time with different polling parameters
        try:
            print("Retrying with different polling parameters...")
            bot.polling(none_stop=True, interval=2, timeout=60)
        except Exception as e2:
            print(f"Bot failed to start again: {e2}")