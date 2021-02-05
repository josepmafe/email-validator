# Email validator

Any e-mail address is made of a local part, the symbol `@` and a domain name. Thus, the validation process is done in three steps, and using RegEx patterns:
1. Check if the email address has a valid base format, i.e., `localpart@domainname`.
2. Check the local part format.
3. Check the domain name format.

Because a vast majority of the users use an unquoted address, the validator do not accepts addresses with a quoted local part. For more information about the formatting of the local part, see this [link](https://en.wikipedia.org/wiki/Email_address#Local-part). In addition, as IP domain names are extremly rare except in email spam, the validator does not accept them either. For more information about the domain formatting, see this other [link](https://en.wikipedia.org/wiki/Email_address#Domain).

Of course, using RegEx patterns I can only verify that the email address is sintactically correct, but not whether it was misstyped or if it (exists checking the SMTP server). For a more complete validator that does extra verifications, one might use the `Python` third-party library `validate-email` (see their GitHub [repo](https://github.com/syrusakbary/validate_email)).

In the following cell I include `EmailValidator`, which is a `Python` class designed to check whether an email address is valid or not. To use it, one only needs to instantiate it and use its convenience function `is_valid`, which returns a boolean value indicating whether the input email is valid or not. In case `is_email_valid` returns `False`, it also prints a message indicating the  reason why. See the following example:
```python
from validator import EmailValidator

validator = EmailValidator()
validator.is_email_valid('user@example.com')
# output: True
```

For a faster (and less exhaustive) validation, one can use its class method `fast_validation`, which also returns a boolean according to the validity of the input address but prints no messages (nor raises exceptions). See the following example:
```python
EmailValidator.fast_validation('userexample.com') # notice there is no need to instantiate the class
# output: False
```

Yet another (with error message):
```python
validator = EmailValidator()
validator.is_email_valid('userexample.com')
# prints: NotValidEmailAddressSyntaxError: Expecting address syntax like `localpart@domainname`
# output: False
```
