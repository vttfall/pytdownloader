import customtkinter as ctk
from tkinter import PhotoImage, Menu
from pytube import YouTube
from pytd.utils import is_yt_url, seconds_to_time_format, get_progressive_media_formatted, get_only_videos_formatted, get_only_audios_formatted, get_output_dir
import requests
from PIL import Image
from sys import platform as op_system
from threading import Thread


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('assets/app_theme.json')

        self.title('Pytdownloader')
        self.geometry('670x390')
        self.resizable(False, False)

        if op_system.startswith('win'):
            self.iconbitmap('assets/app_icon.ico')
        else:
            self.wm_iconphoto(True, PhotoImage(file='assets/app_icon.png'))

        self.header_values = {
            "none": "Available media [ ... ]",
            "progressive": "Available media [ progressive ] [ video + audio ]",
            "adaptative": "Available media [ adaptative ] [ video ] [ audio ]"
        }

        self.fetch_header_label = ctk.CTkLabel(master=self, text="Fetch available media")
        self.fetch_frame = PytFetchFrame(master=self, height=68)

        self.media_header_text = ctk.StringVar()
        self.media_header_text.set(self.header_values['none'])
        self.media_frame = PytNoMediaFrame(master=self)

        self.media_header_label = ctk.CTkLabel(
            master=self,
            text=str(self.media_header_text),
            textvariable=self.media_header_text
        )

        self.fetch_header_label.pack(anchor=ctk.W, padx=10, pady=(10, 5))
        self.fetch_frame.pack(fill=ctk.X, padx=10)
        self.media_header_label.pack(anchor=ctk.W, padx=10, pady=(10, 5))
        self.media_frame.pack(fill=ctk.X, padx=10)


class PytNoMediaFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        ctk.CTkFrame.__init__(self, *args, **kwargs)

        self.media_content = ctk.CTkLabel(master=self, text="PytNoMediaFrame uwu")
        self.media_content.place(in_=self, x=0, y=0)


class PytMediaFrame(ctk.CTkFrame):
    def __init__(self, yt_obj: YouTube, *args, **kwargs):
        ctk.CTkFrame.__init__(self, *args, **kwargs)

        self.yt_obj = yt_obj
        self.thumbs_data = self.yt_obj.vid_info.get("videoDetails").get("thumbnail").get("thumbnails")[1]
        self.vc_mq_url = self.thumbs_data.get("url")

        self.img_req = requests.get(self.vc_mq_url, stream=True)
        self.thumb_img = Image.open(self.img_req.raw)

        self.preview_frame = ctk.CTkFrame(master=self)
        self.preview_frame.pack(side=ctk.LEFT, padx=(0, 10))

        self.vid_cover = ctk.CTkImage(light_image=self.thumb_img, size=(192, 108))
        self.vid_cover_label = ctk.CTkLabel(master=self.preview_frame, image=self.vid_cover, text="")
        self.vid_title_label = ctk.CTkLabel(master=self.preview_frame, text=self.yt_obj.title, wraplength=192, justify=ctk.LEFT)
        self.vid_author_label = ctk.CTkLabel(master=self.preview_frame, text=self.yt_obj.author, height=20)
        self.vid_date_label = ctk.CTkLabel(master=self.preview_frame, text=str(self.yt_obj.publish_date)[:10], height=20)
        self.vid_duration_label = ctk.CTkLabel(master=self.preview_frame, text=seconds_to_time_format(seconds=self.yt_obj.length), height=20)

        self.options_frame = ctk.CTkFrame(master=self)
        self.options_frame.pack(fill=ctk.BOTH, expand=1)

        self.pack(fill=ctk.X, padx=10)

        self.vid_cover_label.grid(padx=10, pady=10)
        self.vid_title_label.grid(padx=10, sticky=ctk.W)
        self.vid_author_label.grid(padx=10, sticky=ctk.W)
        self.vid_date_label.grid(padx=10, sticky=ctk.W)
        self.vid_duration_label.grid(padx=10, sticky=ctk.W)


class PytProgressiveFrame(PytMediaFrame):
    def __init__(self, *args, **kwargs):
        PytMediaFrame.__init__(self, *args, **kwargs)

        self.quality_label = ctk.CTkLabel(master=self.options_frame, text="Quality:", width=60, anchor=ctk.W)
        self.quality_opt_menu = ctk.CTkOptionMenu(
            master=self.options_frame,
            values=get_progressive_media_formatted(self.yt_obj),
            width=340
        )
        self.download_button = ctk.CTkButton(master=self.options_frame, text="Download", command=self.on_download_clicked)

        self.progress_label = ctk.CTkLabel(master=self.options_frame, text="Task")
        self.progress_bar = ctk.CTkProgressBar(master=self.options_frame, orientation="horizontal", height=16)
        self.progress_percent = ctk.CTkLabel(
            master=self.progress_bar,
            height=16,
            text="Download progress:   0%",
            bg_color="transparent",
        )
        self.progress_percent.place(in_=self.progress_bar, x=0, y=0)

        self.quality_label.grid(row=0, column=0, sticky=ctk.W, padx=(10, 10), pady=10)
        self.quality_opt_menu.grid(row=0, column=1, sticky=ctk.W, padx=(0, 10), pady=10)
        self.download_button.grid(row=1, columnspan=2, sticky=ctk.EW, padx=10, pady=0)

    def download_media(self) -> None:
        _itag = int(self.quality_opt_menu.get()[:3])
        self.yt_obj.streams.get_by_itag(_itag).download(output_path=get_output_dir())

    def on_download_clicked(self):
        self.download_button.configure(state="disabled")
        self.progress_label.grid(row=2, columnspan=2, sticky=ctk.EW, padx=10, pady=(10, 0))
        self.progress_bar.grid(row=3, columnspan=2, sticky=ctk.EW, padx=10, pady=(10, 0))
        self.progress_bar.set(0)

        self.yt_obj.register_on_progress_callback(self.on_download_in_progress)
        self.yt_obj.register_on_complete_callback(self.on_download_complete)
        Thread(target=self.download_media).start()

    def on_download_in_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_completed = int((bytes_downloaded / total_size) * 100)
        print(f'{percentage_completed}%')
        self.progress_bar.set(float(percentage_completed / 100))

    def on_download_complete(self, stream, file_path):
        self.download_button.configure(state="normal")
        print(file_path)
        print("Download succesfully completed c:")


