import streamlit as st
from streamlit_option_menu import option_menu


def get_ltp_data():
    return {
        'NIFTY': 17580.35,
        'BANKNIFTY': 39425.70,
        'FINNIFTY': 18652.55,
        'MIDCPNIFTY': 13284.10,
        'SENSEX': 58923.43,
        'BANKEX':61166.36
    }


def show_home_page():
    
    ltp_data = get_ltp_data()

    # Custom CSS for the border and text style
    custom_css = """
        <style>
        .custom-column {
            border: 2px solid #4CAF50; /* Green border */
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            margin: 0px;
        }
        .small-text {
            font-size: 14px;
        }
        .small-header {
            font-size: 16px;
            font-weight: bold;
        }
        </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # Create grid layout with smaller column text sizes and border
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown("<div class='custom-column'><div class='small-header'>NIFTY</div><div class='small-text'>LTP: {}</div></div>".format(ltp_data['NIFTY']), unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='custom-column'><div class='small-header'>BANKNIFTY</div><div class='small-text'>LTP: {}</div></div>".format(ltp_data['BANKNIFTY']), unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='custom-column'><div class='small-header'>FINNIFTY</div><div class='small-text'>LTP: {}</div></div>".format(ltp_data['FINNIFTY']), unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='custom-column'><div class='small-header'>MIDCPNIFTY</div><div class='small-text'>LTP: {}</div></div>".format(ltp_data['MIDCPNIFTY']), unsafe_allow_html=True)

    with col5:
        st.markdown("<div class='custom-column'><div class='small-header'>SENSEX</div><div class='small-text'>LTP: {}</div></div>".format(ltp_data['SENSEX']), unsafe_allow_html=True)

    with col6:
        st.markdown("<div class='custom-column'><div class='small-header'>BANKEX</div><div class='small-text'>LTP: {}</div></div>".format(ltp_data['BANKEX']), unsafe_allow_html=True)




def navigation_bar():
    with st.sidebar:
        selected=option_menu(
            menu_title=None,
            options=['Home','Strategies','Orders','Account'], 
            icons=['house','alt','bookmark-dash','person-circle'],
            default_index=0,
            
        )
    if selected=='Home':
        show_home_page()
    elif selected=='Strategies':
        st.title("You have selected Strategies")
    elif selected=='Orders':
        st.title("You have selected Orders")
    else:
        st.title("You have selected Account")



def main():
    navigation_bar()

        # Add any content for home page here
    #st.write("This is the home page content after a successful login.")
    #st.write("You can add more functionality here.")


# Main function to handle the login and redirection to home page


# Run the main function
if __name__ == "__main__":
    main()