import base64
import streamlit as st
from openai import OpenAI, OpenAIError
from streamlit_cropperjs import st_cropperjs

# Set up page configuration
st.set_page_config(page_title="Scientific Image Analyst", layout="centered", initial_sidebar_state="collapsed")

# Streamlit page setup
st.title("🧪 Lesions Analyst: `GPT-4 Turbo with Vision` 👀")

# Input field for user to enter their OpenAI API key
api_key = st.text_input("Enter your OpenAI API Key", type="password")

if api_key:
    try:
        # Initialize the OpenAI client with the API key entered by the user
        client = OpenAI(api_key=api_key)

        # Function to encode the image to base64
        def encode_image(image_bytes):
            return base64.b64encode(image_bytes).decode("utf-8")

        # Input field for user to enter a custom prompt
        user_prompt = st.text_area("Enter your analysis prompt", height=150)

        # File uploader for the user to add their own image
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

        if uploaded_file:
            # Checkbox to ask user if they want to crop the image
            want_to_crop = st.checkbox("Do you want to crop the image?")

            if want_to_crop:
                # Display cropping tool for the uploaded image
                cropped_pic = st_cropperjs(pic=uploaded_file.getvalue(), btn_text="Crop Image", key="image_crop")
                if cropped_pic:
                    # Display the cropped image
                    st.image(cropped_pic, output_format="PNG")

                    # Button to download the cropped image
                    st.download_button(
                        label="Download Cropped Image",
                        data=cropped_pic,
                        file_name="cropped_image.png",
                        mime="image/png"
                    )

                    image_to_analyze = cropped_pic
            else:
                st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
                image_to_analyze = uploaded_file.getvalue()

            # Button to trigger the analysis
            analyze_button = st.button("Analyze the Image")

            if analyze_button:
                with st.spinner("Analyzing the image..."):
                    # Encode the image for analysis
                    base64_image = encode_image(image_to_analyze)

                    # Update the analysis prompt to include the user's prompt
                    prompt_text = user_prompt
                    # Create the payload for the completion request
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            ],
                        }
                    ]

                    # Make the request to the OpenAI API
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4-vision-preview", messages=messages, max_tokens=500
                        )
                        # Display the response in the app
                        st.markdown(response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

    except OpenAIError as e:
        # Handle invalid API key or other OpenAI-related errors
        st.error(f"An error occurred with the OpenAI service: {e}")

    except Exception as e:
        # Handle other exceptions
        st.error(f"An error occurred: {e}")
