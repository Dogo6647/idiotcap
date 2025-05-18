# 🧢IdiotCap
Screencasting for idiots who want to ""stream"" JPEGs of their screen over HTTP for some reason. <br>
IdiotCap is a simple (but also pretty stupid) tool to fetch the screen of whatever computer is hosting it via HTTP.<br>
it includes:
- A `/screenshot` endpoint to take a quick and crusty JPEG screenshot of the server's monitor
- A `/screenshot/worse` endpoint to take a, well, **even worse** screenshot.
- And a companion webpage right at the `/` index to get a fun live feed of the screen, <br>which requests a screencap every 0.1 seconds by default, effectively "streaming" your screen. (that's 10 FPS btw)

<br>The IdiotCap Live page is also optimized to run on older devices, as old as a Nintendo 2DS! (yes, I tested it, it works, it's not great though)<br><br>
And yes, it's safe if you want it to be. You can create a `whitelist.txt` file at the directory you're running the script from containing the list of IPs you want to give access to your screen.
If you don't create the file, it will only allow local IPs by default.

## Getting Started
As of writing, I've only tested IdiotCap on Linux with X11. Good luck with wayland or other OSes ;)
1. Download the repo with your preferred method.
2. Install requirements:
```bash
pip install -r requirements.txt
```
3. Run `idiotcap.py`
```bash
python3 idiotcap.py
```
And yeah, that's it.
