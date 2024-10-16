from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth import get_user_model
import logging

CustomUser = get_user_model()
logger = logging.getLogger(__name__)


class IntegratedAuthenticationBackend(LDAPBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            ldap_user = super().authenticate(
                request, username=username, password=password, **kwargs)
            if ldap_user is None:
                return None

            # Get attributes safely
            attrs = getattr(ldap_user, 'attrs', {})
            email = attrs.get("mail", [username + "@baylor-uganda.org"])[0]
            fname = attrs.get("givenName", [""])[0]
            lname = attrs.get("sn", [""])[0]
            sam_account_name = attrs.get("sAMAccountName", [username])[0]

            if not sam_account_name:
                logger.error(
                    f"sAMAccountName is missing for the LDAP user {username}.")
                raise ValueError(
                    "sAMAccountName not found in user attributes.")

            # Create or get the user in the Django database with required defaults
            user, created = CustomUser.objects.update_or_create(
                email=email,
                defaults={
                    'fname': fname,
                    'lname': lname,
                    'is_approved': True,
                    'is_staff': True,
                    'is_active': True,
                    'is_ldap_user': True  # Set the LDAP user flag
                }
            )

            # Update password if needed
            if created or not user.check_password(password):
                user.set_password(password)
                user.save()
                logger.info(
                    f"{'Created' if created else 'Updated'} LDAP user in Django: {user.email}")

            return user  # Return the authenticated user

        except Exception as e:
            logger.error(f"LDAP authentication error for {username}: {str(e)}")

        # If LDAP authentication fails, attempt local authentication
        try:
            logger.debug(f"Attempting local authentication for {username}.")
            # Attempt to retrieve the local user by email
            user = CustomUser.objects.get(email=username)
            if user.check_password(password):
                logger.info(f"Local authentication successful for {username}.")
                # Ensure is_ldap_user is False for locally authenticated users
                if user.is_ldap_user:
                    user.is_ldap_user = False
                    user.save()
                    logger.info(
                        f"Updated is_ldap_user to False for {username}.")
                return user  # Return the authenticated user
            else:
                logger.warning(
                    f"Invalid credentials for local user: {username}")

        except CustomUser.DoesNotExist:
            logger.warning(
                f"Local authentication failed for non-existent user: {username}")
        except Exception as e:
            logger.error(
                f"Error during local authentication for {username}: {str(e)}")

        return None  # Return None if authentication fails
