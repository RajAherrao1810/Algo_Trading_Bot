import streamlit as st

# Function to check credentials (dummy authentication for demonstration)
def authenticate(user_id, password):
    if user_id == "user@example.com" and password == "password123":
        return True
    else:
        return False

# Horizontal navigation bar
def navigation_bar():
    st.markdown("""
        <style>
        .nav {
            background-color: #f8f9fa;
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        .nav a {
            margin-right: 20px;
            color: black;
            text-decoration: none;
            font-weight: bold;
        }
        .nav a:hover {
            color: #007bff;
        }
        .nav img {
            float: right;
            height: 40px;
            width: 40px;
        }
        </style>
        <div class="nav">
            <a href="#">Home</a>
            <a href="#">Strategies</a>
            <a href="#">Orders</a>
            <a href="#">Account</a>
            <img src="https://img.icons8.com/ios-filled/50/000000/user.png" alt="Profile Logo">
        </div>
    """, unsafe_allow_html=True)

# Main function to handle the login and redirection to home page
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("Login Page")

        # Input fields for login
        user_id = st.text_input("Email ID or Client ID")
        password = st.text_input("Password", type="password")

        # Login button and authentication check
        if st.button("Login"):
            if authenticate(user_id, password):
                st.session_state['logged_in'] = True
                st.success("Login Successful! Redirecting to Home...")
            else:
                st.error("Invalid Email ID/Client ID or Password")
    else:
        # Display the home page
        st.title("Welcome to the Home Page!")
        navigation_bar()

        # Add any content for home page here
        st.write("This is the home page content after a successful login.")
        st.write("You can add more functionality here.")

# Run the main function
if __name__ == "__main__":
    main()