class PytAdaptativeFrame(PytMediaFrame):
    def __init__(self, *args, **kwargs):
        PytMediaFrame.__init__(self, *args, **kwargs)

        self.video_cb = ctk.CTkCheckBox(master=self.options_frame, text="Video")
        self.video_op_menu = ctk.CTkOptionMenu(
            master=self.options_frame,
            values=get_only_videos_formatted(self.yt_obj),
            width=300
        )

        self.audio_cb = ctk.CTkCheckBox(master=self.options_frame, text="Audio")
        self.audio_op_menu = ctk.CTkOptionMenu(
            master=self.options_frame,
            values=get_only_audios_formatted(self.yt_obj),
            width=300
        )

        self.download_button = ctk.CTkButton(master=self.options_frame, text="Download & convert")

        self.video_cb.grid(row=0, column=0, sticky=ctk.W, padx=(10, 10), pady=(10, 0))
        self.video_op_menu.grid(row=0, column=1, sticky=ctk.W, padx=(0, 10), pady=(10, 0))
        self.audio_cb.grid(row=1, column=0, sticky=ctk.W, padx=(10, 10), pady=(10, 0))
        self.audio_op_menu.grid(row=1, column=1, sticky=ctk.W, padx=(0, 10), pady=(10, 0))
        self.download_button.grid(row=2, columnspan=2, sticky=ctk.EW, padx=10, pady=(10, 0))


class PytFetchFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        ctk.CTkFrame.__init__(self, *args, **kwargs)

        self.entry_url = ctk.CTkEntry(self, placeholder_text="Youtube Url", width=500)

        self.type_streams_to_fetch = ctk.CTkOptionMenu(
            master=self,
            values=['progressive', 'adaptative']
        )
        self.type_streams_to_fetch.set("progressive")

        self.fetch_button = ctk.CTkButton(
            master=self,
            text="Fetch media",
            command=self.fetch_button_clicked
        )

        self.entry_context_menu = Menu(self.entry_url, tearoff=0)
        self.entry_context_menu.add_command(label="Clear & paste", command=self.clear_and_paste_clipboard)
        # self.entry_context_menu.

        self.entry_url.bind("<Button-3>", lambda event: self.entry_context_menu.post(event.x_root, event.y_root))

        self.entry_url.place(x=0, y=0, anchor="nw")
        self.type_streams_to_fetch.place(relx=1, y=0, anchor="ne")
        self.fetch_button.place(relx=1, rely=1, anchor="se")

    def clear_and_paste_clipboard(self):
        self.entry_url.delete(0, ctk.END)
        self.entry_url.insert(0, self.master.clipboard_get())   # ctk.END

    def set_media_header(self, is_valid_yt_url: bool) -> None:
        """
        Function that assigns an appropiate media header label
        depending on download type selected when fetch button is clicked
        :param bool is_valid_yt_url: Boolean value
        """
        if is_valid_yt_url:
            match self.type_streams_to_fetch.get():
                case 'progressive':
                    self.master.media_header_text.set(self.master.header_values['progressive'])
                case 'adaptative':
                    self.master.media_header_text.set(self.master.header_values['adaptative'])
                case _:
                    pass
        else:
            self.master.media_header_text.set(self.master.header_values['none'])

    def set_media_frame(self, is_valid_yt_url: bool) -> None:
        """
        Function that assigns an appropiate media header label
        depending on download type selected when fetch button is clicked
        :param bool is_valid_yt_url: Boolean value
        """
        if is_valid_yt_url:
            match self.type_streams_to_fetch.get():
                case 'progressive':
                    self.master.media_header_text.set(self.master.header_values['progressive'])
                case 'adaptative':
                    self.master.media_header_text.set(self.master.header_values['adaptative'])
                case _:
                    pass
        else:
            self.master.media_header_text.set(self.master.header_values['none'])

    def fetch_button_clicked(self) -> None:
        url = self.entry_url.get()
        is_valid_url = is_yt_url(url)

        self.master.media_frame.destroy()
        if is_valid_url:
            try:
                youtube_object = YouTube(url)

                if self.type_streams_to_fetch.get() == "progressive":
                    self.master.media_frame = PytProgressiveFrame(master=self.master, yt_obj=youtube_object)
                elif self.type_streams_to_fetch.get() == "adaptative":
                    self.master.media_frame = PytAdaptativeFrame(master=self.master, yt_obj=youtube_object)

            except Exception as err:
                print(err)
        else:
            self.entry_url.delete(0, ctk.END)
            self.master.media_frame = PytNoMediaFrame(master=self.master)
            self.master.media_frame.pack(fill=ctk.X, padx=10)

        self.set_media_header(is_valid_url)
