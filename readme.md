# Email validator

`email-validator` is a (project of) `Python` package designed to validate the syntax of a given email address. 

Any e-mail address is made of a local part, the symbol `@` and a domain name. Thus, the validation process is done in three steps, and using RegEx patterns:
1. Check if the email address has a valid base format, i.e., `localpart@domainname`.
2. Check the local part format.
3. Check the domain name format.

Of course, using RegEx patterns I can only verify that the email address is sintactically correct, but not whether it was misstyped or if it (exists checking the SMTP server). For a more complete validator that does extra verifications, one might use the `Python` third-party library `validate-email` (see their GitHub [repo](https://github.com/syrusakbary/validate_email)).

In the following cell one can see how to use `EmailValidator`, which is a `Python` class designed to check whether an email address is valid or not. To utilize it, one only needs to instantiate it and use its convenience function `is_email_valid`, which returns a boolean value indicating whether the input email is valid or not. In case `is_email_valid` returns `False`, it also prints a message indicating the  reason why. See the following example:
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

Yet another example (with error message):
```python
validator = EmailValidator()
validator.is_email_valid('userexample.com')
# prints: NotValidEmailAddressSyntaxError: Expecting address syntax like `localpart@domainname`
# output: False
```
