import streamlit as st
import requests
import base64
from PIL import Image
import io
import os

# Set page config
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Title and description
st.title("AI Image Generator")
st.markdown("Generate images using OpenAI's GPT Image model")

# Get API URL from environment variable or use default
API_URL = os.getenv('API_URL', 'https://meepo-poc.vercel.app/')

# Input form
with st.form("image_generation_form"):
    prompt = st.text_area(
        "Enter your prompt",
        value="A children's book drawing of a veterinarian using a stethoscope to listen to the heartbeat of a baby otter.",
        height=100
    )
    
    # Use columns for layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        size = st.selectbox(
            "Image Size",
            options=["1024x1024", "1024x1792", "1792x1024"],
            index=0
        )
    with col2:
        n_images = st.number_input("Number of images", min_value=1, max_value=4, value=1)
    with col3:
        quality = st.selectbox(
            "Image Quality",
            options=["low", "medium", "high"],
            index=2
        )
    with col4:
        transparent = st.checkbox("Transparent Background", value=False)
    
    submit_button = st.form_submit_button("Generate Images")

# Process the form submission
if submit_button and prompt:
    with st.spinner("Generating images..."):
        try:
            # Make request to our Node.js service
            response = requests.post(
                f"{API_URL}/api/generate-image",
                json={
                    "prompt": prompt,
                    "size": size,
                    "n": n_images,
                    "quality": quality,
                    "transparent": transparent
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Display the generated images
                st.success("Images generated successfully!")
                
                # Create columns for the images
                cols = st.columns(min(n_images, 2))
                
                for idx, base64_image in enumerate(data["images"]):
                    # Convert base64 to image
                    image_data = base64.b64decode(base64_image.split(",")[1])
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Display image in the appropriate column
                    with cols[idx % 2]:
                        st.image(image, caption=f"Generated Image {idx + 1}")
                        # Create a download link
                        st.markdown(f"""
                        <a href="data:image/png;base64,{base64_image.split(',')[1]}" 
                           download="generated_image_{idx + 1}.png">
                           Download Image {idx + 1}
                        </a>
                        """, unsafe_allow_html=True)
            else:
                st.error(f"Error: {response.json().get('details', 'Failed to generate images')}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Add some helpful information
st.markdown("### Tips for writing good prompts")
st.markdown("""
- Be specific and detailed in your description
- Mention the style you want (e.g., "children's book style", "photorealistic", "cartoon")
- Include important details about the subject, setting, and mood
- Example: "A serene landscape with mountains and a lake at sunset, in the style of a watercolor painting"
""") 