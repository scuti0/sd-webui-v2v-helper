import os
import subprocess
import gradio as gr
import shutil
import zipfile
import inspect


# Set test_environment to False in a real Automatic1111 environment
# If true, it will create interface elements for testing purposes, and will mock img2img processing just downloading a pre-prepared set of frames.
test_environment = False
try:
    from modules import script_callbacks
except Exception as error:
    print(f"An error occurred importing A1111 script_callbacks: {error}")
    print("Setting environment to test mode..")
    test_environment = True

# Path to A1111 extension directory in test mode
base_dir = "/content/stable-diffusion-webui/extensions/sd-webui-v2v-helper/"
if not test_environment:
    # Get the current script path and its parents
    script_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
    parent_path = os.path.dirname(script_path)
    grandparent_path = os.path.dirname(parent_path) # use this on v2v-helper.py
    base_dir = grandparent_path


# Define folders
frames_dir = os.path.join(base_dir,"video_frames")
frames_generated_dir = os.path.join(base_dir,"video_frames_generated")
input_video_dir = os.path.join(base_dir,"input_video")
output_video_dir = os.path.join(base_dir,"output_video")
# external CSS file
css_dir = os.path.join(base_dir, "style.css")



# Ensure the work directories exists
def create_directories():
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(frames_generated_dir, exist_ok=True)
    os.makedirs(input_video_dir, exist_ok=True)
    os.makedirs(output_video_dir, exist_ok=True)



# Remove work directories
def remove_directories():
    shutil.rmtree(frames_dir)
    shutil.rmtree(frames_generated_dir)
    shutil.rmtree(input_video_dir)
    shutil.rmtree(output_video_dir)



# Save the uploaded video to input directory
def save_video(videofile):
    try:
        if videofile is not None:
            # Check if the file is an mp4
            if videofile.name.endswith('.mp4'):
                print(f"Saving video: {videofile.name}")
                video_path = os.path.join(input_video_dir,"input.mp4" )
                shutil.copyfile(videofile.name, video_path)
                print(f"Video saved to {video_path}..")
                return video_path
            else:
                raise Exception("The uploaded file is not an mp4.")
        else:
            raise Exception("No video file uploaded.")
    except Exception as error:
        print("An exception occurred:", error)
        raise error



# Rename frame files to a simpler format, to use in ffmpeg
def rename_files(directory):
    # Get a list of all files in the directory
    files = os.listdir(directory)

    # Iterate through each file
    for filename in files:
        # Split the filename into parts using "-"
        parts = filename.split("-")

        # Check if the filename has the pattern we're looking for
        if len(parts) == 2 and parts[1].startswith("frame"):
            # Extract the part before the "-"
            prefix = parts[0]
            # Extract the part after the "-"
            suffix = parts[1].split(".")[1]  # Extracting the file extension

            # Form the new filename
            new_filename = f"{prefix}.{suffix}"

            # Construct the full path for both old and new filenames
            old_filepath = os.path.join(directory, filename)
            new_filepath = os.path.join(directory, new_filename)

            # Rename the file
            os.rename(old_filepath, new_filepath)
            #print(f"Renamed '{filename}' to '{new_filename}'")



# Mock img2img batch: download frames.zip and unzip for testing purposes
def download_and_unzip_frames(url, target_directory):
    try:
        # Download frames.zip using wget
        wget_command = f"wget -c {url} -P {target_directory}"
        subprocess.call(wget_command, shell=True)

        target_file = os.path.join(target_directory, "frames.zip");

        # Unzip frames.zip
        unzip_command = f"unzip {target_file} -d {target_directory}"
        subprocess.call(unzip_command, shell=True)

        # Remove frames.zip
        rm_command = f"rm {target_file}"
        subprocess.call(rm_command, shell=True)

        print("img2img mocked: frames downloaded, extracted, and zip file removed successfully..")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False



# Extract frames from video
def extract_frames(videofile):
    try:
        create_directories();

        # Saves video in directory
        video_path = save_video(videofile)

        file_path_pattern = os.path.join(frames_dir,"frame%4d.png")

        print('Extracting frames..')

        command = f"ffmpeg -i {video_path} -r 25 -start_number 0001 {file_path_pattern}"
        print(command)

        return_code = subprocess.call(command, shell=True)
        if return_code == 0:
            print('Frames extracted successfully..')
        else:
            raise Exception("Could't extract frames with ffmpeg.")

        return ["Frames extracted successfully..", gr.update(visible=True),
                gr.update(visible=True), gr.update(visible=True),
                gr.update(visible=True), gr.update(visible=True),
                gr.update(visible=True), gr.update(visible=True)]

    except Exception as error:

        print("An exception occurred:", error)
        return [f"An exception occurred: {error}", gr.update(visible=False),
                gr.update(visible=False), gr.update(visible=False),
                gr.update(visible=False), gr.update(visible=False),
                gr.update(visible=False), gr.update(visible=False)]



