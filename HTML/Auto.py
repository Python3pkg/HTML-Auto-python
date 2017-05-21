import re
from cgi import escape
from struct import unpack

__version__='0.0.4'

class Tag:

    def __init__( self, params={} ):
        self.encode  = 1                 if 'encode'  in params else 0
        self.sort    = 1                 if 'sort'    in params else 0
        self.level   = params['level']   if 'level'   in params else 0
        self.encodes = params['encodes'] if 'encodes' in params else ''
        self.indent  = params['indent']  if 'indent'  in params else ''
        self.newline = "\n"              if 'indent'  in params else ''
        self.encoder = Encoder()

    def tag( self, params={} ):

        tag   = params['tag']
        cdata = params['cdata'] if 'cdata' in params else ''
        attr  = params['attr']  if 'attr'  in params else {}

        ctype     = type( cdata )
        rendered  = ''
        no_indent = 0

        if not type( attr ) is Attr:
            attr = Attr( attr, self.sort )

        if ctype is list:

            if type( cdata[0] ) is dict:
                self.level += 1
                rendered = self.newline

                for hash in cdata:
                    rendered += self.tag( hash )
                
                self.level -= 1
            else:
                string = ''
                for scalar in cdata:
                    string += self.tag({ 'tag': tag, 'attr': attr, 'cdata': scalar })
                return string

        elif ctype is dict:
            self.level += 1
            rendered = self.newline + self.tag( cdata )
            self.level -= 1

        else:
            # empty tag
            if not len( str( cdata ) ):
                return '<' + tag + str(attr) + ' />'

            rendered = self.encoder.encode( cdata, self.encodes ) if self.encode else cdata
            no_indent = 1

        indent = '' if no_indent else self.indent * self.level

        return (self.indent * self.level) + \
            '<' + tag + str( attr ) + '>' + \
            str( rendered ) + indent + \
            '</' + tag + '>' + self.newline


class Attr:

    def __init__( self, params={}, sort=0 ):
        self.params = params
        self.sort   = sort

    def __str__( self ):
        attr  = ''
        seen = {}
        keys = sorted( self.params.keys() ) if self.sort else list(self.params.keys())
        for key in keys:
            if not key in seen:
                val = self.params[key]
                val = self.stringify( val ) if type( val ) is dict else val
                val = self.rotate( val )    if type( val ) is list else val
                attr += ' %s="%s"' % ( self.key( key ), self.val( val ) )
            seen[key] = 1

        return attr

    def key( self, key ):
        key = re.sub( '\s+', '', key )
        key = re.sub( '["\'>=\/]', '', key )
        return key

    def val( self, val ):
        val = str(val)
        val = re.sub( '"', '', val )
        return val.strip()

    def rotate( self, array ):
        val = array.pop(0)
        array.append( val )
        return val

    def stringify( self, attrs ):
        keys = sorted( attrs.keys() ) if self.sort else list(attrs.keys())
        vals = []
        for key in keys:
            val = attrs[key]
            if type( val ) is list:
                val = self.rotate( val )
            elif type( val ) is dict:
                k = sorted( val.keys() ) if self.sort else list(val.keys())
                val = k[0]
            vals.append( '%s: %s' % ( key, val ) )
        trail = ';' if len( vals ) else ''
        return '; '.join( vals ) + trail


