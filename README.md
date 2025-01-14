# Wayback Classic

[![Ruby](https://github.com/ticky/wayback-classic/actions/workflows/ruby.yml/badge.svg)](https://github.com/ticky/wayback-classic/actions/workflows/ruby.yml) [![Deploy](https://github.com/ticky/wayback-classic/actions/workflows/main.yml/badge.svg)](https://github.com/ticky/wayback-classic/actions/workflows/main.yml)

A simple, CGI-based frontend for the Wayback Machine which works on old browsers without modern JavaScript or CSS support

Wayback Classic is available at [wayback-classic.net](http://wayback-classic.net). It supports both HTTP and HTTPS.

## Why

The Wayback Machine contains a lot of websites from the turn of the century which are perfect for browsing on older machines, but the interface the Wayback Machine itself presents is completely incompatible with many such systems, making it very difficult to navigate.

Wayback Classic attempts to provide a fully-functional frontend for the Wayback Machine, providing these systems with access without the extra technological requirements.

## Notes

This is built on both the [CDX API](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server) (for retrieving lists of page snapshots), as well as the undocumented `__wb/search` API used by the Wayback Machine's own frontend to handle site search and determine if a site exists in the archive. More info about the site search can be found [in this blog post](http://blog.archive.org/2016/10/24/beta-wayback-machine-now-with-site-search/).

## Hosting Wayback Classic

If you wish to run your own instance, the author has two requests:

1. Please configure your server to set the `WEBMASTER_EMAIL` variable for CGI applications to an email address you can be reached at.  
   This variable is included in the `User-Agent` string for requests to the Wayback Machine, and I would feel better knowing that other instances provide proper contact information. For Apache you can add use `SetEnv` in a `.htaccess` file.
2. Please do not display advertising to, or track users using Wayback Classic.

Further, there are some considerations:

- Wayback Classic has a built-in cache mechanism; it will cache responses from the Wayback Machine on-disk with a validity of 24 hours to avoid hammering their servers. You should consider running `bin/cache-clean` periodically to empty this cache, or it will build up.
- Please do not use `bin/dev-server` (described below) in production. Wayback Classic is a basic CGI application and should be deployed as such.

## License

Wayback Classic is licensed under the Affero General Public License version 3, or any later version of the AGPL, the text of which can be found in LICENSE.md, unless otherwise noted.

## Development

A basic, WEBrick-based development server script is included at `bin/dev-server`. It defaults to `localhost:8000`, but the port can be overridden by setting a `PORT` environment variable.

### Testing

While the root directory of this repository is intended to map directly to the root htdocs directory of a server, with no dependencies other than the Ruby standard library, a `Gemfile` is provided under the `tests` directory which contains dependencies for testing.

For testing purposes, the CGI scripts are loaded as Ruby modules instead of normal scripts, and their lifecycle is exercised by a minimal Rack application to facilitate the use of Capybara.

To run the test suite, open a terminal within the `tests` directory, and run `bundle && bundle exec rake`.
