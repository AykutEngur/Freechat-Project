import streamlit as st
import base64
import mysql.connector
import time
from streamlit_option_menu import option_menu
import os
from datetime import datetime





st.set_page_config(
    page_title="Freechat",
    page_icon="🧊",
    layout="wide",
)

def get_base64_image(image_file):
    with open(image_file, "rb") as image:
        return base64.b64encode(image.read()).decode()

image_base64 = get_base64_image("freechat.png")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/png;base64,{image_base64});
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)





st.markdown(
    """
    <style>
    /* Change the sidebar's background color */
    .css-1d391kg {  /* Adjust this class based on your Streamlit version */
        background-color: #130234 !important; /* Your desired sidebar background color */
    }
    .sidebar .nav-link {
        color: #5714db !important;  /* Change the text color of the menu items */
    }
    .sidebar .nav-link.active {
        background-color: #5714db !important;  /* Active item background */
        color: white !important;  /* Active item text color */
    }
    .sidebar {
        background-color: #f0f0f5; /* Sidebar background color */
    }
    
    
    </style>
    """,
    unsafe_allow_html=True
)



# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "show_sign_in" not in st.session_state:
    st.session_state["show_sign_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

# MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="aykut1323",
    database="freechat_database"
)
my_cursor = mydb.cursor()




