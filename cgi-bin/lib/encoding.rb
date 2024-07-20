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

require 'uri'

module WaybackClassic
  class LegacyClientEncoding
    def self.detect(*args)
      new(*args)
    end

    attr_reader :utf8, :encoding_override

    def initialize(env = ENV)
      @utf8 = nil

      # TODO: Handle un-encoded values, somehow?
      query = URI.decode_www_form(env['QUERY_STRING'] || '').to_h

      unless query['utf8'].nil? || query['utf8'].empty?
        @utf8 = query['utf8']
        query.delete('utf8')

        env['QUERY_STRING'] = URI.encode_www_form query
      end

      @encoding_override = unless @utf8.nil?
                             canary_bytes = @utf8.split('').map(&:ord)
                             # NOTE: UTF-8 would be [0x2713]
                             case canary_bytes
                             # Safari forced to Shift_JIS mode
                             when [0xfffd, 0x26, 0x23, 0x36, 0x35, 0x35, 0x33, 0x33, 0x3b],
                                  # Dream Passport 3
                                  [0xfffd, 0x13]
                               'Shift_JIS' # or GB 2312
                               # when [0x26, 0x23, 0x36, 0x35, 0x35, 0x33, 0x33, 0x3b,
                               #       0x26, 0x23, 0x36, 0x35, 0x35, 0x33, 0x33, 0x3b,
                               #       0x26, 0x23, 0x36, 0x35, 0x35, 0x33, 0x33, 0x3b]
                               #   "ISO-2022-JP"
                               # when [0x26, 0x23, 0x36, 0x35, 0x35, 0x33, 0x33, 0x3b,
                               #       0x26, 0x23, 0x36, 0x35, 0x35, 0x33, 0x33, 0x3b]
                               #   "EUC-JP" # or Big5, or Korean Windows
                               # when [0x2704, 0x31, 0xfffd, 0x37]
                               #   "GB 18030" # or ISO Latin2
                             end
                           end
    end

    def encode(value)
      return value unless @encoding_override

      value.encode(@encoding_override, undef: :replace).force_encoding('UTF-8')
    end

    def quotify(value)
      if @encoding_override
        "\"#{value}\""
      else
        "“#{value}”"
      end
    end
  end
end
