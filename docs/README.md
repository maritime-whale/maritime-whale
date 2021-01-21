# Maritime Whale docs

This directory contains maritime-whale project documentation.

## General Development

* Documentation still in progress...

## Set Up

Before diving in, we recommend that you review the [web app architecture diagram](diagrams/web-app-diagram.pdf) to get a better understanding of how this web app interacts with and utilizes various technologies such as Amazon Web Services, GitHub, Gmail, and Wix.

### Installation
1. Clone this repo.
2. Set your current working directory to the root directory of the repo.
3. Run `./install`.

### First-time Use & Validation
1. Set your current working directory to the root directory of the repo.
2. Execute the `run` script with `debug` mode enabled: `./run debug`.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;`./run debug` should produce the following message:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;`Config directory not found. Creating directory: ./conf .`<br/>
3. Move a valid `credentials.json`, `riwhale.config`, and `.mapbox_token` to the newly-created `conf` directory (if you have a valid `.token.pickle` move that to `conf` and _skip_ steps 4-6).<br/>
&nbsp;&nbsp;&nbsp;&nbsp;If there is no `.token.pickle` present in the `conf` directory, then one will need to be generated.
4. Make sure you are logged in to Gmail on the special VMR account (see the [web app diagram](diagrams/web-app-diagram.pdf) for more details).
5. Run `./run debug` again.
6. Validate and authorize app permissions with Gmail using special VMR email (will open new tab in web browser).<br/>
Authorization must be complete within 45 seconds or `.token.pickle` won't get generated and an error is produced.

### Using the `debug` Flag
* Execute the `run` script with `debug` mode enabled: `./run debug`.

* _**WARNING!**_ Do _NOT_ run without `debug` unless you know the consequences ([get in touch with the dev team](mailto:dev.riwhale+help@gmail.com) for more information).<br/>
Execute the `run` script with `debug` mode disabled: `./run`.

## Testing

* Documentation still in progress...