# Combine frames to video
def combine_frames(fps):
    try:
        print("Frames per second selected:",fps);

        # Mock as if img2img process was finished - just for test purposes
        if test_environment:
            print('Mocking img2img process..')
            url = "https://huggingface.co/datasets/scuti0/extension-test/resolve/main/frames.zip"
            download_and_unzip_frames(url, frames_generated_dir)

        rename_files(frames_generated_dir)
        print('Files renamed..')

        print('Creating video..')

        frames_generated_pattern =  os.path.join(frames_generated_dir,"0%4d.png")
       
        output_video_path = os.path.join(output_video_dir,"out.mp4")

        command = f"ffmpeg -r 30 -framerate 5 -start_number 0000 -i \"{frames_generated_pattern}\" -c:v libx264 -vf \"fps={fps},format=yuv420p\" \"{output_video_path}\""
        print(command)

        return_code = subprocess.call(command, shell=True)
                        
        # Check the return code to determine if the installation was successful
        if return_code == 0:
            print('Video created successfully..')
        else:
            raise Exception("Could't create video with ffmpeg.")              
        
        return ["Video created successfully..",
                gr.update(value=output_video_path,visible=True),
                gr.update(visible=False), gr.update(visible=False)]

    except Exception as error:
        print("An exception occurred:", error)
        return [f"An exception occurred: {error}", gr.update(visible=False),
                gr.update(visible=True), gr.update(visible=True)]



# Clear frames after job
def clear_frames():
    try:
        remove_directories();
        create_directories();
        print('Frames cleared successfully..')
        return ["Frames cleared successfully..",
            gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False),
            gr.update(value=None)]
    except Exception as error:
        print("An exception occurred:", error)
        return f"An exception occurred: {error}"



# Download .zip of generated and original frames
def download_zip_frames():
    # Create a zip file
    zip_filename = os.path.join(output_video_dir,"frames.zip")
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        # zip generated frames
        for root, dirs, files in os.walk(frames_generated_dir):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(frames_generated_dir, '..')))
        # zip original frames
        for root, dirs, files in os.walk(frames_dir):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(frames_dir, '..')))

    return [gr.update(value=zip_filename, visible=True), gr.update(visible=False)]



# load custom css for testing purposes
def load_custom_css(file_path=css_dir):
    custom_css = ""
    try:
        with open(file_path, 'r') as file:
            custom_css = file.read()
        print("File content successfully loaded into custom_css.")
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except IOError:
        print(f"Error: An I/O error occurred while reading the file at {file_path}.")
    return custom_css



# adds a slash in end of path for img2img tab
def add_slash(input_path):
    if not input_path.endswith(os.path.sep):
        input_path += os.path.sep
    return input_path



