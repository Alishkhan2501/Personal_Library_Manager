import streamlit as st
import json
import os
import datetime
import time
import requests
import base64
import pandas as pd
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Library Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to apply custom sidebar style
def set_sidebar_style():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background-color: #FFA500 !important; /* Sidebar background color */
            }
            [data-testid="stSidebarNav"] {
                color: #000000 !important; /* Sidebar text color */
                font-weight: bold;
            }
            input, textarea, label, .stTextInput label, .stFileUploader label, .stTextInput div {
                color: white !important;  /* Make all text in inputs and labels white */
            }
            .stTextInput input {
                color: white !important;  /* Make text in search box white */
                background-color: rgba(0, 0, 0, 0.5) !important; /* Optional: change background color */
            }

            /* New CSS for the white text color in 'Fetching books for' */
            .fetching-text {
                color: white !important;
                font-weight: bold;
            }

        </style>
        """,
        unsafe_allow_html=True
    )

# Function to set background image and custom styles
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    st.markdown(
        f"""
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
        .book-card {{
            background-color: rgba(255, 255, 255, 0.8);
            padding: 1rem;
            border-left: 5px solid #3b82f6;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }}
        .read-badge {{
            background-color: #10b981;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
        }}
        .unread-badge {{
            background-color: #f87171;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
        }}

        /* Gradient text color */
        .gradient-text {{
            background: linear-gradient(90deg, rgba(0,123,255,1) 0%, rgba(0,204,255,1) 100%);
            -webkit-background-clip: text;
            color: transparent;
            font-weight: bold;
        }}

        /* Make all headers text color white */
        h2, .gradient-text {{
            color: white !important;
        }}

        /* Style for input fields and labels */
        input, textarea, label, .stTextInput label, .stFileUploader label, .stTextInput div {{
            color: white !important;  /* Make all text in inputs and labels white */
        }}

        /* Make the text color of the local books white */
        .local-book-text {{
            color: white !important;
        }}

        /* Make the text color for API book search results white */
        .api-book-text {{
            color: white !important;
        }}

        /* Make 'Fetching books for' text white */
        .fetching-text {{
            color: white !important;
            font-weight: bold;
        }}

    </style>
    """,
    unsafe_allow_html=True
)

# Apply background and sidebar styles
set_background("images/pngtree-open-book-on-a-table-in-library-with-bookshelves-in-the-picture-image_15755422.jpg")
set_sidebar_style()

# File paths for data storage
BOOKS_FILE = "books.csv"
ISSUED_BOOKS_FILE = "issued_books.csv"
IMAGES_DIR = "book_images"

# Create directories if they don't exist
os.makedirs(IMAGES_DIR, exist_ok=True)

# Load or create CSV files
if os.path.exists(BOOKS_FILE):
    local_books_df = pd.read_csv(BOOKS_FILE)
else:
    local_books_df = pd.DataFrame(columns=["BookID", "Title", "Author", "Status", "ImagePath"])

if os.path.exists(ISSUED_BOOKS_FILE):
    issued_books_df = pd.read_csv(ISSUED_BOOKS_FILE)
else:
    issued_books_df = pd.DataFrame(columns=["BookID", "Title", "IssuedTo", "Status"])

# Sidebar for navigation
with st.sidebar:
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.header("📚 Menu")
    menu = st.radio(
        "Choose an Option",
        ["Add Book", "Delete Book", "Issue Book", "Return Book", "View Local Books", "View API Books"],
        format_func=lambda x: f"📖 {x}"  # Add icons to menu options
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Streamlit app
st.markdown(
    """
    <style>
        .main-header {
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
        }
    </style>
    <div class="main-header">
        📚 Library Management System
    </div>
    """, unsafe_allow_html=True
)

# Main content container
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Add Book (Local Books)
if menu == "Add Book":
    st.markdown('<h2 class="gradient-text">Add a New Book</h2>', unsafe_allow_html=True)
    book_id = st.text_input("Book ID")
    title = st.text_input("Title")
    author = st.text_input("Author")
    image = st.file_uploader("Upload Book Image", type=["jpg", "jpeg", "png"])
    
    if st.button("Add Book"):
        if book_id and title and author:
            # Save the uploaded image
            image_path = None
            if image:
                image_path = os.path.join(IMAGES_DIR, f"{book_id}.{image.name.split('.')[-1]}")
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())
            
            # Add book to the DataFrame
            new_book = {"BookID": book_id, "Title": title, "Author": author, "Status": "Available", "ImagePath": image_path}
            local_books_df = pd.concat([local_books_df, pd.DataFrame([new_book])], ignore_index=True)
            
            # Save to CSV
            local_books_df.to_csv(BOOKS_FILE, index=False)
            st.success("Book added successfully!")
        else:
            st.error("Please fill all fields.")

# Delete Book (Local Books)
elif menu == "Delete Book":
    st.markdown('<h2 class="gradient-text">Delete a Book</h2>', unsafe_allow_html=True)
    book_id = st.text_input("Enter Book ID to Delete")
    
    if st.button("Delete Book"):
        if book_id:
            # Check if the book exists
            if book_id in local_books_df["BookID"].values:
                # Remove the book from the DataFrame
                book = local_books_df[local_books_df["BookID"] == book_id].iloc[0]
                if book["ImagePath"] and os.path.exists(book["ImagePath"]):
                    os.remove(book["ImagePath"])  # Delete the image file
                local_books_df = local_books_df[local_books_df["BookID"] != book_id]
                
                # Save to CSV
                local_books_df.to_csv(BOOKS_FILE, index=False)
                st.success("Book deleted successfully!")
            else:
                st.error("Book not found.")
        else:
            st.error("Please enter a Book ID.")

# Issue Book (Local Books)
elif menu == "Issue Book":
    st.markdown('<h2 class="gradient-text">Issue a Book</h2>', unsafe_allow_html=True)
    book_id = st.text_input("Enter Book ID to Issue")
    issued_to = st.text_input("Issued To (User Name)")
    
    if st.button("Issue Book"):
        if book_id and issued_to:
            # Check if the book exists and is available
            book = local_books_df[local_books_df["BookID"] == book_id]
            if not book.empty:
                if book.iloc[0]["Status"] == "Available":
                    # Update book status
                    local_books_df.loc[local_books_df["BookID"] == book_id, "Status"] = "Issued"
                    
                    # Add to issued books DataFrame
                    new_issued_book = {
                        "BookID": book_id,
                        "Title": book.iloc[0]["Title"],
                        "IssuedTo": issued_to,
                        "Status": "Issued"
                    }
                    issued_books_df = pd.concat([issued_books_df, pd.DataFrame([new_issued_book])], ignore_index=True)
                    
                    # Save to CSV
                    local_books_df.to_csv(BOOKS_FILE, index=False)
                    issued_books_df.to_csv(ISSUED_BOOKS_FILE, index=False)
                    st.success("Book issued successfully!")
                else:
                    st.error("Book is already issued.")
            else:
                st.error("Book not found.")
        else:
            st.error("Please fill all fields.")

# Return Book (Local Books)
elif menu == "Return Book":
    st.markdown('<h2 class="gradient-text">Return a Book</h2>', unsafe_allow_html=True)
    book_id = st.text_input("Enter Book ID to Return")
    
    if st.button("Return Book"):
        if book_id:
            # Check if the book is issued
            issued_book = issued_books_df[issued_books_df["BookID"] == book_id]
            if not issued_book.empty:
                # Update book status
                local_books_df.loc[local_books_df["BookID"] == book_id, "Status"] = "Available"
                
                # Remove from issued books DataFrame
                issued_books_df.drop(issued_books_df[issued_books_df["BookID"] == book_id].index, inplace=True)
                
                # Save to CSV
                local_books_df.to_csv(BOOKS_FILE, index=False)
                issued_books_df.to_csv(ISSUED_BOOKS_FILE, index=False)
                st.success("Book returned successfully!")
            else:
                st.error("Book is not issued.")
        else:
            st.error("Please enter a Book ID.")

# View Local Books
elif menu == "View Local Books":
    st.markdown('<h2 class="gradient-text">Local Books (Added by You)</h2>', unsafe_allow_html=True)
    if not local_books_df.empty:
        for _, row in local_books_df.iterrows():
            st.markdown(f'<div class="local-book-text"><b>Book ID:</b> {row["BookID"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="local-book-text"><b>Title:</b> {row["Title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="local-book-text"><b>Author:</b> {row["Author"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="local-book-text"><b>Status:</b> {row["Status"]}</div>', unsafe_allow_html=True)
            if row["ImagePath"] and os.path.exists(row["ImagePath"]):
                st.image(row["ImagePath"], caption=row["Title"], width=150)
            st.write("---")
    else:
        st.info("No local books added yet.")

# View API Books (Google Books)
elif menu == "View API Books":
    st.markdown('<h2 class="gradient-text">Search and View Books from Open Library</h2>', unsafe_allow_html=True)
    search_query = st.text_input("Search for a book (e.g., Python, History, Fiction):")
    if search_query:
        # Display "Fetching books for..." text with white color
        st.markdown(f'<p class="fetching-text">Fetching books for: {search_query}</p>', unsafe_allow_html=True)
        
        # Make API request to Open Library
        response = requests.get(f"https://openlibrary.org/search.json?q={search_query}")
        if response.status_code == 200:
            data = response.json()
            books = data.get("docs", [])
            
            # Display fetched books
            if books:
                for book in books:
                    title = book.get("title", "N/A")
                    author = book.get("author_name", ["N/A"])[0]  # Get the first author
                    publish_year = book.get("first_publish_year", "N/A")
                    cover_id = book.get("cover_i", None)
                    openlibrary_key = book.get("key", None)
                    
                    st.markdown(f'<div class="api-book-text"><b>Title:</b> {title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="api-book-text"><b>Author:</b> {author}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="api-book-text"><b>Publish Year:</b> {publish_year}</div>', unsafe_allow_html=True)
                    
                    if cover_id:
                        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                        st.image(cover_url, caption=title, width=150)
                    
                    if openlibrary_key:
                        openlibrary_url = f"https://openlibrary.org{openlibrary_key}"
                        st.markdown(f"[View on Open Library]({openlibrary_url})", unsafe_allow_html=True)
                    
                    st.write("---")
            else:
                st.warning("No books found for your search query.")
        else:
            st.error("Failed to fetch books from the API.")
    else:
        st.info("Enter a search query to find books.")

st.markdown('</div>', unsafe_allow_html=True)