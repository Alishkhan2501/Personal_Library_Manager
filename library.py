import streamlit as st
import json
import os
import datetime
import time
import requests
import base64
import pandas as pd
from PIL import Image

# ---------------------- CONFIGURATION ----------------------
st.set_page_config(
    page_title="Library Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

BOOKS_FILE = "books.csv"
ISSUED_BOOKS_FILE = "issued_books.csv"
IMAGES_DIR = "book_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# ---------------------- STYLING FUNCTIONS ----------------------
def set_sidebar_style():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { background-color: #FFA500 !important; }
        [data-testid="stSidebarNav"], input, textarea, label, .stTextInput label,
        .stFileUploader label, .stTextInput div { color: white !important; }
        .stTextInput input {
            color: white !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
        }
        .fetching-text, h2, .gradient-text, .local-book-text, .api-book-text {
            color: white !important;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

def set_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
    <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .main-header {{
            text-align: center;
            font-size: 3rem;
            font-weight: 700;
            color: #000000;
            background-color: rgba(255, 255, 255, 0.5);
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            width: 70%;
            margin: 20px auto;
        }}
    </style>
    """, unsafe_allow_html=True)

# ---------------------- DATA FUNCTIONS ----------------------
def load_data():
    if os.path.exists(BOOKS_FILE):
        books_df = pd.read_csv(BOOKS_FILE)
    else:
        books_df = pd.DataFrame(columns=["BookID", "Title", "Author", "Status", "ImagePath"])

    if os.path.exists(ISSUED_BOOKS_FILE):
        issued_df = pd.read_csv(ISSUED_BOOKS_FILE)
    else:
        issued_df = pd.DataFrame(columns=["BookID", "Title", "IssuedTo", "Status"])
    return books_df, issued_df

def save_data(books_df, issued_df):
    books_df.to_csv(BOOKS_FILE, index=False)
    issued_df.to_csv(ISSUED_BOOKS_FILE, index=False)

# ---------------------- UI SECTIONS ----------------------
def add_book_ui(books_df):
    st.markdown('<h2 class="gradient-text">Add a New Book</h2>', unsafe_allow_html=True)
    book_id = st.text_input("Book ID")
    title = st.text_input("Title")
    author = st.text_input("Author")
    image = st.file_uploader("Upload Book Image", type=["jpg", "jpeg", "png"])
    
    if st.button("Add Book"):
        if book_id and title and author:
            image_path = None
            if image:
                image_path = os.path.join(IMAGES_DIR, f"{book_id}.{image.name.split('.')[-1]}")
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())

            new_book = {
                "BookID": book_id,
                "Title": title,
                "Author": author,
                "Status": "Available",
                "ImagePath": image_path
            }
            books_df = pd.concat([books_df, pd.DataFrame([new_book])], ignore_index=True)
            books_df.to_csv(BOOKS_FILE, index=False)
            st.success("Book added successfully!")
        else:
            st.error("Please fill all fields.")

def delete_book_ui(books_df):
    st.markdown('<h2 class="gradient-text">Delete a Book</h2>', unsafe_allow_html=True)
    book_id = st.text_input("Enter Book ID to Delete")
    if st.button("Delete Book"):
        if book_id and book_id in books_df["BookID"].values:
            book = books_df[books_df["BookID"] == book_id].iloc[0]
            if book["ImagePath"] and os.path.exists(book["ImagePath"]):
                os.remove(book["ImagePath"])
            books_df = books_df[books_df["BookID"] != book_id]
            books_df.to_csv(BOOKS_FILE, index=False)
            st.success("Book deleted successfully!")
        else:
            st.error("Invalid or missing Book ID.")
    return books_df

def issue_book_ui(books_df, issued_df):
    st.markdown('<h2 class="gradient-text">Issue a Book</h2>', unsafe_allow_html=True)
    book_id = st.text_input("Enter Book ID to Issue")
    issued_to = st.text_input("Issued To (User Name)")
    if st.button("Issue Book"):
        book = books_df[books_df["BookID"] == book_id]
        if not book.empty and book.iloc[0]["Status"] == "Available":
            books_df.loc[books_df["BookID"] == book_id, "Status"] = "Issued"
            new_issue = {
                "BookID": book_id,
                "Title": book.iloc[0]["Title"],
                "IssuedTo": issued_to,
                "Status": "Issued"
            }
            issued_df = pd.concat([issued_df, pd.DataFrame([new_issue])], ignore_index=True)
            save_data(books_df, issued_df)
            st.success("Book issued successfully!")
        else:
            st.error("Invalid Book ID or already issued.")

def return_book_ui(books_df, issued_df):
    st.markdown('<h2 class="gradient-text">Return a Book</h2>', unsafe_allow_html=True)
    book_id = st.text_input("Enter Book ID to Return")
    if st.button("Return Book"):
        if book_id in issued_df["BookID"].values:
            books_df.loc[books_df["BookID"] == book_id, "Status"] = "Available"
            issued_df = issued_df[issued_df["BookID"] != book_id]
            save_data(books_df, issued_df)
            st.success("Book returned successfully!")
        else:
            st.error("Book not issued.")
    return issued_df

def view_local_books(books_df):
    st.markdown('<h2 class="gradient-text">Local Books (Added by You)</h2>', unsafe_allow_html=True)
    if books_df.empty:
        st.info("No local books added yet.")
    else:
        for _, row in books_df.iterrows():
            st.markdown(f'<div class="local-book-text"><b>Book ID:</b> {row["BookID"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="local-book-text"><b>Title:</b> {row["Title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="local-book-text"><b>Author:</b> {row["Author"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="local-book-text"><b>Status:</b> {row["Status"]}</div>', unsafe_allow_html=True)
            if row["ImagePath"] and os.path.exists(row["ImagePath"]):
                st.image(row["ImagePath"], caption=row["Title"], width=150)
            st.write("---")

def view_api_books():
    st.markdown('<h2 class="gradient-text">Search and View Books from Open Library</h2>', unsafe_allow_html=True)
    query = st.text_input("Search for a book (e.g., Python, History, Fiction):")
    if query:
        st.markdown(f'<p class="fetching-text">Fetching books for: {query}</p>', unsafe_allow_html=True)
        response = requests.get(f"https://openlibrary.org/search.json?q={query}")
        if response.status_code == 200:
            books = response.json().get("docs", [])
            if books:
                for book in books:
                    title = book.get("title", "N/A")
                    author = book.get("author_name", ["N/A"])[0]
                    publish_year = book.get("first_publish_year", "N/A")
                    cover_id = book.get("cover_i")
                    key = book.get("key")

                    st.markdown(f'<div class="api-book-text"><b>Title:</b> {title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="api-book-text"><b>Author:</b> {author}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="api-book-text"><b>Publish Year:</b> {publish_year}</div>', unsafe_allow_html=True)
                    if cover_id:
                        st.image(f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg", width=150)
                    if key:
                        st.markdown(f"[View on Open Library](https://openlibrary.org{key})", unsafe_allow_html=True)
                    st.write("---")
            else:
                st.warning("No books found.")
        else:
            st.error("Failed to fetch books.")

# ---------------------- MAIN APP ----------------------
set_background("images/pngtree-open-book-on-a-table-in-library-with-bookshelves-in-the-picture-image_15755422.jpg")
set_sidebar_style()

st.markdown('<div class="main-header">📚 Library Management System</div>', unsafe_allow_html=True)

books_df, issued_df = load_data()

with st.sidebar:
    st.header("📚 Menu")
    menu = st.radio(
        "Choose an Option",
        ["Add Book", "Delete Book", "Issue Book", "Return Book", "View Local Books", "View API Books"],
        format_func=lambda x: f"📖 {x}"
    )

# Render selected section
if menu == "Add Book":
    add_book_ui(books_df)
elif menu == "Delete Book":
    books_df = delete_book_ui(books_df)
elif menu == "Issue Book":
    issue_book_ui(books_df, issued_df)
elif menu == "Return Book":
    issued_df = return_book_ui(books_df, issued_df)
elif menu == "View Local Books":
    view_local_books(books_df)
elif menu == "View API Books":
    view_api_books()
