from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth import get_user_model
from django.db import transaction
import logging
from .models import LDAPUser

logger = logging.getLogger(__name__)
CustomUser = get_user_model()


class IntegratedAuthenticationBackend(LDAPBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate against LDAP first, then fall back to local database.
        """
        if not username or not password:
            logger.warning("Authentication attempted with missing credentials")
            return None

        # First try LDAP authentication
        try:
            with transaction.atomic():
                ldap_user = super().authenticate(
                    request, username=username, password=password, **kwargs)
                if ldap_user:
                    return self._handle_ldap_user(ldap_user, password)
        except Exception as e:
            logger.error(f"LDAP authentication error for {username}: {str(e)}")

        # Fall back to local authentication
        return self._authenticate_local(username, password)

    def _handle_ldap_user(self, ldap_user, password):
        """
        Handle LDAP user creation/update in both LDAPUser and CustomUser models.
        """
        try:
            attrs = getattr(ldap_user, 'attrs', {})

            logger.debug(f"Raw LDAP attributes: {attrs}")

            # Extract LDAP attributes with robust fallbacks
            email = attrs.get("mail", [None])[
                0] or f"{ldap_user.username}@baylor-uganda.org"
            sam_account_name = attrs.get(
                "sAMAccountName", [ldap_user.username])[0]

            # Get name components with multiple fallback options
            given_name = attrs.get("givenName", [""])[0]
            cn_parts = attrs.get("cn", [""])[0].split()
            given_name = given_name or (
                cn_parts[0] if cn_parts else sam_account_name)
            surname = attrs.get("sn", [""])[0]

            # Get full name with multiple fallback options
            full_name = attrs.get("cn", [""])[0] or f"{given_name} {surname}"

            # Log extracted information
            logger.info(
                f"Extracted user info - Email: {email}, Username: {sam_account_name}, "
                f"Full Name: {full_name}, First Name: {given_name}, Last Name: {surname}"
            )

            with transaction.atomic():
                # Update or create LDAPUser
                ldap_user_record, _ = LDAPUser.objects.update_or_create(
                    username=sam_account_name,
                    defaults={
                        'email': email,
                        'full_name': full_name,
                        'username': sam_account_name,
                    }
                )

                # Update or create CustomUser
                custom_user, created = CustomUser.objects.update_or_create(
                    email=email,
                    defaults={
                        'fname': given_name,
                        'lname': surname,
                        'is_staff': True,
                        'is_active': True,
                        'organisation_name': 'Baylor Uganda',
                        'is_approved': True,
                    }
                )

                if created or not custom_user.check_password(password):
                    custom_user.set_password(password)
                    custom_user.save()

                logger.info(f"Successfully processed LDAP user: {email}")
                return custom_user

        except Exception as e:
            logger.error(f"Error processing LDAP user: {str(e)}")
            raise

    def _authenticate_local(self, username, password):
        """
        Attempt local database authentication.
        """
        try:
            user = CustomUser.objects.get(email=username)
            if user.check_password(password):
                logger.info(f"Local authentication successful for: {username}")
                return user

            logger.warning(f"Invalid password for local user: {username}")
            return None

        except CustomUser.DoesNotExist:
            logger.warning(f"No local user found with email: {username}")
            return None
        except Exception as e:
            logger.error(
                f"Local authentication error for {username}: {str(e)}")
            return None

    def get_user(self, user_id):
        """
        Retrieve user by ID from CustomUser model.
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
