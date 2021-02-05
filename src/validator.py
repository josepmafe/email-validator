import traceback

from params import (
    EMAIL_ADDRESS_MAX_LENGTH, LOCAL_PART_MAX_LENGTH, DOMAIN_MAX_LENGTH, DNS_LABEL_MAX_LENGHT,
    VALID_ADDRESS_PATTERN, UNQUOTED_LOCAL_PART_DOTS_PATTERN, UNQUOTED_LOCAL_PART_PATTERN, QUOTED_LOCAL_PART_PATTERN,
    DOMAIN_DNS_LABEL_HYPHENS_PATTERN, DOMAIN_DNS_LABEL_DOTS_PATTERN, DOMAIN_NAME_PATTERN, DOMAIN_LITERAL_PATTERN
)
from exceptions import AddressNotSetError, NotValidEmailAddressSyntaxError, LocalPartSyntaxError, DomainSyntaxError

class EmailValidator():
    """
    Class used to validate an e-mail address. 
    
    Any e-mail address is made of a local part, the symbol @ and a domain name.
    According to the curernt standards, the local part is case-sentive, but the 
    recieving hosts must deliver messages in a case-independent way. Thus, we 
    treat the whole addresses in this latter manner.
    
    It uses the syntax rules from RFC 5322 (https://tools.ietf.org/html/rfc5322)
    """
    def __init__(self, email_address = None):
        """
        Parameters
        ----------
        email_address: str, optional
            the address to validate. it can be set either when the 
            class is instantiated or when the method `self.validate`
            is called. however, it is recommended to set pass it in
            the latter case
        """
        self.email_address_set_at_init = email_address is not None
        self.email_address = str(email_address).lower() if self.email_address_set_at_init else None
        self.local_part = None
        self.domain = None
        
        #lenghts
        self._email_address_max_length = EMAIL_ADDRESS_MAX_LENGTH
        self._local_part_max_length = LOCAL_PART_MAX_LENGTH
        self._domain_max_length = DOMAIN_MAX_LENGTH
        self._dns_label_max_length = DNS_LABEL_MAX_LENGHT
        
        # patterns
        self._valid_address_pattern = VALID_ADDRESS_PATTERN
        self._unquoted_local_part_dots_pattern = UNQUOTED_LOCAL_PART_DOTS_PATTERN
        self._unquoted_local_part_pattern = UNQUOTED_LOCAL_PART_PATTERN
        self._quoted_local_part_pattern = QUOTED_LOCAL_PART_PATTERN
        self._lhd_domain_dns_label_hyphens_pattern = DOMAIN_DNS_LABEL_HYPHENS_PATTERN
        self._lhd_domain_dns_label_dots_pattern = DOMAIN_DNS_LABEL_DOTS_PATTERN
        self._lhd_domain_dns_label_pattern = DOMAIN_NAME_PATTERN
        self._domain_literal_pattern = DOMAIN_LITERAL_PATTERN
    
    def _is_call_valid(self, attr):
        if attr is None:
            print(
                ('WARNING: This private method must not be called directly. ' 
                 'Use `self.is_email_valid()` or `cls.fast_validation()` instead.')
            )
            return False
        
        return True
        
    def _validate_base(self, simple = False):
        """
        Checks if the e-mail address has an appropiate base format. 
        
        NOTE: This (private) method must not be called directly but only via `self.validate`.
        """
        if not self._is_call_valid(self.email_address):
            return
        
        if len(self.email_address) > self._email_address_max_length:
            raise NotValidEmailAddressSyntaxError(
                f"The address can not be longet than {self._email_address_max_length} characters"
            )
        
        # when called by `cls.fast_validation`
        if simple:
            if self._valid_address_pattern.search(self.email_address) is None:
                raise NotValidEmailAddressSyntaxError((f"Invalid syntax for address `{self.email_address}`"))
            
            local_part, _, domain = self.email_address.rpartition('@')
            if len(local_part) > self._local_part_max_length or len(domain) > self._domain_max_length:
                raise NotValidEmailAddressSyntaxError((f"Invalid syntax for address `{self.email_address}`"))
                   
        # when called by `self.is_email_valid` or by `self.validate()`    
        else:              
            if self.email_address.count('@') == 0:
                raise NotValidEmailAddressSyntaxError("Expecting address syntax like `localpart@domainname`")

            # assume that in case an address has more than 1 `@` character, the one
            # delimiting local part and the domain is the last one
            self.local_part, _, self.domain = self.email_address.rpartition('@')
    
    def _find_invalid_chars(self, text, pattern):
        """Find the characters from `text` not matching the `pattern` (the so-called invalid characters)"""
        valid_characters = ''.join(pattern.findall(text))
        if valid_characters:
            return set(text).difference(valid_characters)
        else:
            return sorted(set(text))
    
    def _validate_local_part_quoted(self):
        """
        Validates the local part format when it is quoted.
        
        NOTE: This (private) method must not be called directly but only via `self.validate`.
        """
        if not self._is_call_valid(self.local_part):
            return
        
        if self.local_part.count('"') > 2:
            raise LocalPartSyntaxError(
                (f"Invalid syntax for quoted local part `{self.local_part}`.\n"
                  "It must contain only one quoted string, i.e., it can't contain "
                """more than 2 `"` characters.""")
            )
            
        invalid_chars = self._find_invalid_chars(self.local_part, self._quoted_local_part_pattern)
        if invalid_chars:
            raise LocalPartSyntaxError(
                (f"Invalid syntax for quoted local part `{self.local_part}`.\n"
                 f"It contains the following non-valid characters: `{''.join(invalid_chars)}`.\n" 
                  """The accepted ones are printable US-ASCII characters but printable ASCII chars but `"` and `\`""")
            )
        
    def _validate_local_part_unquoted(self):
        """
        Validates the local part format when it is unquoted.
        
        NOTE: This (private) method must not be called directly but only via `self.validate`.
        """
        if not self._is_call_valid(self.local_part):
            return
        
        if self._unquoted_local_part_dots_pattern.search(self.local_part) is not None:
            raise LocalPartSyntaxError(
                (f"Invalid syntax for local part `{self.local_part}`.\n"
                  "Unquoted local parts cannot either begin, end, or have two or more consecutive dot `.` characters.")
            )
            
        invalid_chars = self._find_invalid_chars(self.local_part, self._unquoted_local_part_pattern)
        if invalid_chars:
            raise LocalPartSyntaxError(
                (f"Invalid syntax for unquoted local part `{self.local_part}`.\n"
                 f"It contains the following non-valid characters: `{''.join(invalid_chars)}`.\n" 
                  "The accepted ones are printable US-ASCII characters not including the specials, i.e.:\n"
                  "  - Latin letters `a` to `z` and `A` to `Z`\n"
                  "  - Digits `0` to `9`\n"
                  "  - Printable characters `!#$%&'*+-/=?^_`{|}~`\n"
                  "  - Dot `.`, as long as it is not the first or last character and that it does not appear consecutively")
            )
            
    def _validate_local_part(self):
        """
        Validates the local part syntax according to the rules extracted from 
        RFC 5322
        
        This (private) method must not be called directly but only via `self._validate_local_part`.
        """
        if not self._is_call_valid(self.local_part):
            return
        
        if len(self.local_part) > self._local_part_max_length:
            raise LocalPartSyntaxError(f"The local part cannot be longer than {self._local_part_max_length} characters")
        if self.local_part.startswith('"') and self.local_part.endswith('"'):
            self._validate_local_part_quoted()
        else:
            self._validate_local_part_unquoted()
            
    def _validate_domain_literal(self):
        """
        Validates the domain name when it is an IP address.
        
        NOTE: This (private) method must not be called directly but only via `self.validate`.
        """
        if not self._is_call_valid(self.domain):
            return
        
        if self._domain_literal_pattern.search(self.domain) is None:
            raise DomainSyntaxError("Invalid domain literal syntax")
            
        # TODO: add further distinction between IP versions
            
    def _validate_LDH_domain(self):
        """
        Validates the domain name when it follows the Letters, Digits, Hyphen (LHD) rule.
        
        NOTE: This (private) method must not be called directly but only via `self.validate`.
        """
        if not self._is_call_valid(self.domain):
            return
        
        # the domain name is a sequence of dot-separated DNS labels
        if self._lhd_domain_dns_label_dots_pattern.search(self.domain) is not None:
            raise DomainSyntaxError(
                (f"Invalid format for domain name `{self.domain}`.\n"
                  "DNS labels must be separated by a single dot `.` character.")
            )
                
        self.dns_labels = self.domain.split(".")
        for label in self.dns_labels:
            if len(label) > self._dns_label_max_length:
                raise DomainSyntaxError(
                    (f"Invalid syntax for domain name `{self.domain}`.\n"
                     f"DNS labels cannot be longer than {self._dns_label_max_length} characters")
                )
            
            if self._lhd_domain_dns_label_hyphens_pattern.search(label) is not None:
                raise DomainSyntaxError(
                    (f"Invalid syntax for domain name `{self.domain}`.\n"
                      "DNS labels cannot either begin or end with a hyphen `-` character.")
                )
                
            invalid_chars = self._find_invalid_chars(label, self._lhd_domain_dns_label_pattern)
            if invalid_chars:
                raise DomainSyntaxError(
                    (f"Invalid format for domain name `{self.domain}`.\n"
                     f"The DNS label `{label}` contains the following non-valid characters: `{''.join(invalid_chars)}`.\n"
                      "The accepted ones are printable US-ASCII characters not including the specials, i.e.:\n"
                      "  - Latin letters `a` to `z` and `A` to `Z`\n"
                      "  - Digits `0` to `9`\n"
                      "  - Printable characters `!#$%&'*+-/=?^_`{|}~`\n"
                      "  - Dot `.`, as long as it is not the first or last character and that it does not appear"
                          "consecutively")
                )    
        
    def _validate_domain(self):
        """
        Validates the domain name of an email address according to the rules extracted from 
        https://en.wikipedia.org/wiki/Email_address#Domain
        
        This (private) method must not be called directly but only via `self._validate_local_part`.
        """
        if not self._is_call_valid(self.domain):
            return
        
        if len(self.domain) > self._domain_max_length:
            raise DomainSyntaxError(
                (f"Invalid syntax for domain name `{self.domain}`.\n"
                 f"It cannot be longer than {self._domain_max_length} characters")
            )
            
        # when the domain name is an IP address, it is surrounded by square brackets.
        if self.domain.startswith('[') and self.domain.endswith(']'):
            self._validate_domain_literal()
        else:
            self._validate_LDH_domain()
            
    def validate(self, email_address = None):
        """
        The validation process is done in three steps:
          1. Check if the email address has a valid base format, i.e., `localpart@domainname`.
          2. Check the local part format.
          3. Check the domain name format

        If any validation step fails, the function raises an exception explaining what went wrong.
        
        Parameters
        ----------
        email_address: str, optional
            the address to validate. there is no need to pass 
            it if it was set during the class instantiation
        """
        if email_address is None and self.email_address is None:
            raise AddressNotSetError(
                ("The address to validate must be set either when the class "
                 "is instantiated or when this method is called.")
            )
            
        if self.email_address_set_at_init and email_address != self.email_address:
            print(
                (f"WARNING: the email address `{self.email_address}` was when "
                 f"instantiating the class, but now you are trying to validate "
                 f"a different address `{email_address}`. "
                 f"To avoid this warning, do not set any email address during the "
                 f"class instantiation, as indicated in the docs.")
            )
                   
        # for convenience, cast to string (to avoid exceptions due to wrong input types) and lowercase
        self.email_address = str(email_address).lower()
        self._validate_base()
        self._validate_local_part()
        self._validate_domain()
    
    def _handle_error(self, error, show_traceback):
        """
        Controls how to handle errors raised when validating an email address.
        The current process is to print the error, optionally show its traceback
        and return False, as an address that raises an error during its validation
        is assumed to be an invalid one.
        
        Parameters
        ----------
        error: Exception
            the exception to be handled
        show_traceback: bool
            whether to print the error traceback or not
        
        Returns
        -------
        False: bool
            an email address that raises an error during its validation
            is assumed to be an invalid one
        """
        if show_traceback:
            lines = traceback.format_tb(error.__traceback__)
            for line in lines:
                print(line)
        print(f'{type(error).__name__}: {error}')
        return False
    
    @classmethod
    def fast_validation(cls, email_address):
        """
        Convenience classmethod to check where an email address is valid or not. 
        It checks whether the address syntax (including the length of its parts) 
        is valid and returns a boolean accordingly.
        
        For a more exhaustive validation, one can use `self._is_email_valid()`
        
        Parameters
        ----------
        email_address: str
            the address to validate
        
        Returns
        -------
        address_is_valid: bool
            whether the input email address is valid or not
        """
        try:
            return cls(email_address)._validate_base(simple = True) is None
        except NotValidEmailAddressSyntaxError as expected_error:
            return False
        except Exception as unexpected_error:
            print(f'Found the following unexpected error when validating the address `{email_address}`')
            return cls()._handle_error(unexpected_error, show_traceback = True)
        
    def is_email_valid(self, email_address, show_traceback = False):
        """
        Convenience function to check where an email address is valid or not. 
        Unless `self.validate()`, it does not raise any exceptions but prints them.
        For more information see the `validate` function.
        
        Parameters
        ----------
        email_address: str
            the address to validate
        
        Returns
        -------
        address_is_valid: bool
            whether the input email address is valid or not
        """
        try:
            return self.validate(email_address) is None
        except (NotValidEmailAddressSyntaxError, LocalPartSyntaxError, DomainSyntaxError) as expected_error:
            return self._handle_error(expected_error, show_traceback = show_traceback)
        except Exception as unexpected_error:
            print(f'Found the following unexpected error when validating the address `{email_address}`')
            return self._handle_error(unexpected_error, show_traceback = True) 