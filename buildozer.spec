[app]

# (str) Title of your application
title = AudioConverter

# (str) Package name
package.name = audioconverter

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.3

# (list) Application requirements
# Usando KivyMD master para compatibilidade e ffmpeg
requirements = python3,kivy==2.3.0,https://github.com/kivymd/KivyMD/archive/master.zip,pillow,ffmpeg,openssl

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET

# (int) Target Android API
android.api = 34

# (int) Minimum API
android.minapi = 21

# --- CORREÇÃO CRÍTICA AQUI ---
# NDK 25b quebra o FFmpeg. Usamos o 23c que é a versão LTS estável para bibliotecas C.
android.ndk = 23c

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Bootstrap to use for android builds
p4a.branch = master

# (str) Architecture to build for
# Vamos focar nas arquiteturas modernas para evitar erros de compilação em 32bits
android.archs = arm64-v8a

# (bool) Skip byte compile for .py files
android.no-byte-compile = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1


