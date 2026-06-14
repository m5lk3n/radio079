import os

from fetch_swr3 import fetch_swr3


def main():
    openai_api_key = os.environ["OPENAI_API_KEY"]
    print(openai_api_key[:4])
    fetch_swr3()


if __name__ == "__main__":
    main()
