import re

# NOTE 1
# (?: ) represents a non-capturing group, which allows to control 
# the expression concatenation order without the overhead of saving 
# it as a matched part of the string
#
# NOTE 2
# the following references allude to RFC5322 
# (https://tools.ietf.org/html/rfc5322)
#
# NOTE 3
# as indicated in 3.1. Introduction, refer to RFC5234 Appendix B.1 
# (https://tools.ietf.org/html/rfc5234#appendix-B.1) for the primitive 
# tokens definitions
#
# NOTE 4
# in 3.2.2., when defining the comment content, RFC includes COMMENT 
# syntax, but adding it would be circular

# see 2.2.2. Structured Header Field Bodies
WSP = r'\s'                                               # White SPace (maybe add square brakets)

# see 2.2.3. Long Header Fields
CRLF = r'(?:\r\n)'                                        # Carriage Return and Line Feed

# see 3.2.1. Quoted characters
QUOTED_PAIR = r'(?:\\.)'

# see 3.2.2. Folding White Space and Comments
FWS = r'(?:(?:' + WSP + '*' + CRLF + r')?' + WSP + r'+)'
CTEXT = r'[\x21-\x27\x2A-\x5B\x5D-\x7E]'                  # comment text: printable US-ASCII chars but `(`, `)`, `\`
CCONTENT = r'(?:' + CTEXT + r'|' + QUOTED_PAIR + r')'
COMMENT = r'\((?:' + FWS + r'?' + CCONTENT + r')*' + FWS + r'?\)'
CFWS = r'(?:(?:(?:' + FWS + r'?' + COMMENT + r')+' + FWS + r'?)' + r'|' + FWS + r')'

# see 3.2.3. Atom
ATEXT = r'[a-zA-Z0-9!#\$%&\'\*\+\-/=\?\^_`\{\|\}~]'       # atom text: printable US-ASCII chars not including specials
ATOM = CFWS + r'?' + ATEXT + r'+' + CFWS + r'?'
DOT_ATOM_TEXT = ATEXT + r'+(?:\.' + ATEXT + r'+)*'
DOT_ATOM = CFWS + r'?' + DOT_ATOM_TEXT + CFWS + r'?'

# see 3.2.4. Quoted string
QTEXT = r'[\x21\x23-\x5B\x5D-\x7E]'                       # quoted text: printable ASCII chars but `"`, `\`
QCONTENT = r'(?:' + QTEXT + r'|' + QUOTED_PAIR + r')'
QUOTED_STRING = CFWS + r'?' + r'"(?:' + FWS + r'?' + QCONTENT + r')*' + FWS + r'?' + r'"' + CFWS + r'?'

# see 3.4.1. Addr-Spec
LOCAL_PART = r'(?:' + DOT_ATOM + r'|' + QUOTED_STRING + r')'
DTEXT = r'[\x21-\x5A\x5E-\x7E]' # domain text: printable US-ASCII chars but `(`, `)`, `\`
DOMAIN_LITERAL = CFWS + r'?' + r'\[' + r'(?:' + FWS + r'?' + DTEXT + r')*' + FWS + r'?\]' + CFWS + r'?'
DOMAIN = r'(?:' + DOT_ATOM + r'|' + DOMAIN_LITERAL + r')'
ADDR_SPEC = r'(' + LOCAL_PART + r')' + '@' + r'(' + DOMAIN + r')'

# compiled regex patterns
VALID_ADDRESS_PATTERN = re.compile(r'^' + ADDR_SPEC + r'$')         # a valid address must match exactly ADDR_SPEC
UNQUOTED_LOCAL_PART_DOTS_PATTERN = re.compile(r"^\.|\.{2,}|\.$")    # dot explicit problems for unquoted local part
UNQUOTED_LOCAL_PART_PATTERN = re.compile(DOT_ATOM)                  # without quotes, it follows the DOT_ATOM syntax
QUOTED_LOCAL_PART_PATTERN = re.compile(r'^' + QUOTED_STRING + r'$') # when quoted, the local part syntax is more flexible
DOMAIN_DNS_LABEL_DOTS_PATTERN = re.compile("\.{2,}")                # domain DNS labels must be separated by a single dot
DOMAIN_DNS_LABEL_HYPHENS_PATTERN = re.compile("^-|-$")              # domain DNS labels must not begin nor end with a hyphen
DOMAIN_NAME_PATTERN = UNQUOTED_LOCAL_PART_PATTERN                   # when not a literal, the domain has the ULP syntax 
DOMAIN_LITERAL_PATTERN = re.compile(r'^' + DOMAIN_LITERAL + r'$')   # IP format

# lenght constants
EMAIL_ADDRESS_MAX_LENGTH = 254
LOCAL_PART_MAX_LENGTH = 64
DOMAIN_MAX_LENGTH = 255
DNS_LABEL_MAX_LENGHT = 64