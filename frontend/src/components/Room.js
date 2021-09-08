import React, { Component } from "react";

import { Button, Grid, Typography } from "@material-ui/core";
import { Link } from "react-router-dom";
import MusicPlayer from "./MusicPlayer";
import CreateRoomPage from "./CreateRoomPage";
export default class Room extends Component {
  constructor(props) {
    super(props);
    this.state = {
      votesToSkip: 2,
      guestCanPause: "false",
      isHost: false,
      showSettings: false,
      spotifyAuthenticated: false,
      song: {},
    };
    this.roomCode = this.props.match.params.roomCode;
    this.getRoomDetails = this.getRoomDetails.bind(this);
    this.getCurrentSong = this.getCurrentSong.bind(this);
    this.authenticateSpotify = this.authenticateSpotify.bind(this);
    this.leaveRoomButtonPressed = this.leaveRoomButtonPressed.bind(this);
    this.updateShowSettings = this.updateShowSettings.bind(this);
    this.renderSettingsButton = this.renderSettingsButton.bind(this);
    this.renderSettings = this.renderSettings.bind(this);
    this.getRoomDetails();
    // remove test call
    // this.getCurrentSong();
  }

  componentDidMount() {
    // call to get Current Song every second
    // NOTE: Not optimal way, we should use websocket for sclalablity
    this.interval = setInterval(this.getCurrentSong, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  getRoomDetails() {
    fetch("/api/get-room" + "?code=" + this.roomCode)
      .then((response) => {
        // if room does not exist
        if (!response.ok) {
          // clear roomcode from homepage
          this.props.leaveRoomCallback;
          // redirect to homepage
          this.props.history.push("/");
        }
        return response.json();
      })
      .then((data) => {
        this.setState({
          votesToSkip: data.votes_to_skip,
          guestCanPause: data.guest_can_pause,
          isHost: data.is_host,
        });

        // TODO:: This block being called again and again...
        if (this.state.isHost) {
          console.log(
            `authenticateSpotify() called again ${this.state.spotifyAuthenticated.toString()}`
          );
          this.authenticateSpotify();
        }
      });
  }

  authenticateSpotify() {
    fetch("/spotify/is-authenticated")
      .then((response) => response.json())
      .then((data) => {
        console.log(`spotifyAuthenticated: ${data.status}`);
        this.setState({
          spotifyAuthenticated: data.status,
        });
        // if (!data.status) {
        if (!this.state.spotifyAuthenticated) {
          fetch("/spotify/get-auth-url")
            .then((response) => response.json())
            .then((data) => {
              // redirect Spotify callback
              // TODO:: DEBUG INFINITE LOOP WHILE REDIRECTING FROM SPOTIFY AUTHENTICATION
              window.location.replace(data.url);
            });
        }
      });
  }

  getCurrentSong() {
    fetch("/spotify/current-song")
      .then((response) => {
        if (!response.ok) {
          return {};
        } else {
          return response.json();
        }
      })
      .then((data) => {
        // data = undefined
        // console.log(data);
        this.setState({
          song: data,
        });
      });
  }

  leaveRoomButtonPressed() {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    };
    fetch("/api/leave-room", requestOptions).then((_response) => {
      // clear roomcode from homepage
      this.props.leaveRoomCallback();
      // redirect to homepage
      this.props.history.push("/");
    });
  }

  updateShowSettings(value) {
    this.setState({
      showSettings: value,
    });
  }

  // render settings button if user is host
  renderSettingsButton() {
    return (
      <Grid item xs={12}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => this.updateShowSettings(true)}
        >
          Settings
        </Button>
      </Grid>
    );
  }

  renderSettings() {
    return (
      <Grid container spacing={1} align="center">
        <Grid item xs={12}>
          <CreateRoomPage
            update={true}
            votesToSkip={this.state.votesToSkip}
            guestCanPause={this.state.guestCanPause}
            roomCode={this.roomCode}
            updateCallback={this.getRoomDetails}
          />
        </Grid>
        <Grid item xs={12}>
          <Button
            variant="contained"
            color="secondary"
            onClick={() => this.updateShowSettings(false)}
          >
            Close
          </Button>
        </Grid>
      </Grid>
    );
  }

  render() {
    if (this.state.showSettings) {
      return this.renderSettings();
    }
    return (
      <Grid container spacing={1} align="center">
        <Grid item xs={12}>
          <Typography variant="h4" component="h4">
            Code: {this.roomCode}
          </Typography>
        </Grid>
        <MusicPlayer {...this.state.song} />
        {this.state.isHost && this.renderSettingsButton()}
        <Grid item xs={12}>
          <Button
            variant="contained"
            color="secondary"
            onClick={this.leaveRoomButtonPressed}
          >
            Leave Room
          </Button>
        </Grid>
      </Grid>
    );
  }
}
