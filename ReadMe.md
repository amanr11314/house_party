# HOUSE PARTY [DEPLOYED APP](https://my-music-controller.herokuapp.com/)

## Getting Started

<hr>

### Make sure you have pipenv installed on your system :-

    pip install pipenv

### Install django and other python dependencies:- <br> cd into root directory of project and run :-

    pipenv install

### Install react and other frontend node dependencies:-

    cd ./frontend
    pipenv install

### Make migrations for the model (from root directory of this application run):-

    python manage.py makemigrations
    python manage.py migrate

### To run the application on localhost:8000 open two Terminals side by side:-

    t0: python manage.py runserver
    t1: cd ./frontend
    t1: npm run dev

## About this project:-

- This project is a room based app in which host can CREATE the room. For which he will have to Authenticate with their Spotify account.
- Each room is UNIQUELY identified by its room code - A 6 character UNIQUE CODE.
- Other users can join the room by Room Code after Authenticating from their Spotify account.
- If host leaves room, Room is destroyed.
- Host can update how many votes required to skip the song.
- Host has PLAYBACK CONTROLS (PLAY/PAUSE/SKIP) for the room. However he must have premium spotify account to do this as per Spotify documentation.
- Every other users can see the song whhich is being played (ALBUM COVER, TITLE, ARTIST, PROGRESS)
- It uses Django, DjangoRestFrameWork, React, Material UI, Webpack to bundle React files into a single js file.
- Django app is based on MVT (Model-View-Template) pattern

# NOTE:-

    - Don't foregt to create your own spotify developer account and replace credentials in ./spotify/credentials.py file.

    - For redirect URI put [{YOUR_LOCAL_HOST_URL} or {YOUR_PRODUCTION_APP_URL}]/spotify/redirect this should be also added into your created app in spotify dhashboard in your app settings.

    - Spotify API doesn't allow playback controls (PLAY/PAUSE/SKIP/SEEK) from API endpoint unless that user has premium account. So keep that in mind while runnig the application.
