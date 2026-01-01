import os
import sys
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
from kivy.core.window import Window
from kivy.utils import platform

# Layout da interface em KV Language
KV = '''
MDScreen:
    md_bg_color: 0.1, 0.1, 0.1, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

        MDLabel:
            text: "Conversor de Áudio Pro"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H4"
            bold: True
            size_hint_y: None
            height: dp(50)

        MDLabel:
            id: label_file
            text: "Nenhum arquivo selecionado"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.8, 0.8, 0.8, 1
            font_style: "Body1"

        MDFillRoundFlatButton:
            text: "Selecionar Arquivo (M4A, WMA, WEBM)"
            pos_hint: {'center_x': 0.5}
            on_release: app.file_manager_open()

        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(10)
            size_hint_y: None
            height: dp(50)
            pos_hint: {'center_x': 0.5}
            
            MDLabel:
                text: "Converter para:"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                halign: "right"
            
            MDLabel:
                text: "MP3" 
                theme_text_color: "Custom"
                text_color: 0, 1, 0, 1
                bold: True
                halign: "left"

        MDFillRoundFlatButton:
            id: btn_convert
            text: "INICIAR CONVERSÃO"
            pos_hint: {'center_x': 0.5}
            md_bg_color: 0, 0.7, 0, 1
            on_release: app.convert_audio()
            disabled: True

        MDSpinner:
            id: spinner
            size_hint: None, None
            size: dp(46), dp(46)
            pos_hint: {'center_x': 0.5}
            active: False
            palette: [0.3, 0.3, 1, 1]

        MDLabel:
            id: status_label
            text: ""
            halign: "center"
            theme_text_color: "Error"
            markup: True
'''

class AudioConverterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,
            ext=['.m4a', '.wma', '.webm', '.wav', '.ogg', '.aac', '.flac', '.mp3']
        )
        self.selected_path = ""

    def file_manager_open(self):
        # No Android, começamos no diretório de armazenamento externo
        path = os.path.expanduser("~")
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            path = "/storage/emulated/0/"
        
        self.file_manager.show(path)
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        self.selected_path = path
        self.root.ids.label_file.text = f"Selecionado:\n{os.path.basename(path)}"
        self.root.ids.btn_convert.disabled = False
        self.root.ids.status_label.text = ""
        toast(path)

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def convert_audio(self):
        if not self.selected_path:
            return

        self.root.ids.spinner.active = True
        self.root.ids.btn_convert.disabled = True
        self.root.ids.status_label.text = "Convertendo..."
        
        # Executar em thread para não travar a UI
        import threading
        threading.Thread(target=self.run_ffmpeg).start()

    def run_ffmpeg(self):
        import subprocess
        
        input_file = self.selected_path
        filename = os.path.basename(input_file)
        name_without_ext = os.path.splitext(filename)[0]
        
        # Lógica de saída segura para Android 15
        output_dir = os.path.dirname(input_file)
        
        if platform == 'android':
            from android.storage import app_storage_path
            storage_path = app_storage_path()
            if storage_path:
                output_dir = storage_path

        output_file = os.path.join(output_dir, f"{name_without_ext}_convertido.mp3")

        # Comando FFmpeg
        ffmpeg_cmd = "ffmpeg"
        
        try:
            # -y sobrescreve se existir, -i input, output
            command = [ffmpeg_cmd, "-y", "-i", input_file, output_file]
            
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                msg = f"Sucesso!\nSalvo em:\n[size=12]{output_file}[/size]"
                self.update_status(msg, error=False)
            else:
                err_msg = stderr.decode('utf-8')
                self.update_status(f"Erro FFmpeg:\n{err_msg[-150:]}", error=True)

        except Exception as e:
            self.update_status(f"Erro Crítico: {str(e)}", error=True)

    def update_status(self, message, error=False):
        # Atualizar UI na thread principal
        def _update(dt):
            self.root.ids.spinner.active = False
            self.root.ids.btn_convert.disabled = False
            self.root.ids.status_label.text = message
            self.root.ids.status_label.theme_text_color = "Error" if error else "Custom"
            if not error:
                self.root.ids.status_label.text_color = (0, 1, 0, 1) # Verde
        
        from kivy.clock import Clock
        Clock.schedule_once(_update)

if __name__ == "__main__":
    AudioConverterApp().run()


