import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

# Set Streamlit page configuration
st.set_page_config(
    page_title="Web Chat Analyzer",
    page_icon=":speech_balloon:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set custom background color and styling for the sidebar
st.markdown(
    """
    <style>
        body {
            background-color: skyblue; /* Light gray background */
        }
        .stApp {
            background-color: skyblue; /* Light gray background */
        }
        .sidebar .sidebar-content {
            background-color: #1E2A38; /* Dark teal */
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
            border-radius: 10px; /* Rounded corners */
        }
        .sidebar .css-2trqyj {
            color: #FFFFFF; /* White text */
        }
        .block-container {
            background-color: #d2b4de; /* Change to skyblue or any desired color */
            padding: 1.4rem; /* Adjust the padding as needed */
            border-radius: 10px; /* Rounded corners */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Web Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

       # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'].values, timeline['message'].values, color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)


        # Assuming 'daily_timeline' is defined before this point in your code

        # Print unique values in 'only_date' for inspection
        if 'daily_timeline' in locals():
            print("Unique values in 'only_date' before conversion:", daily_timeline['only_date'].unique())
        else:
            print("'daily_timeline' is not defined before attempting to print unique values.")

        # Convert 'only_date' to datetime with specified format
        if 'daily_timeline' in locals():
            daily_timeline['only_date'] = pd.to_datetime(daily_timeline['only_date'], errors='coerce', format='%Y-%m-%d')

            # Drop rows with NaT (Not a Time) values
            daily_timeline = daily_timeline.dropna(subset=['only_date'])

            # Confirm changes
            print("Unique values in 'only_date' after conversion:", daily_timeline['only_date'].unique())
        else:
            print("'daily_timeline' is not defined before attempting to convert and drop.")

        # Plotting
        if 'daily_timeline' in locals():
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#2ecc71')  # Streamlit green
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            print("'daily_timeline' is not defined before attempting to plot.")
            
        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(busy_day.index, busy_day.values, color='#9b59b6')  # Purple
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(busy_month.index, busy_month.values, color='#e67e22')  # Orange
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 8))
        ax = sns.heatmap(user_heatmap, cmap='YlGnBu')  # Yellow to Blue
        st.pyplot(fig)

        # Finding the busiest users in the group (Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots(figsize=(10, 6))

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='#e74c3c')  # Red
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # Most common words
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(most_common_df[0], most_common_df[1], color='#3498db')  # Streamlit blue
        plt.xticks(rotation='horizontal')
        st.title('Most Common Words')
        st.pyplot(fig)

        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(df_wc, interpolation='bilinear')
        st.pyplot(fig)
        #st.title("Word Cloud")

        # Combine all messages into a single string
        #all_messages = " ".join(df[df['user'] == selected_user]['message'].values)

        # Debugging statements
        #print(f"Number of messages for {selected_user}: {df[df['user'] == selected_user].shape[0]}")
        #print(f"All messages: {all_messages}")

        # Check if there are non-whitespace characters in all_messages
        #if all_messages.strip():
            # Generate the word cloud
            #wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_messages)

            # Display the word cloud using Streamlit
            #st.image(wordcloud.to_array(), use_container_width=True)
        #else:
            #st.warning("No words to generate a word cloud.")
       

         # Emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots(figsize=(8, 8))
    
            emoji_df_head = emoji_df.head()
    
            # Check if the DataFrame has at least two columns
            if emoji_df_head.shape[1] >= 2:
                ax.pie(emoji_df_head.iloc[:, 1], labels=emoji_df_head.iloc[:, 0], autopct="%0.2f", colors=sns.color_palette('pastel'))
                st.pyplot(fig)
            else:
                st.warning("The DataFrame does not have enough columns for plotting.")
