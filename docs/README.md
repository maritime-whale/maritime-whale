# Maritime Whale docs

This directory contains maritime-whale project documentation.

## General Development

* Documentation still in progress...

## Installation (Local)

1. Clone this repo.
2. Open a terminal session.
3. Navigate to the root directory of the repo.
4. Ensure the `install` script has the correct permissions by running `chmod a+x install`.
5. Run the `./install` command.

### First-time Use & Validation (Local)
1. Open a terminal session.
2. Navigate to the root directory of the repo.
3. Ensure the `run` script has the correct permissions by running `chmod a+x run`.<br/>
4. Execute the `run` script with `debug` mode ENABLED: `./run debug`.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;`./run debug` should produce the following message:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;`Config directory not found. Creating directory: ./conf .`<br/>
5. Move a valid `credentials.json`, `riwhale.config`, and `.mapbox_token` to the newly-created `conf` directory (if you have a valid `.token.pickle` move that to `conf` too).<br/>
&nbsp;&nbsp;&nbsp;&nbsp;If there is no `.token.pickle` present in the `conf`dir, then one will need to be generated.
6. Make sure you are logged in to Gmail on the special VMR account (see documentation [diagram](docs/webapp-diagram.png)).
7. Run `./run debug` again.
8. Validate and authorize app permissions with Gmail using special VMR email (will open new tab in web browser). Authorization must be complete within 45 seconds or `.token.pickle` won't get generated and an error is produced.

### How to Use (_debug_ mode ENABLED)
Execute the `run` script with `debug` mode ENABLED: `./run debug`.

### How to Use (_debug_ mode DISABLED)
_**WARNING!**_ Do _NOT_ run without `debug` unless you know the consequences (check with the dev team for more information).*<br/>
Execute the `run` script with `debug` mode DISABLED: `./run`.

## Installation (Cloud)

* Documentation still in progress...

## Testing

* Documentation still in progress...
