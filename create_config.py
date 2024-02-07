import configparser

def create_config_file():
    config = configparser.ConfigParser()
    config['SPOTIFY'] = {
        'CLIENT_ID': 'your_client_id',
        'CLIENT_SECRET': 'your_client_secret',
        'REDIRECT_URI': 'http://localhost:8888/callback'
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def prompt_user_for_credentials():
    client_id = input("Enter your Spotify Client ID: ")
    client_secret = input("Enter your Spotify Client Secret: ")

    # Update the config with user input
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('SPOTIFY', 'CLIENT_ID', client_id)
    config.set('SPOTIFY', 'CLIENT_SECRET', client_secret)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def main():
    create_config_file()
    prompt_user_for_credentials()

if __name__ == "__main__":
    main()
