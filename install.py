import os
import inspect
import subprocess
import sys
import configparser
from packaging import version

# current A1111 gradio version. 
# Update here for future changes in Automatic1111 (see requirements-versions.txt):
gradio_version = "3.41.2"

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
    parent_path = os.path.dirname(script_path) # use this on install.py
    base_dir = parent_path


def install_gradio(target_version=gradio_version):
    try:
        import gradio as gr
        if version.parse(gr.__version__) == version.parse(target_version):
            print(f"Gradio {target_version} is already installed.")
        else:
            print(f"Gradio version {gr.__version__} is installed. Installing version {target_version}...")
            subprocess.check_call([sys.executable, "-m", "pip", f"install", f"gradio=={target_version}"])
            import gradio as gr
            print(f"Gradio {target_version} has been installed.")
    except ImportError:
        print(f"Gradio is not installed. Installing version {target_version} now...")
        subprocess.check_call([sys.executable, "-m", "pip", f"install", f"gradio=={target_version}"])
        import gradio as gr
        print(f"Gradio {target_version} has been installed.")


def is_google_colab():
    try:
        import google.colab
        return True
    except ImportError:
        return False


def set_ffmpeg_installed_status(status):
    config = configparser.ConfigParser()
    config['INSTALLATION_STATUS'] = {'ffmpeg_installed': str(status)}
    # Ensure the base directory exists
    os.makedirs(base_dir, exist_ok=True)
    ini_path = os.path.join(base_dir, "install_status.ini")
    with open(ini_path, 'w') as configfile:
        config.write(configfile)


def check_ffmpeg_installed():
    config = configparser.ConfigParser()
    ini_path = os.path.join(base_dir, "install_status.ini")
    if not os.path.exists(ini_path):
        return False
    config.read(ini_path)
    return config.getboolean('INSTALLATION_STATUS', 'ffmpeg_installed', fallback=False)


def install_ffmpeg_colab():
    print('Installing ffmpeg-colab..')
    subprocess.call("git clone https://github.com/XniceCraft/ffmpeg-colab.git", shell=True)
    subprocess.call("chmod 755 ./ffmpeg-colab/install", shell=True)

    # Run the installation script
    install_return_code = subprocess.call("./ffmpeg-colab/install", shell=True)

    # Check the return code to determine if the installation was successful
    if install_return_code == 0:
        print('ffmpeg-colab installation finished.')
        set_ffmpeg_installed_status(True)
    else:
        print(f'ffmpeg-colab installation failed with return code: {install_return_code}')
        set_ffmpeg_installed_status(False)

    print('Cleaning ffmpeg-colab installation files..')
    subprocess.call("rm -fr ./ffmpeg-colab", shell=True)


def create_custom_css():

    # Ensure the base directory exists
    os.makedirs(base_dir, exist_ok=True)
    # Define the full path to the style.css file
    css_path = os.path.join(base_dir, "style.css")

    # Check if the style.css file already exists
    if not os.path.exists(css_path):
        print('Creating v2v-helper custom styles..')

        # custom css styles for this extension
        css_content = """
        #sd-webui-v2v-helper-label h2 { font-size: 14px; color: #75ff75; }
        #sd-webui-v2v-helper-label div div { font-size: 14px; color: #75ff75; }
        #sd-webui-v2v-helper-video { max-width: 512px; margin: auto; }
        """

        try:
            # Create and write to the style.css file
            with open(css_path, "w") as file:
                file.write(css_content)
            print('Custom styles created successfully.')
        except Exception as error:
            print(f"An error occurred: {error}")
    else:
        print('Custom v2v-helper styles already exist.')


# Install dependencies
if test_environment:
    install_gradio()

if is_google_colab():
    if not check_ffmpeg_installed():
        install_ffmpeg_colab()
    else:
        print('ffmpeg-colab is already installed.')
else:
    print('Non-Google Colab Unix-like system detected.')
    print('If you are using Windows, install ffmpeg separately first: https://www.ffmpeg.org/download.html#build-windows')
    print('Don\'t forget to add ffmpeg bin\\ folder to your "Path" in Windows system variables.')

# Create custom CSS styles
create_custom_css();
