import tkinter
from tkinter import ttk, Label, Entry, Text, PhotoImage, simpledialog
import sv_ttk
import re 
import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
from googleapiclient.discovery import build

# Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set up YouTube Data API key
YOUTUBE_API_KEY = "AIzaSyDLBRVEAp8DSUl5ODdvB3wQyXN9hfFnxlw"  # Default value, will be updated by user input

# Function to set YouTube API Key
def set_api_key():
    global YOUTUBE_API_KEY
    new_api_key = simpledialog.askstring("Set YouTube API Key", "Enter your YouTube API Key:")
    if new_api_key:
        YOUTUBE_API_KEY = new_api_key

# Chatbot logic
def handle_response(user_input):
    user_input = user_input.lower()

    # Define responses
    greetings = ["hi", "hello", "hey"]
    farewells = ["bye", "goodbye", "see you later"]
    thanks = ["thanks", "thank you"]
    conversation = {
        "how are you": "I'm doing well, thanks for asking! How can I help you today?",
        "what's the weather like": "I don't have real-time weather information, but I can tell you it's usually sunny in California.",
        "anything else?": "Sure, what else would you like to know?"
    }
    math_keywords = ["calculate", "solve", "math", "add", "subtract", "multiply", "divide"]

    # Handle user input
    if user_input in greetings:
        return "Hello! How can I assist you today?"

    elif user_input in farewells:
        return "Goodbye! Have a great day."

    elif user_input in thanks:
        return "You're welcome!"

    elif user_input in conversation:
        return conversation[user_input]

    elif "how do i make a calculator" in user_input:
        return "To make a calculator in Python, you can use the Tkinter library to create a graphical user interface. You'll need to define buttons for the digits and operators, and implement the logic to perform calculations."

    elif "how do i use tkinter" in user_input:
        return "To use Tkinter, you first need to import the module: `import tkinter`. Then, you can create a Tkinter window by creating an instance of the `Tk()` class. You can add widgets such as buttons, labels, and entry fields to the window using various Tkinter classes like `Button`, `Label`, and `Entry`."

    # Check if the user input contains math-related keywords
    elif any(keyword in user_input for keyword in math_keywords):
        # Extract math expression using regular expression
        match = re.search(r'([-+]?\d*\.\d+|[-+]?\d+)\s*([-+*/])\s*([-+]?\d*\.\d+|[-+]?\d+)', user_input)
        if match:
            try:
                # Evaluate the math expression
                result = eval(match.group(0))
                return f"The result is: {result}"
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return "I'm sorry, I couldn't understand the math expression."

    elif "search for a song" in user_input:
        query = user_input.replace("search for a song", "").strip()
        if query:
            search_results = search_youtube(query)
            if search_results:
                # Extract video ID from the first search result
                first_video_id = search_results[0].split(": ")[-1].split("=")[-1]
                # Open the first search result in a web browser
                webbrowser.open(f"https://www.youtube.com/watch?v={first_video_id}")
                return "Playing the first search result."
            else:
                return f"Sorry, I couldn't find any results for '{query}'."
        else:
            return "Please provide a song name to search for."

    else:
        # Search Wikipedia for the provided topic
        try:
            summary = wikipedia.summary(user_input, sentences=2)
            return summary
        except wikipedia.exceptions.PageError:
            return "I'm sorry, I couldn't find information on that topic."

# Function to search for songs on YouTube
def search_youtube(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=query, part="snippet", maxResults=5, type="video")
    response = request.execute()
    search_results = []
    for item in response["items"]:
        video_title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        search_results.append(f"{video_title}: {video_url}")
    return search_results

# GUI functions
def get_user_input(event=None):
    send_message()

def update_chat_history(message, sender="You"):
    chat_history.insert(tkinter.END, f"{sender}: {message}\n")
    chat_history.see(tkinter.END)

def send_message():
    user_message = user_input_field.get().strip()
    if user_message:
        update_chat_history(user_message)
        response = handle_response(user_message)
        update_chat_history(response, sender="ZakChat")
        user_input_field.delete(0, tkinter.END)
        speak_response(response)

def change_theme():
    if sv_ttk.get_theme() == "dark":
        sv_ttk.set_theme("light")
    else:
        sv_ttk.set_theme("dark")

def listen_for_voice():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            user_input_field.delete(0, tkinter.END)
            user_input_field.insert(0, user_input)
            send_message()
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

def speak_response(response):
    engine.say(response)
    engine.runAndWait()

# Create the Tkinter window
root = tkinter.Tk()
root.title("BALTICHAT")

# Load the chatbot logo
chatbot_logo = PhotoImage(file="chatic.png")

# Create the chatbot logo label
logo_label = Label(root, image=chatbot_logo)
logo_label.grid(row=0, column=0, columnspan=2, pady=10)

# Create the chatbot widgets
welcome_label = Label(root, text="Welcome! How can I help you today?")
user_input_field = Entry(root, width=50, font=("Arial", 14))  # Increased font size for better visibility
chat_history = Text(root, height=15, width=50)  # Increased height for user input
send_button = ttk.Button(root, text="Send", command=send_message)
change_theme_button = ttk.Button(root, text="Change Theme", command=change_theme)
voice_button = ttk.Button(root, text="Speak", command=listen_for_voice)

# Grid the chatbot widgets
welcome_label.grid(row=1, column=0, columnspan=2, pady=5)
user_input_field.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
chat_history.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
send_button.grid(row=4, column=0, padx=5, pady=5)
change_theme_button.grid(row=4, column=1, padx=5, pady=5)
voice_button.grid(row=5, column=0, columnspan=2, pady=5)

# Configure row and column weights for resizing
root.rowconfigure(3, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
# Apply the initial theme
sv_ttk.set_theme("dark")

# Bind Enter key to send_message function
root.bind("<Return>", get_user_input)

# Run the Tkinter event loop
root.mainloop()