class Encoder:

    def encode( self, string, *args):

        def num_entity(char):
            try:
                hex = unpack( 'B', bytes( char, 'utf_8' ) )
            except TypeError:
                hex = unpack( 'B', bytes( char ) )
            return '&#x%X;' % hex[0]

        def default(m):
            if m.group(0) in self.char2entity: return self.char2entity[ m.group(0) ]
            else: return num_entity( m.group(0) )


        if args and len(str(args[0])):
            lookup = {}
            def custom(m):
                if m.group(0) in lookup: return lookup[ m.group(0) ]
                else: return m.group(0)

            for c in str( args[0] ):
                lookup[c] = num_entity(c) if not c in self.char2entity else self.char2entity[c]
            string = re.sub( r'.', custom, string )
        else:
            # Encode control chars, high bit chars and '<', '&', '>', ''' and '"'
            string = re.sub( r"([^\n\r\t !\#\$%\(-;=?-~])", default, string )

        return string


    def encode_hex( self, *args ):
        tmp = self.char2entity
        self.char2entity = {}
        string = self.encode( *args )
        self.char2entity = tmp
        return string

    def __init__(self):

        self.entity2char = {
            'amp'  : '&',  # ampersand 
            'gt'   : '>',  # greater than
            'lt'   : '<',  # less than
            'quot' : '"',  # double quote
            'apos' : "'",  # single quote
            # PUBLIC ISO 8879-1986//ENTITIES Added Latin 1//EN//HTML
            'AElig' : chr( 198 ),  # capital AE diphthong (ligature)
            'Aacute': chr( 193 ),  # capital A, acute accent
            'Acirc' : chr( 194 ),  # capital A, circumflex accent
            'Agrave': chr( 192 ),  # capital A, grave accent
            'Aring' : chr( 197 ),  # capital A, ring
            'Atilde': chr( 195 ),  # capital A, tilde
            'Auml'  : chr( 196 ),  # capital A, dieresis or umlaut mark
            'Ccedil': chr( 199 ),  # capital C, cedilla
            'ETH'   : chr( 208 ),  # capital Eth, Icelandic
            'Eacute': chr( 201 ),  # capital E, acute accent
            'Ecirc' : chr( 202 ),  # capital E, circumflex accent
            'Egrave': chr( 200 ),  # capital E, grave accent
            'Euml'  : chr( 203 ),  # capital E, dieresis or umlaut mark
            'Iacute': chr( 205 ),  # capital I, acute accent
            'Icirc' : chr( 206 ),  # capital I, circumflex accent
            'Igrave': chr( 204 ),  # capital I, grave accent
            'Iuml'  : chr( 207 ),  # capital I, dieresis or umlaut mark
            'Ntilde': chr( 209 ),  # capital N, tilde
            'Oacute': chr( 211 ),  # capital O, acute accent
            'Ocirc' : chr( 212 ),  # capital O, circumflex accent
            'Ograve': chr( 210 ),  # capital O, grave accent
            'Oslash': chr( 216 ),  # capital O, slash
            'Otilde': chr( 213 ),  # capital O, tilde
            'Ouml'  : chr( 214 ),  # capital O, dieresis or umlaut mark
            'THORN' : chr( 222 ),  # capital THORN, Icelandic
            'Uacute': chr( 218 ),  # capital U, acute accent
            'Ucirc' : chr( 219 ),  # capital U, circumflex accent
            'Ugrave': chr( 217 ),  # capital U, grave accent
            'Uuml'  : chr( 220 ),  # capital U, dieresis or umlaut mark
            'Yacute': chr( 221 ),  # capital Y, acute accent
            'aacute': chr( 225 ),  # small a, acute accent
            'acirc' : chr( 226 ),  # small a, circumflex accent
            'aelig' : chr( 230 ),  # small ae diphthong (ligature)
            'agrave': chr( 224 ),  # small a, grave accent
            'aring' : chr( 229 ),  # small a, ring
            'atilde': chr( 227 ),  # small a, tilde
            'auml'  : chr( 228 ),  # small a, dieresis or umlaut mark
            'ccedil': chr( 231 ),  # small c, cedilla
            'eacute': chr( 233 ),  # small e, acute accent
            'ecirc' : chr( 234 ),  # small e, circumflex accent
            'egrave': chr( 232 ),  # small e, grave accent
            'eth'   : chr( 240 ),  # small eth, Icelandic
            'euml'  : chr( 235 ),  # small e, dieresis or umlaut mark
            'iacute': chr( 237 ),  # small i, acute accent
            'icirc' : chr( 238 ),  # small i, circumflex accent
            'igrave': chr( 236 ),  # small i, grave accent
            'iuml'  : chr( 239 ),  # small i, dieresis or umlaut mark
            'ntilde': chr( 241 ),  # small n, tilde
            'oacute': chr( 243 ),  # small o, acute accent
            'ocirc' : chr( 244 ),  # small o, circumflex accent
            'ograve': chr( 242 ),  # small o, grave accent
            'oslash': chr( 248 ),  # small o, slash
            'otilde': chr( 245 ),  # small o, tilde
            'ouml'  : chr( 246 ),  # small o, dieresis or umlaut mark
            'szlig' : chr( 223 ),  # small sharp s, German (sz ligature)
            'thorn' : chr( 254 ),  # small thorn, Icelandic
            'uacute': chr( 250 ),  # small u, acute accent
            'ucirc' : chr( 251 ),  # small u, circumflex accent
            'ugrave': chr( 249 ),  # small u, grave accent
            'uuml'  : chr( 252 ),  # small u, dieresis or umlaut mark
            'yacute': chr( 253 ),  # small y, acute accent
            'yuml'  : chr( 255 ),  # small y, dieresis or umlaut mark
            # Some extra Latin 1 chars that are listed in the HTML3.2 draft (21-May-96)
            'copy'  : chr( 169 ),  # copyright sign
            'reg'   : chr( 174 ),  # registered sign
            'nbsp'  : chr( 160 ),  # non breaking space
            # Additional ISO-8859/1 entities listed in rfc1866 (section 14)
            'iexcl' : chr( 161 ),
            'cent'  : chr( 162 ),
            'pound' : chr( 163 ),
            'curren': chr( 164 ),
            'yen'   : chr( 165 ),
            'brvbar': chr( 166 ),
            'sect'  : chr( 167 ),
            'uml'   : chr( 168 ),
            'ordf'  : chr( 170 ),
            'laquo' : chr( 171 ),
            'not'   : chr( 172 ),
            'shy'   : chr( 173 ),
            'macr'  : chr( 175 ),
            'deg'   : chr( 176 ),
            'plusmn': chr( 177 ),
            'sup1'  : chr( 185 ),
            'sup2'  : chr( 178 ),
            'sup3'  : chr( 179 ),
            'acute' : chr( 180 ),
            'micro' : chr( 181 ),
            'para'  : chr( 182 ),
            'middot': chr( 183 ),
            'cedil' : chr( 184 ),
            'ordm'  : chr( 186 ),
            'raquo' : chr( 187 ),
            'frac14': chr( 188 ),
            'frac12': chr( 189 ),
            'frac34': chr( 190 ),
            'iquest': chr( 191 ),
            'times' : chr( 215 ),
            'divide': chr( 247 ),
        }

        self.char2entity = {}
        for k, v in list(self.entity2char.items()):
            self.char2entity[v] = '&' + str(k) + ';'

        for i in range(255):
            if chr(i) not in self.char2entity:
                self.char2entity[ chr(i) ] = '&#' + str(i) + ';'
