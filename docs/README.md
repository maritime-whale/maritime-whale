# Maritime Whale docs

This directory contains maritime-whale project documentation.

## Description

This web app fetches daily vessel movement reports and wind data. Data is imported, cleaned, and cached. Statistical analyses is performed and HTML plot files are generated using Plotly. The plot files, wrangled data files, and a vessel blacklist file get pushed to the [riwhale.github.io](https://github.com/riwhale/riwhale.github.io/) repo. These files are hosted with live changes at https://riwhale.github.io via GitHub Pages. Plots and download links for the processed data files are embedded within the https://www.maritimewhale.com website. Remote caching handled by the [secure-cache](https://github.com/riwhale/secure-cache) repo.

## General Development

* Documentation still in progress...

## Installation (Local)

1. Simply clone this repo or download it as a ZIP (**NOTE:** _the ZIP method is **NOT** recommended for developers_).
2. Open a terminal session.
3. Navigate to the root directory of the repo.
4. Ensure the `install` script has the correct permissions by running `chmod a+x install`.
5. Run the `./install` command.

### First-time Use & Validation (Local)
1. Open a terminal session.
2. Navigate to the root directory of the repo.
3. Ensure the `run` script has the correct permissions by running `chmod a+x run`.<br/>
**WARNING!** Do **NOT** run without `debug` unless you know the consequences.*<br/>
4. Execute the `run` script with `debug` mode **_ENABLED_**: `./run debug`.<br/>
Do **NOT** run without `debug` if this is your first time running the `run` script.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;If this is your first time running the `run` script follow the steps below...<br/>
&nbsp;&nbsp;&nbsp;&nbsp;`./run debug` should produce the following message:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;`Config directory not found. Creating directory: ./conf .`<br/>
5. Move a valid `credentials.json` and `riwhale.config` to the newly-created `conf` directory (if you have a valid `.token.pickle` move that to `conf` too).<br/>
&nbsp;&nbsp;&nbsp;&nbsp;If there is no `.token.pickle` present in the `conf`dir, then one will need to be generated.
6. Make sure you are logged in to Gmail on the special VMR account (see documentation).
7. Run `./run debug` again.
8. Validate and authorize app permissions with Gmail using special VMR email (will open new tab in web browser). Authorization must be complete within 45 seconds or `.token.pickle` won't get generated and an error is produced.

### How to Use (_debug_ mode _ENABLED_)
Execute the `run` script with `debug` mode **_ENABLED_**: `./run debug`.

### How to Use (_debug_ mode _DISABLED_)
**WARNING!** Do **NOT** run without `debug` unless you know the consequences.*<br/>
Execute the `run` script with `debug` mode **_DISABLED_**: `./run`.


## Installation (Cloud)

* Documentation still in progress...

## Testing

* Documentation still in progress...
