# Maritime Whale docs

This directory contains maritime-whale project documentation.

## Set Up

Before diving in, we recommend that you review the [web app architecture diagram](diagrams/web-app-diagram.pdf) to get a better understanding of how this web app interacts with and utilizes various technologies such as Amazon Web Services, GitHub, Gmail, and Wix.

### Installation
1. Clone this repo.
2. Set your current working directory to the root directory of the repo.
3. Run `./install`.

### First-time use & validation
1. Move a valid `credentials.json`, `riwhale.config`, and `.mapbox_token` to the `conf` directory (if you have a valid `.token.pickle` move that to `conf` and _skip_ steps 2-4).
2. Make sure you are logged in to Gmail on the special VMR account (see [this diagram](diagrams/web-app-diagram.pdf) for more details).
3. Set your current working directory to the root directory of the repo and run `./run debug`.
4. Validate and authorize app permissions with Gmail using special VMR email (will open new tab in web browser).<br/>
Authorization must be complete within 45 seconds otherwise `.token.pickle` won't get generated and an error is produced.

### Using the `debug` flag
* Execute the `run` script with `debug` mode enabled: `./run debug`.

* _**WARNING!**_ Do _NOT_ run without `debug` unless you know the consequences ([contact the dev team](mailto:dev.riwhale+help@gmail.com) for more info).<br/>
Execute the `run` script with `debug` mode disabled: `./run`.

## Testing

* Documentation still in progress...
