import tempfile
import time

import streamlit as st
import streamlit_ext as ste

from face_cluster import FaceCluster

st.set_page_config(layout='wide')

# st.title("Any Face Clustering")
st.markdown("<h1 style='text-align: center; color: grey;'>x-face.ai photo clustering</h1>", unsafe_allow_html=True)
st.text(" ")
st.text("Upload Images of Multiple Faces (with AT LEAST 3 images of a particular face).")

uploaded_files = st.file_uploader("", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
st.session_state.clustered = False

no_of_files = len(uploaded_files)

if no_of_files > 0:
    placeholder = st.empty()
    placeholder.success("{} Images uploaded successfully!".format(no_of_files))
    time.sleep(3)
    placeholder.empty()
    fc = FaceCluster()

    progress_bar = st.progress(0)
    progress_step = 100 / no_of_files

    for idx, f in enumerate(uploaded_files):
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(f.read())
        fc.add_image(tfile.name)
        progress_bar.progress(int((idx + 1) * progress_step),
                              text=f"Processing image: {(idx + 1)} of {no_of_files} images")

    # converting the data into a numpy array
    if not st.session_state.clustered:
        fc.cluster_images()
        st.balloons()
        st.session_state.clustered = True

    st.subheader("Number of unique faces identified (excluding the unknown faces) is: " + str(fc.numUniqueFaces))

    container = st.container()

    # loop over the unique face integers
    for labelID, montage, whole_images in fc.get_faces_cluster():

        current_title = "Face #{}:".format(labelID + 1)
        expander_caption = "Images with Face #{}:".format(labelID + 1)
        current_title = "Unknown:" if labelID == -1 else current_title

        with container:
            col1, mid, col2, mid1, col3 = st.columns([1, 1, 1, 1, 16])
            with col1:
                st.write(current_title)
            with col2:
                st.image(montage)
            with col3:
                with open("zip_face#{}.zip".format(labelID + 1), "rb") as fp:
                    btn = st.download_button(
                        label="Download ZIP of clustered images with face #{}".format(labelID + 1),
                        data=fp,
                        file_name="clustered_faces#{}.zip".format(labelID + 1),
                        mime="application/zip"
                    )
                fp.close()
            with st.expander(expander_caption):
                # st.image(montage)
                st.write(expander_caption)
                cols2 = st.columns(3)
                for j in range(len(whole_images)):
                    with cols2[j % 3]:
                        st.image(whole_images[j], use_container_width='always')
