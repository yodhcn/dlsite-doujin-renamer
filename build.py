import PyInstaller.__main__

if __name__ == '__main__':
    PyInstaller.__main__.run([
        'main.py',
        '--onefile',
        '--windowed',
        '--clean',
        '--icon',
        'Letter_R_blue.ico',  # https://icon-icons.com/icon/letter-r-blue/34893
        '--add-data',
        'Letter_R_blue.ico;.',
    ])
