# maritime-whale
# Description
Monitors maritime vessel traffic in the ports of _Charleston, North Carolina_ & _Savannah, Georgia_.<br/>
**_Maritime Whale Web App Engine_** - Fetches daily vessel movement reports and wind data. Imports, cleans, and caches data; perform statistical analysis on data and generates HTML plot files using Plotly -- pushing plot files, wrangled data files, and a vessel blacklist file to the [riwhale.github.io](https://github.com/riwhale/riwhale.github.io/) repo. Hosted with live changes at https://riwhale.github.io via GitHub Pages. Plots and wrangled data files are embed within the www.maritimewhale.com website. Remote caching handled by the [secure-cache](https://github.com/riwhale/secure-cache) repo.

# Key Features
* Plots
* Meeting and passing
* *etc. (TO BE COMPLETED)*

# Installation Instructions
1. Simply clone this repo or download it as a ZIP (**NOTE:** _the ZIP method is **NOT** recommended for developers_).
2. Open a terminal session.
3. Navigate to the root directory of the repo.
4. Ensure the `install` script has the correct permissions by running `chmod a+x install`.
5. Run the `./install` command.

# First-time Use & Validation
1. Open a terminal session.
2. Navigate to the root directory of the repo.
3. Ensure the `run` script has the correct permissions by running `chmod a+x run`.<br/>
***_WARNING!_** Do **_NOT_** run without `debug` unless you know the consequences.*<br/>
4. Execute the `run` script with `debug` mode **_ENABLED_**: `./run debug`.<br/>
*Do **_NOT_** run without `debug` if this is your first time running the `run` script.*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*If this is your first time running the `run` script follow the steps below...*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*`./run debug` should produce the following message:*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*`Config directory not found. Creating directory: ./conf .`*<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*Don't worry **this is normal**...*<br/>
5. Move a valid `credentials.json` and `riwhale.config` to the newly-created `conf` directory (if you have a valid `.token.pickle` move that to `conf` too).<br/>
&nbsp;&nbsp;&nbsp;&nbsp;*If there is no `.token.pickle` present in the `conf`dir, then one will need to be generated.*
6. Make sure you are logged in to Gmail on the special VMR account (see documentation).
7. Run `./run debug` again.
8. Validate and authorize app permissions with Gmail using special VMR email (will open new tab in web browser) -- must complete within 45 seconds or `.token.pickle` won't get generated and an error is produced.

# How to Use (*debug* mode *ENABLED*)
Execute the `run` script with `debug` mode **_ENABLED_**: `./run debug`.

# How to Use (*debug* mode *DISABLED*)
***_WARNING!_** Do **_NOT_** run without `debug` unless you know the consequences.*<br/>
Execute the `run` script with `debug` mode **_DISABLED_**: `./run`.

_For more help please refer to the **maritime-whale** [wiki](http://riwhale.github.io/docs/docs.txt) or contact [@riwhale](https://github.com/riwhale) at [dev.riwhale+help@gmail.com](mailto:dev.riwhale+help@gmail.com)._
