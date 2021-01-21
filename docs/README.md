# Maritime Whale docs

This directory contains maritime-whale project documentation.

## General Development

* Documentation still in progress...

## Set Up

Before diving in, we recommend that you review the [web app architecture diagram](diagrams/webapp-diagram.png) to get a better understanding of how this web app interacts with and utilizes various technologies such as GitHub, GitHub Pages, Gmail, MapBox, and VesselFinder.

### Installation
1. Clone this repo.
2. Open a terminal session.
3. Navigate to the root directory of the repo.
4. Run `./install`.

### First-time Use & Validation
1. Open a terminal session.
2. Navigate to the root directory of the repo.
3. Execute the `run` script with `debug` mode enabled: `./run debug`.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;`./run debug` should produce the following message:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;`Config directory not found. Creating directory: ./conf .`<br/>
4. Move a valid `credentials.json`, `riwhale.config`, and `.mapbox_token` to the newly-created `conf` directory (if you have a valid `.token.pickle` move that to `conf` and _skip_ steps 5-7).<br/>
&nbsp;&nbsp;&nbsp;&nbsp;If there is no `.token.pickle` present in the `conf` directory, then one will need to be generated.
5. Make sure you are logged in to Gmail on the special VMR account (see the [web app diagram](diagrams/webapp-diagram.png) for more details).
6. Run `./run debug` again.
7. Validate and authorize app permissions with Gmail using special VMR email (will open new tab in web browser).<br/>
Authorization must be complete within 45 seconds or `.token.pickle` won't get generated and an error is produced.

### Using the `debug` Flag
* Execute the `run` script with `debug` mode enabled: `./run debug`.

* _**WARNING!**_ Do _NOT_ run without `debug` unless you know the consequences ([get in touch](mailto:dev.riwhale+help@gmail.com) with the dev team for more information).<br/>
Execute the `run` script with `debug` mode disabled: `./run`.

## Testing

* Documentation still in progress...
