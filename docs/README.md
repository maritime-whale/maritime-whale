# Maritime Whale docs

This directory contains [maritime-whale](https://github.com/riwhale/maritime-whale)
project documentation.

## Methodologies

This web application monitors and characterizes ship behavior at the Charleston
and Savannah port entrances during the [migratory season](https://www.fisheries.noaa.gov/species/north-atlantic-right-whale)
of the North Atlantic right whale. By placing a high value on transparency and
including the rationale behind specific design decisions, we hope to provide a
clear picture of the intricacies of our data handling process. Please direct
any questions you may have to
[dev.riwhale+help@gmail.com](mailto:dev.riwhale+help@gmail.com).

### Vessel data retrieval and filtering

This analysis focuses on Post-Panamax and Panamax vessels in accordance with the
[USACE approach](https://erdc-library.erdc.dren.mil/jspui/handle/11681/32750) of
evaluating the largest ships in dredged channels. Vessels not subject to the
speed rule (e.g. military ops, law enforcement, search and rescue) as well as
pusher tugs, fishing vessels, and dredge operations are filtered out. Thus,
container ships, general cargo, bulk cargo, tankers, ro-ro, car carriers, and
cruise ships are the targets of this analysis. Erroneous entries are removed
from the data (e.g. abnormally high vessel speed, course errors, heading
errors). If a single position is reported for a given ship the entry is also
removed. Sample areas include ships under mandatory pilotage and exclude data
from pilot boarding areas. Bends in the Savannah entrance channel—which
naturally require vessels to turn—incur high yaw values. To prevent skewing
this analysis these areas are ignored. Doing so allows for a more lucid
characterization of vessel behavior in adverse and non-adverse conditions.

### Wind data retrieval and matching

The wind matching algorithm associates wind data with each AIS vessel position
based on timestamps, using data from the [NBDC](https://www.ndbc.noaa.gov/). The
algorithm matches wind buoy and vessel timestamps, finding the closest match
within a three-hour window. When operational, the buoys typically record every
ten minutes. If no match is found, fall back on alternate buoy data. In the
event of primary and alternate buoy failure corresponding wind entries get set
to `NaN`. Charleston’s buoy ID is
[41004](https://www.ndbc.noaa.gov/station_page.php?station=41004) and Savannah’s
is [41008](https://www.ndbc.noaa.gov/station_page.php?station=41008). Due to
their proximity, the Charleston buoy serves as an alternate for Savannah and
vice versa.

### Meeting and passing analysis

One-way transits are channel conditions where there is no oncoming traffic for a
given vessel position. Conversely, two-way transits are channel conditions where
ships are traveling in opposite directions. The two-way condition applies to all
entries up until the point where the last set of ships meet and pass. After,
they are considered to be one-way. The `meetpass` algorithm iteratively compares
AIS vessel positions, identifying meeting and passing instances, while
classifying two-way and one-way transit entries. Potential instances of meeting
and passing are identified by checking if a pair of ships have timestamps within
a one-hour window and opposing course behavior. The distance between each pair
of vessel positions is subsequently computed within this time window, and the
minimum distance (point of closest approach) is saved. Working in reverse
chronological order from the point of closest approach and its associated
timestamp, the algorithm identifies all relevant positions subject to two-way
conditions. A minimum distance value is used to qualify potential meeting and
passing encounters as true encounters.

### Data enrichment

Each vessel's max and mean speed are computed and recorded. Relative vessel
location (nearshore or offshore) is specified by the channel's longitudinal
midpoint. Buoy source IDs are added depending on wind data matching. One-way
and two-way transits are assigned via `meetpass` analysis. Compute and add yaw,
which is the absolute difference between course and heading.
Vessel effective beam is calculated using the following formula:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://render.githubusercontent.com/render/math?math=EB = cos(90-yaw)\*loa %2B cos(yaw)\*beam">

where effective beam, LOA (length overall), and beam are all expressed in feet,
yaw is in degrees.
Channel occupancy is computed based on transit condition and effective beam.
Vessels subject to two-way conditions can only navigate in half the channel
width, while one-way conditions can navigate the full channel width. Higher
yaw values translate to higher effective beams, yielding larger percentages of
occupied channel.

### Data visualizations
Statistical plots visually characterize vessel behavior in the entrance
channels. The vessel speed histogram compares compliant and non-compliant
entries. Whereas, the wind speed histogram compares adverse and non-adverse
wind conditions. The correlation between wind and vessel speed is shown as a
density plot. Most vessels transit at non-compliant speed—typically for the
majority, if not the entirety of the transit. The vessel speed plot illustrates
this, as well as the disparity between one-way and two-way transits.
Similarities in yaw values between compliant and non-compliant vessels are
shown in the vessel speed and yaw line plot. Navigational leeway is depicted
by comparing the relationships between vessel speed, channel occupancy, and
transit condition. Any plot or statistic characterizing wind behavior excludes
entries with missing wind information. However, if 65% or more of the wind data
is missing after matching, an error is displayed instead of rendering the wind
plots.

## Set Up

Before diving in, we recommend that you review the
[web app architecture diagram](diagrams/web-app-diagram.pdf) to get a better
understanding of how this web app interacts with and utilizes various
technologies such as Amazon Web Services, GitHub, Gmail, and Wix.

### Installation
1. Clone this repo.
2. Set your current working directory to the root directory of this repo.
3. Run `./install`.

### First-time use & validation
1. Move a valid `credentials.json`, `riwhale.config`, and `.mapbox_token` to the
`conf` directory (if you have a valid `.token.pickle` move that to `conf`
and _skip_ steps 2-4).
2. Make sure you are logged in to Gmail on the special VMR account (see
[this diagram](diagrams/web-app-diagram.pdf) for more details).
3. Set your current working directory to the root directory of the repo and
run `./run debug`.
4. Validate and authorize app permissions with Gmail using special VMR email
(will open new tab in web browser).<br/>
Authorization must be complete within 45 seconds otherwise `.token.pickle`
won't get generated and an error is produced.

### Using the `debug` flag
* Execute the `run` script with `debug` mode enabled: `./run debug`.

* _**WARNING!**_ Do _NOT_ run without `debug` unless you know the consequences
([contact the dev team](mailto:dev.riwhale+help@gmail.com) for more info).<br/>
Execute the `run` script with `debug` mode disabled: `./run`.

## Testing

* Documentation still in progress...