# Create the Gradio interface
def on_ui_tabs():

    with gr.Blocks(analytics_enabled=False,
                   css=load_custom_css() if test_environment else "") as ui_component:

        # add components
        with gr.Row():
            output_text = gr.Textbox(label="Output message:", interactive=False)

        with gr.Row():
            video_input = gr.File(label="Drop your .mp4 video here:", type="file") #change to "filepath" when gradio 4.x
            upload_button = gr.Button("Upload and Extract Frames")

        # add components initially hidden
        with gr.Row():
            label_text = "Please copy these paths to img2img batch input/output directories, or just click 'Send to img2img batch' button:"
            label = gr.Label(value=label_text,
                             label="Message",
                             visible=False,
                             elem_id="sd-webui-v2v-helper-label")
            textbox1 = gr.Textbox(value=add_slash(frames_dir),
                                  label="img2img batch input directory",
                                  lines=4, show_label=True,
                                  interactive=False,
                                  visible=False,
                                  show_copy_button=True)
            textbox2 = gr.Textbox(value=add_slash(frames_generated_dir),
                                  label="img2img batch output directory",
                                  lines=4, show_label=True,
                                  interactive=False,
                                  visible=False,
                                  show_copy_button=True)
            send_button = gr.Button("Send to img2img batch", visible=False)

        with gr.Row():
            fps = gr.Slider(8, 30, value=30, step=2, label="Frames per second", show_label=True, visible=False)
            create_video_button = gr.Button("Create Video", visible=False)
            video_generated = gr.PlayableVideo(visible=False, format="mp4", elem_id="sd-webui-v2v-helper-video")

        with gr.Row():
            clear_button = gr.Button("Clear all frames and data", visible=False)
            confirm_btn = gr.Button("Confirm delete? You will lose your previous work!", variant="stop", visible=False)
            cancel_btn = gr.Button("Cancel", visible=False)
            download_zip_btn = gr.Button("Download frames", visible=False)
            output_zip = gr.File(label="Download original/generated frames as .zip file", visible=False)

        # add components just for test purposes, avoiding javascript errors
        if test_environment:
            with gr.Row():
                # testing send img2img
                img2img_input = gr.Textbox(label="Mock img2img input:",
                                           value="testeinput",
                                           elem_id="img2img_batch_input_dir",
                                           visible=True,
                                           interactive=True)
                img2img_output = gr.Textbox(label="Mock img2img output:",
                                            value="testeoutput",
                                            elem_id="img2img_batch_output_dir",
                                            visible=True,
                                            interactive=True)
            with gr.Row():
                gr.Button("txt2img", elem_classes="tab-nav");
                gr.Button("img2img", elem_classes="tab-nav");
                gr.Button("btn1", elem_id="mode_img2img");
                gr.Button("btn2", elem_id="mode_img2img");
                gr.Button("btn3", elem_id="mode_img2img");
                gr.Button("btn4", elem_id="mode_img2img");
                gr.Button("btn5", elem_id="mode_img2img");
                gr.Button("btn6", elem_id="mode_img2img");

        # add events

        # send directories to img2img inputs
        send_button.click(None, inputs=[textbox1,textbox2], outputs=[], _js="""
                function(textbox1,textbox2) {
                    function triggerChangeEvent(textarea) {
                        textarea.focus();
                        var currentValue = textarea.value;
                        textarea.value = currentValue + ' ';
                        var inputEvent = new Event('input', { bubbles: true });
                        textarea.dispatchEvent(inputEvent);
                        textarea.value = currentValue;
                        textarea.dispatchEvent(inputEvent);
                        var changeEvent = new Event('change', { bubbles: true });
                        textarea.dispatchEvent(changeEvent);
                        textarea.blur();
                        var blurEvent = new Event('blur', { bubbles: true });
                        textarea.dispatchEvent(blurEvent);
                    }

                    var tabButtons = document.querySelectorAll('.tab-nav button');
                    if (tabButtons.length > 1) {
                        tabButtons[1].click();
                    }
                    var modeButtons = document.querySelectorAll('#mode_img2img button');
                    if (modeButtons.length > 5) {
                        modeButtons[5].click();
                    }

                    var inputTextarea = document.querySelector('#img2img_batch_input_dir textarea');
                    var outputTextarea = document.querySelector('#img2img_batch_output_dir textarea');

                    // Set the value for the input and output directories
                    inputTextarea.value = textbox1;
                    outputTextarea.value = textbox2;

                    triggerChangeEvent(inputTextarea);
                    triggerChangeEvent(outputTextarea);
                }
            """)

        upload_button.click(fn=extract_frames,
                            inputs=video_input,
                            outputs=[output_text, label,
                                     textbox1, textbox2,
                                     send_button, fps,
                                     create_video_button, clear_button])

        create_video_button.click(fn=combine_frames,
                                  inputs=[fps],
                                  outputs=[output_text,video_generated,
                                           fps,create_video_button]);

        clear_button.click(lambda :[gr.update(visible=False),
                                    gr.update(visible=True),
                                    gr.update(visible=True),
                                    gr.update(visible=True)],
                                    None, [clear_button, confirm_btn, cancel_btn, download_zip_btn])

        cancel_btn.click(lambda :[gr.update(visible=True),
                                  gr.update(visible=False),
                                  gr.update(visible=False),
                                  gr.update(visible=False),
                                  gr.update(visible=False)],
                                  None, [clear_button, confirm_btn, cancel_btn, download_zip_btn, output_zip])

        download_zip_btn.click(fn=download_zip_frames,
                               inputs=[],
                               outputs=[output_zip,download_zip_btn])

        confirm_btn.click(fn=clear_frames,
                          inputs=[],
                          outputs=[output_text, label, textbox1,
                                   textbox2, send_button, fps, create_video_button,
                                   video_generated, clear_button, confirm_btn,
                                   cancel_btn, download_zip_btn, output_zip,
                                   video_input])

        return [(ui_component, "v2v Helper", "v2v_helper_tab")]

if test_environment:
    # Get the UI component
    demo = on_ui_tabs()[0][0]
    # Launch the UI
    demo.launch(share=True,debug=True)
else:
    # call extension gradio ui in Automatic1111
    script_callbacks.on_ui_tabs(on_ui_tabs)
