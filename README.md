# ![Logo](assets/logo_64.png) Maritime Whale

Maritime Whale tracks ship traffic in the ports of Charleston, North Carolina
and Savannah, Georgia.

Daily monitoring and analysis is made available at
https://www.maritimewhale.com.

This web app is designed to fetch vessel movement reports and wind data every
day. The data is imported, cleaned, and cached. Statistical analysis is
performed and HTML plot files are generated using [Plotly](https://plotly.com/).
The plot files, wrangled data files, and a vessel blacklist file get pushed to
the [riwhale.github.io](https://github.com/riwhale/riwhale.github.io/) repo.
These files are hosted with live changes at https://riwhale.github.io via
_GitHub Pages_. Plots and download links for the processed data files are
embedded within the https://www.maritimewhale.com website. Remote caching
handled by the [secure-cache](https://github.com/riwhale/secure-cache) repo.

Documentation is rooted in [docs/README.md](docs/README.md).

_For more help please contact [@riwhale](https://github.com/riwhale) at [dev.riwhale+help@gmail.com](mailto:dev.riwhale+help@gmail.com)._
