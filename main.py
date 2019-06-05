import pathlib
from typing import Optional
import pickle

import google.oauth2.credentials

import event


def load_token(file: pathlib.Path) -> Optional[google.oauth2.credentials.Credentials]:
    """トークンをロードします。

    pickleの中にtokenがなければNoneを返します。
    """
    try:
        # pathlib.Path('token.pickle').read_bytes()をモックしたテスト
        with file.open('rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


def main():
    token_file = pathlib.Path('token.pickle')
    credentials = event.ServiceBuilder.renew_token(credentials=load_token(token_file))

    with token_file.open('wb') as f:
        pickle.dump(credentials, f)
    
    service = event.ServiceBuilder.build() # missing one argument
    events = event.EventManager.fetch_events(number=2, service=service)
    print(events)

if __name__ == '__main__':
    main()
