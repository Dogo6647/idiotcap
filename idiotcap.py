from flask import Flask, request, send_file, render_template_string, abort, make_response
from io import BytesIO
from PIL import Image
import os
import mss

app = Flask(__name__)

# polling interval (1/[fps])
POLL_INTERVAL = 1/10

# whitelist file is optional
WHITELIST_FILE = 'whitelist.txt'

def capture_mss_to_memory(worse):
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)

            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

            if not worse:
                base_height = 480
            else:
                base_height = 240
            h_percent = base_height / float(img.size[1])
            new_width = int(float(img.size[0]) * h_percent)
            img_resized = img.resize((new_width, base_height), Image.LANCZOS)

            # jpeg my beloved
            buffer = BytesIO()
            if not worse:
                img_resized.save(buffer, format='JPEG', quality=75)
            else:
                img_resized.save(buffer, format='JPEG', quality=25)
            buffer.seek(0)
            return buffer
    except Exception as e:
        print("mss capture failed:", str(e))
        return None

def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return None
    with open(WHITELIST_FILE) as f:
        return set(line.strip() for line in f if line.strip())

def is_allowed(ip, whitelist):
    if whitelist is None:
        return ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.') or ip.startswith('127.')
    return ip in whitelist

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>🧢 IdiotCap Live</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            background: black;
            height: 100%;
            max-width: 100vw;
            max-height: 100vh;
        }

        .mainview {
            position: relative;
            width: 100%;
            height: 100%;
            background: black;
            text-align: center;
        }

        #screen {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: opacity 0.1s linear;

            font-family: 'object-fit: contain;';
        }

        /* Fallback for browsers that don't support object-fit */
        @supports not (object-fit) {
            #screen {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: auto;
                height: 100%;
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
<div class="mainview">
<img id="screen" src="" alt="IdiotCap Live Stream ({{ 1 / interval }} fps)">
</div>
<script>
  var img = document.getElementById('screen');
  var supportsBlob = !!(window.URL && window.URL.createObjectURL);

  function updateImage() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/screenshot?ts=' + new Date().getTime(), true);

    if (supportsBlob) {
      xhr.responseType = 'blob';
    }

    xhr.onload = function () {
      if (xhr.status === 200) {
        if (supportsBlob) {
          var url = URL.createObjectURL(xhr.response);
          img.src = url;
        } else {
          img.src = '/screenshot?ts=' + new Date().getTime();
        }
      }
    };

    xhr.send();
  }
  window.onload = function () {
      if (supportsBlob) {
          setInterval(updateImage, {{ interval * 1000 }});
      } else {
            alert('Blob is not supported. Quality will be downgraded.');
            (function() {
                var img = document.getElementById('screen');
                var tempImg = new Image();
                var interval = {{ interval * 1000 }};

                function updateImage() {
                  tempImg.onload = function() {
                    img.src = tempImg.src;
                    setTimeout(updateImage, interval);
                  };

                  tempImg.src = '/screenshot/worse?t=' + Date.now();
                }

                updateImage();
              })();
      }
  }
</script>
</body>
</html>
""", interval=POLL_INTERVAL)

@app.route('/worse')
def index_worse():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>🧢 IdiotCap Live (but worse)</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            background: black;
            height: 100%;
            max-width: 100vw;
            max-height: 100vh;
        }

        .mainview {
            position: relative;
            width: 100%;
            height: 100%;
            background: black;
            text-align: center;
        }

        #screen {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: opacity 0.1s linear;

            font-family: 'object-fit: contain;';
        }

        /* Fallback for browsers that don't support object-fit */
        @supports not (object-fit) {
            #screen {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: auto;
                height: 100%;
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
<div class="mainview">
<img id="screen" src="" alt="IdiotCap Live Stream ({{ 1 / interval }} fps)">
</div>
<script>
  var img = document.getElementById('screen');
  var supportsBlob = !!(window.URL && window.URL.createObjectURL);

  function updateImage() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/screenshot?ts=' + new Date().getTime(), true);

    if (supportsBlob) {
      xhr.responseType = 'blob';
    }

    xhr.onload = function () {
      if (xhr.status === 200) {
        if (supportsBlob) {
          var url = URL.createObjectURL(xhr.response);
          img.src = url;
        } else {
          img.src = '/screenshot?ts=' + new Date().getTime();
        }
      }
    };

    xhr.send();
  }
  window.onload = function () {
      if (false) {
          setInterval(updateImage, {{ interval * 1000 }});
      } else {
            (function() {
                var img = document.getElementById('screen');
                var tempImg = new Image();
                var interval = {{ interval * 1000 }};

                function updateImage() {
                  tempImg.onload = function() {
                    img.src = tempImg.src;
                    setTimeout(updateImage, interval);
                  };

                  tempImg.src = '/screenshot/worse?t=' + Date.now();
                }

                updateImage();
              })();
      }
  }
</script>
</body>
</html>
""", interval=POLL_INTERVAL)

@app.route('/screenshot')
def screenshot():
    whitelist = load_whitelist()
    client_ip = request.remote_addr

    if not is_allowed(client_ip, whitelist):
        abort(403, description="no")

    image_io = capture_mss_to_memory(worse=False)
    if not image_io:
        abort(500, description="Screengrab failed D: (Are you on X11? Do you even HAVE a monitor?)")

    response = make_response(send_file(image_io, mimetype='image/jpeg'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/screenshot/worse')
def screenshot_worse():
    whitelist = load_whitelist()
    client_ip = request.remote_addr

    if not is_allowed(client_ip, whitelist):
        abort(403, description="sorry but no")

    image_io = capture_mss_to_memory(worse=True)
    if not image_io:
        abort(500, description="Screengrab failed D: (Are you on X11? Do you even HAVE a monitor?)")

    response = make_response(send_file(image_io, mimetype='image/jpeg'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

