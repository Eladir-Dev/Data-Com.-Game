import webview
import sys

def main():
    if len(sys.argv) < 4:
        sys.exit(-1)

    _, scaled_width, scaled_height, window_caption, url = sys.argv

    webview.create_window(
        window_caption,
        url,
        width=int(scaled_width),
        height=int(scaled_height),
        resizable=False,
    )
    webview.start()
    sys.exit(0)


if __name__ == "__main__":
    main()
