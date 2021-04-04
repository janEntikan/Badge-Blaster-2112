from setuptools import setup

setup(
    name="Badge Blaster",
    options={
        'build_apps': {
            'include_patterns': [
                'assets/cache/*',
                'assets/fireworks/*.png',
                'assets/fonts/*.ttf',
                'assets/gui/*.png',
                'assets/models/*.bam',
                'assets/music/*.ogg',
                'assets/sfx/*.wav',
                'assets/shaders/*.vert',
                'assets/shaders/*.frag',
                'README.md',
                'keybindings.toml',
                'settings.prc',
                'assets/cache/*',
                'BoxArt.png',
            ],
            'gui_apps': {
                'bdgeblst': 'main.py',
            },
            'icons': {
                'bdgeblst': ['icon.png'],
            },
            'log_filename': '$USER_APPDATA/Badge Blaster/output.log',
            'log_append': False,
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
        }
    }
)