def display_footer():
    st.markdown(
        """
        <div style='position: fixed; top: 60px; right: 10px; color: gray; font-size: 13px;'>
            Developed by <strong>Aykut Engür</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

def sign_in_page():
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("<div style='margin: 60px 0;'></div>", unsafe_allow_html=True)
        st.subheader("Sign in to your account")
        with st.form("sign_in"):
            sign_in_username = st.text_input("Username")
            sign_in_password = st.text_input("Password", type="password")
            sign_in_button = st.form_submit_button("Sign In", use_container_width=True)

        if sign_in_button:
            my_cursor.execute("SELECT user_id FROM freechat_rg_table WHERE username = %s AND password = %s", (sign_in_username, sign_in_password))
            record = my_cursor.fetchone()
            if sign_in_username == "" or sign_in_password == "":
                st.error("All areas are necessary to sign in")
            elif record:
                st.session_state["authenticated"] = True
                st.session_state["username"] = sign_in_username
                st.session_state["user_id"] = record[0]
                st.success("Successfully signed in! Directing to the Home Page...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Incorrect username or password")

def register_page():
    st.markdown("<div style='margin: 60px 0;'></div>", unsafe_allow_html=True)
    st.subheader("Register to Freechat!")
    with st.form("registration"):
        rg_username = st.text_input("Username")
        rg_email = st.text_input("Email Address")
        rg_password = st.text_input("Password", type="password")
        criteria = [
            "• At least 8 characters",
            "• At least one uppercase letter",
            "• At least one special character (e.g., ?@!#%+-*_.)"
        ]
        
        st.markdown(
            "<div style='font-size: 12px; color: gray;'>" + "<br>".join(criteria) + "</div>",
            unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            has_agreed = st.checkbox("I agree to the License & User Agreement, which ensures that my data is secure and private.")
        registration_button = st.form_submit_button("Register", use_container_width=True)
        my_cursor.execute("SELECT * FROM freechat_rg_table")
        records = my_cursor.fetchall()
        usernames_list = [record[1] for record in records]
        emails_list = [record[2] for record in records]
        if registration_button:
            if rg_username == "" or rg_email == "" or rg_password == "":
                st.error("All areas must be filled")
            elif rg_username in usernames_list:
                st.error("This username is taken please select another username")
            elif rg_email in emails_list:
                st.error("This email already exists, please sign in or register with a new mail address")
            elif not (rg_email.endswith("@gmail.com") or rg_email.endswith("@hotmail.com") or rg_email.endswith(".com") or
                      rg_email.endswith("@yahoo.com") or rg_email.endswith("@edu.tr")):
                st.error("Please select a valid email address")
            elif len(rg_password) < 8:
                st.error("The password must include at least 8 characters")
            elif not any(char.isupper() for char in rg_password):
                st.error("The password must include at least one uppercase letter")
            elif not any(char in "?@!#%+-*_%." for char in rg_password):
                st.error("The password must have at least one special character")
            elif not has_agreed:
                st.error("You must agree to the License & User Agreement to register")
                
            else:
                sql = "INSERT INTO freechat_rg_table (username, email, password) VALUES (%s, %s, %s)"
                values = (rg_username, rg_email, rg_password)
                my_cursor.execute(sql, values)
                mydb.commit()
                st.success("Registration Successful! Directing to the Sign In page...")
                time.sleep(1)
                st.session_state["show_sign_in"] = True 
                st.rerun()

def display_friend_list():
    st.markdown("<h1 style='color: #AFA8BA;'>Your Friends</h1>", unsafe_allow_html=True)
    
    # Fetch friends data sorted by friendship date (latest first)
    my_cursor.execute("""
        SELECT friend_id, friendship_date FROM friends WHERE user_id = %s
        ORDER BY friendship_date DESC
    """, (st.session_state["user_id"],))
    friends_data = my_cursor.fetchall()

    if not friends_data:
        st.write("You have no friends yet. Start adding friends from the Find Friends page!")
        return

    # Limit to the latest 21 friends
    friends_data = friends_data[:21]

    # Display in three columns
    cols = st.columns(3)
    for index, (friend_id, friendship_date) in enumerate(friends_data):
        my_cursor.execute("SELECT username FROM freechat_rg_table WHERE user_id = %s", (friend_id,))
        friend_username = my_cursor.fetchone()
        if friend_username:
            with cols[index % 3]:  # Distribute across 3 columns
                # Use Markdown to set the color of the username
                st.markdown(f"<span style='color:#AFA8BA ;'>{friend_username[0]}</span> - Friends since {friendship_date.strftime('%d %B %Y')}", unsafe_allow_html=True)



def save_audio_file(audio_file, user_id):
    os.makedirs("audio_messages", exist_ok=True)
    # Create a unique filename using user_id and current timestamp
    timestamp = int(time.time())
    file_path = f"audio_messages/{user_id}_{timestamp}_{audio_file.name}"
    with open(file_path, "wb") as f:
        f.write(audio_file.getbuffer())
    return file_path


def send_audio_message(sender_id, receiver_id, audio_file):
    try:
        audio_url = save_audio_file(audio_file, sender_id)  # Save the audio file with a unique name
        sql = "INSERT INTO messages (sender_id, receiver_id, audio_url, message_type, timestamp) VALUES (%s, %s, %s, 'audio', NOW())"
        my_cursor.execute(sql, (sender_id, receiver_id, audio_url))
        mydb.commit()
        
        # Send notification after sending the message
        send_message_notification(receiver_id, sender_id)
        
        # Return the latest messages after sending the new one
        return fetch_latest_messages(sender_id, receiver_id)

    except Exception as e:
        st.error(f"Database error: {e}")


def fetch_latest_messages(sender_id, receiver_id):
    my_cursor.execute("""
        SELECT sender_id, audio_url, timestamp 
        FROM messages 
        WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp DESC LIMIT 5
    """, (sender_id, receiver_id, receiver_id, sender_id))
    
    return my_cursor.fetchall()




def display_messages(selected_friend):
    st.markdown(f"<h3 style='color: #AFA8BA;'>Chat with {selected_friend}</h3>", unsafe_allow_html=True)

    my_cursor.execute("SELECT user_id FROM freechat_rg_table WHERE username = %s", (selected_friend,))
    friend_record = my_cursor.fetchone()

    if not friend_record:
        st.error("Friend not found.")
        return
    
    friend_id = friend_record[0]

    # Fetch and display messages
    messages = fetch_latest_messages(st.session_state["user_id"], friend_id)

    for msg in reversed(messages):  # Display latest messages at the bottom
        sender = "You" if msg[0] == st.session_state["user_id"] else selected_friend
        timestamp = msg[2].strftime("%H:%M")

        alignment = 'right' if msg[0] == st.session_state["user_id"] else 'left'

        st.markdown(f"<div style='text-align: {alignment}; margin-top: 10px;'>"
                     f"<strong style='color: #AFA8BA;'>{sender}</strong>: <span style='color: #AFA8BA;'>{timestamp}</span></div>", 
                     unsafe_allow_html=True)

        # Display the audio message
        st.audio(msg[1], format='audio/wav')

    # Audio input section
    audio_input = st.experimental_audio_input("Record your voice message", label_visibility="collapsed")
    
    if audio_input is not None:
        st.session_state.audio_input = audio_input

        if st.button("Send Message"):
            try:
                messages = send_audio_message(st.session_state["user_id"], friend_id, audio_input)
                st.session_state.audio_input = None  # Clear the recorded audio input
                st.rerun()  # Refresh to show the new message
            except Exception as e:
                st.error(f"Error sending audio message: {e}")




def friends():
    st.subheader("")
    my_cursor.execute("SELECT friend_id FROM friends WHERE user_id = %s", (st.session_state["user_id"],))
    friends = my_cursor.fetchall()

    friend_usernames = []
    for friend in friends:
        my_cursor.execute("SELECT username FROM freechat_rg_table WHERE user_id = %s", (friend[0],))
        friend_record = my_cursor.fetchone()
        if friend_record:
            friend_usernames.append(friend_record[0])

    col1, col2 = st.columns([1, 2])  # Adjusted proportions for wider space
    with col1:
        st.markdown("<h2 style='color: #AFA8BA;'>Your Friends</h2>", unsafe_allow_html=True)
        selected_friend = st.selectbox("Select a friend to chat with:", friend_usernames, key="friend_select")

    with col2:
        if selected_friend:
            display_messages(selected_friend)



def find_friends():
    st.markdown("<h1 style='color: #AFA8BA;'>Find Friends</h1>", unsafe_allow_html=True)
    my_cursor.execute("SELECT user_id, username FROM freechat_rg_table WHERE user_id != %s", (st.session_state["user_id"],))
    users = my_cursor.fetchall()

    selected_friend = st.selectbox("Freechat Users", [username for _, username in users], key="add_friend_select")
    
    if st.button("Add Friend", key="add_friend_button"):
        friend_id = next(user[0] for user in users if user[1] == selected_friend)
        my_cursor.execute("SELECT * FROM friends WHERE user_id = %s AND friend_id = %s", (st.session_state["user_id"], friend_id))
        existing_friendship = my_cursor.fetchone()
        
        if existing_friendship:
            st.error(f"{selected_friend} is already your friend!")
        else:
            my_cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)", (st.session_state["user_id"], friend_id))
            my_cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)", (friend_id, st.session_state["user_id"]))
            mydb.commit()

            # Send notification for friend request
            send_friend_request_notification(friend_id, st.session_state["user_id"])
            st.success(f"{selected_friend} has been added to your friends list!")



def about_freechat():
        st.markdown(
        """
        <div style='font-size: 24px; color: #AFA8BA; margin-top: 70px; text-align: center;'>  <!-- Adjust font size, color, and margin -->
        <h2 style='font-weight: bold;color:#5714db;'>About Freechat</h2>  <!-- Bold heading -->

Freechat is a platform designed to bring people closer through the power of voice. Unlike traditional messaging apps, Freechat is all about authentic, 
real-time communication. Here, friends can easily find each other, connect, 
and build friendships, but with a twist—there are no text messages. The entire experience is voice-only, allowing for faster, more personal exchanges. 
Whether you’re catching up with an old friend or starting a new conversation, 
Freechat makes connecting simple and genuine by focusing on what truly matters: your voice.\n
This project was developed by <strong>Aykut Engür</strong>,  a computer science student with a passion for creating innovative digital experiences.

     
        """,
        unsafe_allow_html=True
    )




def send_message_notification(receiver_id, sender_id):
    sql = "INSERT INTO notifications (user_id, type, sender_id) VALUES (%s, 'message', %s)"
    my_cursor.execute(sql, (receiver_id, sender_id))
    mydb.commit()

    
def send_friend_request_notification(receiver_id, sender_id):
    sql = "INSERT INTO notifications (user_id, type, sender_id) VALUES (%s, 'friend_request', %s)"
    my_cursor.execute(sql, (receiver_id, sender_id))
    mydb.commit()

def fetch_notifications(user_id):
    sql = "SELECT type, sender_id, timestamp FROM notifications WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10"
    my_cursor.execute(sql, (user_id,))
    return my_cursor.fetchall()


    
def check_notifications():
    while True:
        time.sleep(2) 
        notifications = fetch_notifications(st.session_state["user_id"])
        # Update the frontend with new notifications
        update_notification_display(notifications)
        
def update_notification_display(notifications):
    for notification in notifications:
        st.markdown(f"- **{notification[0]}** from user ID {notification[1]} at {notification[2]}")


def display_notifications():
    notifications = fetch_notifications(st.session_state["user_id"])
    
    st.header("Notifications")  

    if notifications:
        current_time = datetime.now()

        for notification in notifications:
            notification_type = notification[0]
            sender_id = notification[1]
            timestamp = notification[2]

            # Fetch the username for the sender
            my_cursor.execute("SELECT username FROM freechat_rg_table WHERE user_id = %s", (sender_id,))
            sender_record = my_cursor.fetchone()
            sender_username = sender_record[0] if sender_record else "Unknown User"

            # Calculate the time difference
            time_difference = current_time - timestamp
            total_seconds = int(time_difference.total_seconds())

            # Convert total seconds to minutes and hours
            minutes, seconds = divmod(total_seconds, 60)
            hours, minutes = divmod(minutes, 60)

            # Create a time ago string based on the difference
            time_ago_parts = []
            if hours > 0:
                time_ago_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
            if minutes > 0:
                time_ago_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")

            time_ago = ' and '.join(time_ago_parts) if time_ago_parts else "just now"

            if notification_type == 'message':
                st.markdown(f"🔔 New message from <span style='color: #AFA8BA;'>{sender_username}</span> {time_ago} ago", unsafe_allow_html=True)
            elif notification_type == 'friend_request':
                st.markdown(f"🤝 Friend request from <span style='color: #AFA8BA;'>{sender_username}</span> {time_ago} ago", unsafe_allow_html=True)

    else:
        st.markdown("No new notifications.")




def fetch_user_audio_messages(user_id):
    my_cursor.execute("""
        SELECT sender_id, receiver_id, audio_url, timestamp 
        FROM messages 
        WHERE sender_id = %s OR receiver_id = %s
        ORDER BY timestamp DESC
        LIMIT 7
    """, (user_id, user_id))
    return my_cursor.fetchall()


def display_audio_messages(user_id):
    messages = fetch_user_audio_messages(user_id)
    
    for msg in messages:
        sender_id, receiver_id, audio_url, timestamp = msg
        sender = "You" if sender_id == user_id else "Friend"
        st.markdown(f"<strong>{sender}</strong>: {timestamp.strftime('%Y-%m-%d %H:%M')}")

        st.audio(audio_url, format='audio/wav')

        if st.button(f"Delete Message from {sender}", key=f"delete_{timestamp}"):
            delete_audio_message(audio_url)
            st.success("Message deleted.")
            st.rerun()  # Refresh the page to update the message list
def delete_audio_message(audio_url):
    # Delete the audio file from the server
    if os.path.exists(audio_url):
        os.remove(audio_url)

    # Remove the message from the database
    my_cursor.execute("DELETE FROM messages WHERE audio_url = %s", (audio_url,))
    mydb.commit()

    # Optionally, also delete the associated notification if needed
    # You may need to implement a way to link notifications to messages



def manage_messages(user_id):
    st.subheader("Manage Your Audio Messages")
    
    # Fetch audio messages sent by the user
    messages = fetch_user_audio_messages(user_id)

    if not messages:
        st.write("You have no audio messages.")
        return

    for msg in messages:
        sender_id, receiver_id, audio_url, timestamp = msg
        
        # Only show messages sent by the user
        if sender_id == user_id:
            formatted_timestamp = timestamp.strftime("%H:%M %d %B %Y")
            st.markdown(f"<strong>You</strong>: {formatted_timestamp}", unsafe_allow_html=True)

            # Display the audio
            st.audio(audio_url, format='audio/wav')

            # Provide a delete button
            if st.button(f"Delete Message", key=f"delete_{timestamp}"):
                delete_audio_message(audio_url)
                st.success("Message deleted.")
                st.rerun()  # Refresh to update the message list
        else:
            # Skip displaying messages received by the user
            continue




# Main App
if not st.session_state["authenticated"]:
    sign_in_option = st.radio("Select an option", ("Sign In", "Register"))
    if sign_in_option == "Sign In" or st.session_state["show_sign_in"]:
        sign_in_page()
    elif sign_in_option == "Register":
        register_page()
else:
    with st.sidebar:
        st.sidebar.markdown(f"<h2 style='font-weight: bold; color: #5714db;'>Welcome, {st.session_state['username']}!</h2>", unsafe_allow_html=True)
        menu = option_menu(
            menu_title=None,
            options=["Chats", "Friends", "Find Friends","Notifications","About Freechat", "Manage Messages"],
            icons=["chat", "person", "person-add","bell","info","info"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
               styles={
        "nav-link": {"color": "white"},
        "nav-link-selected": {"background-color": "#5714db", "color": "white"}
        
    }
        )
        st.sidebar.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        if st.sidebar.button("Logout"):
            st.session_state["authenticated"] = False
            st.session_state["show_sign_in"] = False
            st.rerun()
        display_footer()
    
    if menu == "Chats":
        friends()
        display_footer()
    elif menu == "Friends":
        display_friend_list()
        display_footer()
    elif menu == "Find Friends":
        find_friends()
        display_footer()
    elif menu == "About Freechat":
        about_freechat()
    elif menu == "Notifications":
        display_notifications()
    elif menu == "Manage Messages":
        manage_messages(st.session_state["user_id"])
