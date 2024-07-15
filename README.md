## Introduction
v2v Helper is an [Automatic1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui/) extension to help to create AI videos, just a wrapper to [ffmpeg](https://github.com/XniceCraft/ffmpeg-colab.git) within a Colab environment.
It must be used paired with img2img batch tab.


## Installation
Inside A1111 extensions/ folder, run this command:
```
git clone https://github.com/scuti0/sd-webui-v2v-helper
```
Or paste this link in A1111 "Extensions" tab, then hit "install from url".

For windows, you must install ffmpeg separately: https://www.ffmpeg.org/download.html#build-windows

Don't forget to add ffmpeg \bin folder to your "Path" in Windows variables.

Obs.: if you use --share or --listen options in A1111 launch command line, don't forget to add --enable-insecure-extension-access, or [it could not work](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Extensions/f0258ac80df3176dbf9e900c5ad9d638f90b1923).


## Motivation

I've been using [mov2mov](https://github.com/Scholar01/sd-webui-mov2mov) for video2video works, it was an excellent extension, but it seems it will be no longer updated. 
So, I created a very rough extension to help in my current workflow process to create videos inside A1111.


## Advantages
- You can separate frames and remount your video after img2img processing inside A1111, without the need of running ffmpeg separately;
- Since you use img2img batch, you can create your video using extensions mov2mov does not support, like Adetailer.
- You can download your original and generated frames to process them in another program you like.


## Disadvantages
- It was inside a Google Colab environment. For example, you can use [SimpleSD](https://civitai.com/articles/2674/simplesd-stable-diffusion-colab-notebook) notebook. For windows, you must install [ffmpeg for Windows](https://www.ffmpeg.org/download.html#build-windows) separately.
- It's not possible to use different prompts to a specific range of frames. In this case, use mov2mov or any ComfyUI workflow that already implements this feature. 
  You can also divide your video in small semantic pieces, run img2img with a different prompt for each of them, then put everything together in any video software to combine them.


## Workflow / How to use
1. On v2v helper tab, upload your video and hit "Upload and Extract Frames" button;
2. After process, copy the input and output directories to img2img batch tab: just hit "Send to img2img" or you can use the small copy button in the upper right corner of textboxes;
3. Configure all your prompts, controlnets, adetailer or upscaling in img2img tab;
4. After img2img finishes processing, go back to v2v helper tab, select your desired fps, and then hit "Create Video";
5. Wait processing, then you can download your video!
6. If you want to download frames to backup or process in another program, you can download a .zip file with the button "Download frames", as an option after clicking "Clear all frames and data";
7. If you want to improve video quality, I recommend [TensorPix](https://app.tensorpix.ai/) site.
