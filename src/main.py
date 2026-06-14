import os


def main():
    openai_api_key = os.environ["OPENAI_API_KEY"]
    print(openai_api_key[:4])


if __name__ == "__main__":
    main()
