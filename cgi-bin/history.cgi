#!/usr/bin/env ruby

# Wayback Machine History CGI Script
# ----------------------------------
# Uses the Wayback Machine's CDX API to retrieve
# a list of snapshots for the given URL.
#
# Wayback Classic
# Copyright (C) 2024 Jessica Stokes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

require 'cgi'

require_relative 'lib/cdx'
require_relative 'lib/encoding'
require_relative 'lib/error_reporting'
require_relative 'lib/permit_world_writable_temp' if ENV["FORCE_WORLD_WRITABLE_TEMP"] == "true"
require_relative 'lib/utils'
require_relative 'lib/web_client'

module WaybackClassic
  module History
    def self.run
      legacy_encoding = LegacyClientEncoding.detect

      CGI.new.tap do |cgi|
        ErrorReporting.catch_and_respond(cgi) do
          if cgi.params.keys - ["q", "date"] != [] || cgi.params["q"]&.first.nil? || cgi.params["q"]&.first&.empty?
            raise ErrorReporting::BadRequestError.new("A query parameter must be provided")
          end

          query = cgi.params["q"]&.first
          date = cgi.params["date"]&.first

          if date == "latest" || date == "earliest"
            limit = if date == "latest"
                      # The Wayback Machine's CDX API seems to have a bug
                      # where retrieving the last 1 returns 0,
                      # but the last 2 returns 2, so, we do the latter
                      -2
                    elsif date == "earliest"
                      1
                    end

            response = begin
                         WebClient.open uri("https://web.archive.org/cdx/search/cdx",
                                            url: query,
                                            output: "json",
                                            limit: limit)
                       rescue OpenURI::HTTPError
                         raise ErrorReporting::ServerError.new("Couldn't retrieve #{date} snapshot for this URL")
                       end

            cdx_results = CDX.objectify response.read

            if cdx_results.any?
              # NearlyFreeSpeech only exposes this as ENV["HTTPS"]
              scheme = if ENV["HTTPS"] == "on"
                         "https"
                       else
                         (ENV["REQUEST_SCHEME"] || ENV["REQUEST_URI"] || "http").split(":").first
                       end

              redirect_uri = "#{scheme}://web.archive.org/web/#{cdx_results.last["timestamp"]}if_/#{cdx_results.last["original"]}"

              cgi.out "type" => "text/html",
                      "charset" => "UTF-8",
                      "status" => "REDIRECT",
                      "location" => redirect_uri do
                render "redirect.html", redirect_uri: redirect_uri
              end

              return
            else
              raise ErrorReporting::ServerError.new("Couldn't retrieve #{date} snapshot for this URL")
            end
          end

          date_index = begin
            response = WebClient.open uri("https://web.archive.org/cdx/search/cdx",
                                          url: query,
                                          output: "json",
                                          collapse: "timestamp:6")

            CDX.objectify(response.read).group_by { |index_item| index_item["datetime"].year }
          rescue OpenURI::HTTPError
            raise ErrorReporting::ServerError.new("Couldn't retrieve date index for this URL")
          end

          if date.nil? || date.empty? || date.length < 6
            cgi.out "type" => "text/html",
                    "charset" => "UTF-8",
                    "status" => "OK" do
              render "history/index.html",
                     query: query,
                     date_index: date_index,
                     legacy_encoding: legacy_encoding
            end

            return
          end

          response = begin
                       WebClient.open uri("https://web.archive.org/cdx/search/cdx",
                                          url: query,
                                          output: "json",
                                          from: date,
                                          to: date,
                                          collapse: "digest")
                     rescue OpenURI::HTTPError
                       raise ErrorReporting::ServerError.new("Couldn't retrieve monthly history for this URL")
                     end

          cdx_results = CDX.objectify response.read

          cgi.out "type" => "text/html",
                  "charset" => "UTF-8",
                  "status" => "OK" do
            render "history/calendar.html",
                   query: query,
                   date_index: date_index,
                   date: date,
                   cdx_results: cdx_results,
                   legacy_encoding: legacy_encoding
          end
        end
      end
    end
  end
end

WaybackClassic::History.run if $PROGRAM_NAME == __FILE__
