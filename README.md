# maritime-whale-map
# Description
Maritime vessel traffic speed plotter.

Fetches daily vessel movement report from Gmail. Imports, cleans, and caches data. Generates HTML plot files using Plotly, pushing plot files to the https://github.com/riwhale/riwhale.github.io/ repo. Hosted with live changes at https://riwhale.github.io via GitHub Pages. Embed the plot webpages in the www.maritimewhale.com website using the URLs for the GitHub hosted HTML files.

# Installation Instructions
1. Simply clone this repo or download it as a ZIP.
2. Open a terminal session.
3. Navigate to the root directory of the repo.
4. Ensure the `install` script has the correct permissions by running `chmod a+x install`.
5. Run the `./install` command.

# First-time Use & Validation
1. Open a terminal session.
2. Navigate to the root directory of the repo.
3. Ensure the `run` script has the correct permissions by running `chmod a+x run`.<br/>
***_WARNING!_** Do **_NOT_** run without `dev` unless you know the consequences.*<br/>
4. Run the `./run` command with `dev` mode _ENABLED_: `./run dev`.<br/>
*Do **_NOT_** run without `dev` if this is your first time running the `run` script.*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*If this is your first time running the `run` script follow the steps below...*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*`./run` will produce a message like:*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*`Config directory not found. Creating directory: ./conf .`*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*OR*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*`Missing config file. ./conf/riwhale.config does not exist.`*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*Don't worry **this is normal**...*<br/>
5. Move a valid `credentials.json` and `riwhale.config` to the newly-created `conf` directory (if you have a valid `.token.pickle` move that to `conf` too).<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*If there is no `.token.pickle` present in the `conf`dir, then one will need to be generated.*
6. Make sure you are logged in to Gmail on the special VMR account (see documentation).
7. Run `./run dev` again.
8. Validate and authorize app permissions with Gmail using special VMR email (will open new tab in web browser) -- must complete within 45 seconds or `.token.pickle` won't get generated and an error is produced.

# How to Use (*dev* mode disabled)
1. Open a terminal session.
2. Navigate to the root directory of the repo.
3. Ensure the `run` script has the correct permissions by running `chmod a+x run`.<br/>
***_WARNING!_** Do **_NOT_** run without `dev` unless you know the consequences.*<br/>
4. Run the `./run` command with `dev` mode **_DISABLED_**: `./run`.

_For more help please refer to the **maritime-whale** [documentation](http://riwhale.github.io/) or contact [@riwhale](https://github.com/riwhale) at [dev.riwhale@gmail.com](dev.riwhale@gmail.com)._
