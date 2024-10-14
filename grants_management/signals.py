from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import (
    Grant,
    GrantApplicationResponses,
    TransformedGrantApplicationData,
    GrantApplication,
    GrantApplicationReview,
    GrantApplicationDocument,
    FilteredGrantApplicationResponse,
    DefaultApplicationQuestion,
    GrantApplicationDocument,
    BudgetTotal,
    GrantAccount,
    FundingAllocation,
    ProgressReport,
    Disbursement,
    GrantCloseOut,
    GrantCloseOutDocuments,
    Modifications,
    Requests,
    RequestReview,
    FinancialReport,
    Requirements,
    Extensions,
    GrantApplicationReviewDocument
)
from django.utils.html import escape as html_escape
from authentication.models import CustomUser
from notifications.models import Notification
from subgrantees.models import SubgranteeProfile
import logging
from django.db.models import Sum
from decimal import Decimal
from django.utils.html import strip_tags
import html
from django.db.models import Q
from django.db.models import F
import time

logger = logging.getLogger(__name__)


def send_formatted_email(subject, html_content, recipient_list):
    plain_message = strip_tags(html_content)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_content,
        fail_silently=False,
    )


def create_notification(user, notification_type, notification_category, text, **kwargs):
    notification = Notification.objects.create(
        notification_type=notification_type,
        notification_category=notification_category,
        text=text,
        **kwargs
    )
    notification.user.add(user)
    return notification


@receiver(post_save, sender=Grant)
def notify_grantees_on_grant_creation(sender, instance, created, **kwargs):
    if created:
        grantees = CustomUser.objects.filter(is_staff=False, is_approved=True)

        # Create a single Notification instance
        notification = Notification(
            notification_type="grantee",
            notification_category="new_grant",
            text=f"New funding opportunity available",
            grant=instance,
        )
        notification.save()  # Save to create the Notification instance in the database

        # Set all grantees as users for this single notification
        notification.user.set(grantees)

        # Sending email notifications
        email_list = [grantee.email for grantee in grantees]
        try:
            send_mail(
                "New Grant Available",
                f"A new funding opportunity has been added: {instance.name}. Please login and check the details in your dashboard.",
                settings.DEFAULT_FROM_EMAIL,
                email_list,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")



@receiver(post_save, sender=GrantApplicationDocument)
def notify_admin_on_grant_application(sender, instance, created, **kwargs):
    # Fetching the admins
    admin_users = CustomUser.objects.filter(is_staff=True)

    # Determine the notification message based on creation or update
    if created:
        message_type = "submitted"
        notification_text = (
            f"A new application for a funding opportunity has been submitted by {instance.user.organisation_name} "
            f"for: {instance.application.grant.name}."
        )
    else:
        message_type = "updated"
        notification_text = (
            f"The application for funding opportunity submitted by {instance.user.organisation_name} "
            f"for: {instance.application.grant.name} has been updated."
        )

    # Creating the notification object
    notification = Notification.objects.create(
        notification_type='admin',
        notification_category='grant_application',
        text=notification_text,
    )

    # Attaching users to the notification
    notification.user.set(admin_users)

    # Sending email notification to admins
    email_list = [admin.email for admin in admin_users]
    html_content = f"""
        <html>
        <body>
        <h2>Grant Application {message_type.capitalize()}</h2>
        <p>{html.escape(notification_text)}</p>
        <p>Please login and review it.</p>
        </body>
        </html>
    """
    send_formatted_email(
        subject=f"Grant Application {message_type.capitalize()}",
        html_content=html_content,
        recipient_list=email_list
    )


@receiver(post_save, sender=GrantApplicationResponses)
def transform_responses(sender, instance, **kwargs):
    try:
        # Ensure related instances exist
        user_exists = CustomUser.objects.filter(id=instance.user.id).exists()
        grant_exists = Grant.objects.filter(id=instance.grant.id).exists()

        if not user_exists:
            logger.error(f"User not found: User ID={instance.user.id}")
            return
        if not grant_exists:
            logger.error(f"Grant not found: Grant ID={instance.grant.id}")
            return

        with transaction.atomic():
            # Retrieve existing transformed data or create a new one
            transformed_data, created = (
                TransformedGrantApplicationData.objects.get_or_create(
                    user=instance.user,
                    grant=instance.grant,
                )
            )

            logger.info(f"TransformedGrantApplicationData created: {created}")

            # Initialize responses data structure
            if created:
                responses_data = {
                    "grant": {"grant_id": instance.grant.id, "responses": []},
                    "user": {"user_id": instance.user.id},
                }
            else:
                responses_data = transformed_data.transformed_data or {
                    "grant": {"grant_id": instance.grant.id, "responses": []},
                    "user": {"user_id": instance.user.id},
                }

            # Retrieve the related question instance
            question = instance.question

            # Debugging: Log the question details
            logger.info(
                f"Processing question: ID={question.id}, Type={question.question_type}, Text={question.text}"
            )

            # Add the response to the nested structure
            response = {
                "question_id": question.id,
                "answer": instance.answer,
                "choices": instance.choices or None,
                "question_type": question.question_type,  # Include question_type
                "text": question.text,  # Include text
            }

            # Debugging: Log the response details
            logger.info(f"Response being added: {response}")

            # Check if the question already exists in the responses
            existing_responses = next(
                (
                    r
                    for r in responses_data["grant"]["responses"]
                    if r["question_id"] == response["question_id"]
                ),
                None,
            )
            if existing_responses:
                existing_responses.update(response)
            else:
                responses_data["grant"]["responses"].append(response)

            # Update or create the transformed data instance
            transformed_data.transformed_data = responses_data
            transformed_data.save()

            # Debugging: Log the saved transformed data
            logger.info(
                f"Transformed data saved: {transformed_data.transformed_data}")

    except Exception as e:
        logger.error(f"Error transforming responses: {e}")


@receiver(post_save, sender=GrantApplication)
def create_grant_account_on_complete(sender, instance, created, **kwargs):
    if not created and instance.status == "approved":
        if not GrantAccount.objects.filter(
            grant=instance.grant, account_holder=instance.subgrantee
        ).exists():
            budget_total = BudgetTotal.objects.filter(
                grant=instance.grant, application=instance, user=instance.subgrantee
            ).first()
            if not budget_total:
                logger.error(
                    f"No BudgetTotal found for grant ID {instance.grant.id}")
                return
            GrantAccount.objects.create(
                grant=instance.grant,
                account_holder=instance.subgrantee,
                budget_total=budget_total,
            )


@receiver(post_save, sender=GrantApplicationReview)
def notify_subgrantee_on_review(sender, instance, created, **kwargs):
    with transaction.atomic():
        print("Inside notify_subgrantee_on_review")
        grant_application = instance.application
        user = grant_application.subgrantee

        # Notify only if the status has changed
        if user:
            if created or instance.status != instance.__class__.objects.get(pk=instance.pk).status:
                print(
                    f"Before update: Application {grant_application.id} reviewed = {grant_application.reviewed}")

                notification_text = f"Your application for '{grant_application.grant.name}' has been set to {instance.status}. "

                if instance.status == "approved":
                    notification_text += "Please proceed to create your budget."

                elif instance.status == "rejected":
                    notification_text += "Thank you for your application."

                elif instance.status == "negotiate":
                    notification_text += "Please review the feedback and respond accordingly."

                # Create notification
                notification = Notification.objects.create(
                    notification_type='grantee',
                    notification_category='grant_review',
                    text=notification_text,
                    review=instance,
                )
                notification.user.add(user)
                notification.save()

                # Send email notification
                html_content = f"""
                <html>
                <body>
                <h2>Grant Application Review</h2>
                <p>Dear {html_escape(user.organisation_name)},</p>
                <p>Your application for funding opportunity {html_escape(grant_application.grant.name)} has been reviewed.</p>
                <p>Status: {html_escape(instance.status.capitalize())}</p>
                <p>{notification_text}</p>
                <p>{'Please login to see the remarks and next steps.' if instance.status != 'rejected' else 'Thank you for your time and interest. We hope to work with you in the future.'}</p>
                </body>
                </html>
                """
                send_formatted_email(
                    subject=f"Grant Application Review - {instance.status.capitalize()}",
                    html_content=html_content,
                    recipient_list=[user.email]
                )


@receiver(post_save, sender=GrantApplicationReviewDocument)
def update_notification_with_upload(sender, instance, **kwargs):
    # Find the Notification related to this review
    notification = Notification.objects.filter(review=instance.review).first()

    # Update the notification's uploads field if a related notification is found
    if notification:
        notification.uploads = instance
        notification.save()



@receiver(post_save, sender=GrantApplicationDocument)
def notify_grantee_on_successful_submission(sender, instance, created, **kwargs):
    if created:
        grant_application = instance.application
        user = grant_application.subgrantee

        if user:
            # Check if a notification already exists for this application
            existing_notification = Notification.objects.filter(
                user=user,
                application=grant_application,
            ).first()

            if not existing_notification:
                notification = Notification.objects.create(
                    notification_type='grantee',
                    notification_category='grant_submission',
                    text=f"Your application for the funding opportunity '{grant_application.grant.name}' have been successfully submitted.",
                    application=grant_application,
                    grant=grant_application.grant

                )
                notification.user.add(user)

                # Optional: Save the notification again if additional fields are set
                notification.save()

                # Update the grant application as signed if not already done
                if not grant_application.signed:
                    grant_application.signed = True
                    grant_application.save()

                html_content = f"""
                <html>
                <body>
                <h2>Grant Application</h2>
                <p>Dear {html.escape(user.organisation_name)},</p>
                <p>Your application for funding opportunity {html.escape(grant_application.grant.name)} has been submitted successfully</p>
                <p>Please wait for a response as its being reviewed.</p>
                </body>
                </html>
                """
                send_formatted_email(
                    subject=f"Grant Application",
                    html_content=html_content,
                    recipient_list=[user.email]
                )


@receiver(post_save, sender=GrantApplicationResponses)
def store_filtered_responses(sender, instance, **kwargs):
    question = instance.question

    if not question:
        return

    application = GrantApplication.objects.filter(
        grant=instance.grant, subgrantee=instance.user
    ).first()

    if application:
        if (
            question.text
            == "Please be sure to include the following documents listed in the checklist as attachments to your EOI."
        ):
            checkbox_responses = instance.choices

            if isinstance(checkbox_responses, str):
                import json

                checkbox_responses = json.loads(checkbox_responses)

            checked_choices = [
                item["check"] for item in checkbox_responses if "check" in item
            ]

            FilteredGrantApplicationResponse.objects.filter(
                application=application, user=instance.user, question=question
            ).delete()

            for choice in checked_choices:
                FilteredGrantApplicationResponse.objects.update_or_create(
                    application=application,
                    user=instance.user,
                    question=question,
                    defaults={
                        "choices": checked_choices,
                    },
                )

        elif (
            question.text
            == "Please indicate the anticipated budget total needed to carry out the work listed above (UGX)"
        ):
            budget_total = instance.answer

            BudgetTotal.objects.filter(
                application=application, grant=instance.grant, user=instance.user
            ).delete()

            BudgetTotal.objects.update_or_create(
                application=application,
                grant=instance.grant,
                user=instance.user,
                defaults={
                    "budget_total": budget_total,
                },
            )


@receiver(post_save, sender=FundingAllocation)
def update_grant_account(sender, instance, created, **kwargs):
    grant_account = instance.grant_account
    budget_item = instance.item

    if created:  # Handle creation
        grant_account.current_amount -= instance.amount
        budget_item.amount -= instance.amount
    else:  # Handle update
        previous_instance = FundingAllocation.objects.get(pk=instance.pk)
        amount_difference = instance.amount - previous_instance.amount

        grant_account.current_amount -= amount_difference
        budget_item.amount -= amount_difference

    # Save the updated grant account and budget item
    grant_account.save()
    budget_item.save()


@receiver(post_save, sender=Disbursement)
def notify_on_disbursement(sender, instance, created, **kwargs):
    grant_account = instance.grant_account
    subgrantee_user = grant_account.account_holder
    action = "credited" if created else "updated"

    if created:
        new_amount = instance.disbursement_amount
    else:
        # Calculate the new disbursement amount
        original = Disbursement.objects.get(pk=instance.pk)
        new_amount = instance.disbursement_amount - original.disbursement_amount

    # Update the grant account's current amount
    grant_account.current_amount += new_amount
    grant_account.save()

    if subgrantee_user:
        try:
            subgrantee_profile = SubgranteeProfile.objects.get(
                user=subgrantee_user)
            subgrantee_text = f"Your account for {grant_account.grant.name} has been {action}. Please go ahead and allocate your funds."

            # Create or update notification
            notifications = Notification.objects.filter(
                notification_type="grantee",
                notification_category="disbursement_received",
                subgrantee=subgrantee_profile,
                grant=grant_account.grant,
            )

            if notifications.exists():
                # Update all matching notifications
                for notification in notifications:
                    notification.text = subgrantee_text
                    notification.save()
            else:
                # Create a new notification
                notification = Notification.objects.create(
                    notification_type="grantee",
                    notification_category="disbursement_received",
                    subgrantee=subgrantee_profile,
                    grant=grant_account.grant,
                    text=subgrantee_text
                )

            notification.user.add(subgrantee_user)

            # Prepare email content
            subgrantee_html_content = f"""
            <html>
            <body>
                <h2>Disbursement {action.capitalize()} for Funding Opportunity: {html.escape(grant_account.grant.name)}</h2>
                <p>Dear {html.escape(str(subgrantee_profile))},</p>
                <p>Your account for the funding opportunity '{html.escape(grant_account.grant.name)}' has been {action}.</p>
                <h3>Disbursement Details:</h3>
                <ul>
                    <li><strong>Disbursement Date:</strong> {instance.disbursement_date}</li>
                    <li><strong>Amount:</strong> {new_amount} UGX</li>
                    <li><strong>Total Disbursed:</strong> {instance.disbursement_amount} UGX</li>
                    <li><strong>Remaining Budget:</strong> {instance.budget_balance} UGX</li>
                </ul>
                <p>Thank you for your continued efforts.</p>
            </body>
            </html>
            """
            # Send the email
            send_formatted_email(
                subject=f"Disbursement {action.capitalize()} for Grant: {grant_account.grant.name}",
                html_content=subgrantee_html_content,
                recipient_list=[subgrantee_user.email]
            )

        except SubgranteeProfile.DoesNotExist:
            print(
                f"No SubgranteeProfile found for user: {subgrantee_user.email}")


@receiver(post_save, sender=ProgressReport)
def notify_on_report_review(sender, instance, created, **kwargs):
    if instance.review_status == 'reviewed':
        grant_account = instance.grant_account
        subgrantee = grant_account.account_holder

        if subgrantee:
            text = f"Your progress report for '{grant_account.grant.name}' has been {instance.reviewer_status}."

            # Create or update the notification
            notification, created = Notification.objects.get_or_create(
                notification_type="grantee",
                notification_category="status_report_reviewed",
                grant=grant_account.grant,
                progress_report=instance,
                defaults={'text': text}
            )

            # If the notification already existed, update its text
            if not created:
                notification.text = text
                notification.save()

            # Add the user to the notification's user set
            notification.user.add(subgrantee)

            # Send email notification
            send_mail(
                subject=f"Progress Report Reviewed for Grant: {instance.grant_account.grant.name}",
                message=f"""
                Dear {subgrantee.organisation_name},

                Your progress report for the funding opportunity '{instance.grant_account.grant.name}' has been {instance.reviewer_status} and below are the comments from the grantor.
                
                Review Details:
                Review Date: {instance.last_updated}
                Comments: {instance.review_comments}

                Thank you for your continued efforts.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subgrantee.email],
                fail_silently=False,
            )


@receiver(post_save, sender=Disbursement)
def notify_on_disbursement(sender, instance, created, **kwargs):
    grant_account = instance.grant_account
    subgrantee_user = grant_account.account_holder
    action = "credited" if created else "updated"
    text = f"Your account for {grant_account.grant.name} has been {action} with an amount of {instance.disbursement_amount} UGX."

    if subgrantee_user:
        try:
            # Attempt to get the SubgranteeProfile associated with this user
            subgrantee_profile = SubgranteeProfile.objects.get(
                user=subgrantee_user)

            # Create notification object
            notification = Notification.objects.create(
                notification_type="grantee",
                notification_category="disbursement_received",
                text=text,
                subgrantee=subgrantee_profile,  # Use the SubgranteeProfile here
                grant=grant_account.grant
            )
            # Add the user to the notification's Many-to-Many field
            notification.user.add(subgrantee_user)

            html_content = f"""
            <html>
            <body>
                <h2>Disbursement {action.capitalize()} for Grant: {html.escape(grant_account.grant.name)}</h2>
                <p>Dear {html.escape(subgrantee_user.organisation_name)},</p>
                <p>Your account for the funding opportunity '{html.escape(grant_account.grant.name)}' has been {action}.</p>
                <h3>Disbursement Details:</h3>
                <ul>
                    <li><strong>Disbursement Date:</strong> {instance.disbursement_date}</li>
                    <li><strong>Amount:</strong> {instance.disbursement_amount} UGX</li>
                    <li><strong>Balance:</strong> {instance.budget_balance} UGX</li>
                </ul>
                <p>Thank you for your continued efforts.</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject=f"Disbursement {action.capitalize()} for Grant: {grant_account.grant.name}",
                html_content=html_content,
                recipient_list=[subgrantee_user.email]
            )
        except SubgranteeProfile.DoesNotExist:
            # Handle the case where there's no SubgranteeProfile for this user
            print(
                f"No SubgranteeProfile found for user: {subgrantee_user.email}")


@receiver(post_save, sender=Disbursement)
def update_grant_account_status(sender, instance, **kwargs):
    grant_account = instance.grant_account
    budget_balance = instance.budget_balance

    if budget_balance <= Decimal('0'):
        grant_account.disbursed = 'fully_disbursed'
    elif budget_balance < grant_account.budget_total.budget_total:
        grant_account.disbursed = 'partially_disbursed'
    else:
        grant_account.disbursed = 'not_disbursed'

    grant_account.save()


@receiver(post_save, sender=GrantCloseOut)
def handle_grant_closeout(sender, instance, created, **kwargs):
    if created:
        Requests.objects.create(
            request_type='grant_closeout',
            user=instance.initiated_by,
            grant_closeout=instance
        )
    else:
        request, created = Requests.objects.get_or_create(
            request_type='grant_closeout',
            user=instance.initiated_by,
            grant_closeout=instance
        )
        request.save()


@receiver(post_save, sender=Modifications)
def create_request_for_modifications(sender, instance, created, **kwargs):
    if created:
        Requests.objects.create(
            request_type='modification',
            user=instance.requested_by,
            modifications=instance,
        )


@receiver(post_save, sender=Extensions)
def create_request_for_extensions(sender, instance, created, **kwargs):
    if created:
        Requests.objects.create(
            request_type='extension',
            user=instance.requested_by,
            extensions=instance,
        )

    else:
        request, created = Requests.objects.get_or_create(
            request_type='extension',
            user=instance.requested_by,
            extensions=instance,
        )
        request.save()


@receiver(post_save, sender=RequestReview)
def update_related_models(sender, instance, **kwargs):
    requesting = instance.request

    # Determine the request type from the related Request
    request_type = requesting.request_type
    requesting.reviewed = True
    requesting.save()

    if request_type == 'grant_closeout' and requesting.grant_closeout:
        grant_closeout = requesting.grant_closeout
        grant_closeout.reviewed = True
        grant_closeout.reviewed_by = instance.reviewer
        grant_closeout.status = instance.status
        grant_closeout.save()

        grant_account = grant_closeout.grant_account
        subgrantee = grant_account.account_holder

        subgrantee_profile = SubgranteeProfile.objects.get(user=subgrantee)
        action = f"{instance.status}"
        text = f"Your request to closeout funding opportunity {grant_account.grant.name} has been {action}."

        if subgrantee:
            notification = Notification.objects.create(
                notification_type='grantee',
                notification_category='request_review',
                text=text,
                subgrantee=subgrantee_profile,
                requests=instance,
            )
            notification.user.add(subgrantee)

            html_content = f"""
            <html>
            <body>
            <h2>Grant Closeout Request</h2>
            <p>Dear {html_escape(subgrantee.organisation_name)},</p>
            <p>Your request to closeout funding opportunity {html_escape(grant_account.grant.name)} has been {action}.</p>
            <p>Please review this closeout request and take any necessary actions.</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject="Grant Closeout Request",
                html_content=html_content,
                recipient_list=[subgrantee.email]
            )

    elif request_type == 'requirements' and requesting.requirements:
        requirements = requesting.requirements
        requirements.reviewed = True
        requirements.reviewed_by = instance.reviewer
        requirements.status = instance.status
        requirements.save()

        grant_account = requirements.grant_account
        subgrantee = grant_account.account_holder

        subgrantee_profile = SubgranteeProfile.objects.get(user=subgrantee)
        action = f"{instance.status}"
        text = f"Your request for requirements for funding opportunity {grant_account.grant.name} has been {action}."

        if subgrantee:
            notification = Notification.objects.create(
                notification_type='grantee',
                notification_category='request_review',
                text=text,
                subgrantee=subgrantee_profile,
                requests=instance,
            )
            notification.user.add(subgrantee)

            html_content = f"""
            <html>
            <body>
            <h2>Grant Requirements Review</h2>
            <p>Dear {html_escape(subgrantee.organisation_name)},</p>
            <p>Your request for requirements for funding opportunity {html_escape(grant_account.grant.name)} has been {action}.</p>
            <p>Please review this requirement and take any necessary actions.</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject="Grant Requirements Review",
                html_content=html_content,
                recipient_list=[subgrantee.email]
            )

    elif request_type == 'modifications' and requesting.modifications:
        modifications = requesting.modifications
        modifications.reviewed = True
        modifications.reviewed_by = instance.reviewer
        modifications.status = instance.status
        modifications.save()

        grant_account = modifications.grant_account
        subgrantee = grant_account.account_holder

        subgrantee_profile = SubgranteeProfile.objects.get(user=subgrantee)
        action = f"{instance.status}"
        text = f"Your request for modifications for funding opportunity {grant_account.grant.name} has been {action}."

        if subgrantee:
            notification = Notification.objects.create(
                notification_type='grantee',
                notification_category='request_review',
                text=text,
                subgrantee=subgrantee_profile,
                requests=instance,
            )
            notification.user.add(subgrantee)

            html_content = f"""
            <html>
            <body>
            <h2>Grant Modifications Review</h2>
            <p>Dear {html_escape(subgrantee.organisation_name)},</p>
            <p>Your request for modifications for funding opportunity {html_escape(grant_account.grant.name)} has been {action}.</p>
            <p>Please review this modification request and take any necessary actions.</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject="Grant Modifications Review",
                html_content=html_content,
                recipient_list=[subgrantee.email]
            )

    elif request_type == 'extension' and requesting.extensions:
        extensions = requesting.extensions
        extensions.reviewed = True
        extensions.reviewed_by = instance.reviewer
        extensions.status = instance.status
        extensions.save()

        grant_account = extensions.grant_account
        subgrantee = grant_account.account_holder

        subgrantee_profile = SubgranteeProfile.objects.get(user=subgrantee)
        action = f"{instance.status}"
        text = f"Your request for extensions for funding opportunity {grant_account.grant.name} has been {action}."

        if subgrantee:
            notification = Notification.objects.create(
                notification_type='grantee',
                notification_category='request_review',
                text=text,
                subgrantee=subgrantee_profile,
                request=instance,
            )
            notification.user.add(subgrantee)

            html_content = f"""
            <html>
            <body>
            <h2>Grant Extensions Review</h2>
            <p>Dear {html_escape(subgrantee.organisation_name)},</p>
            <p>Your request for extensions for funding opportunity {html_escape(grant_account.grant.name)} has been {action}.</p>
            <p>Please review this extension request and take any necessary actions.</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject="Grant Extensions Review",
                html_content=html_content,
                recipient_list=[subgrantee.email]
            )


@receiver(post_save, sender=FinancialReport)
def notify_on_new_financial_report(sender, instance, created, **kwargs):
    if created:
        # Get the grant account associated with the financial report
        grant_account = instance.grant_account
        subgrantee = grant_account.account_holder

        # Create a notification for the subgrantee
        text = f"Your financial report {grant_account.grant.name} has been created on {instance.report_date}."
        create_notification(subgrantee, 'grantee', 'financial_report', text)

        html_content = f"""
        <html>
        <body>
        <h2>Financial Report</h2>
        <p>Dear {html.escape(subgrantee.organisation_name)},</p>
        <p>Your financial report for funding opportunity {grant_account.grant.name} has been created on {instance.report_date}.</p>
        <p>Please log in to your account to review the report.</p>
        </body>
        </html>
        """
        send_formatted_email(
            subject=f"Financial Report",
            html_content=html_content,
            recipient_list=[subgrantee.email]
        )


@receiver(post_save, sender=Requirements)
def save_requirements_request(sender, instance, created, **kwargs):
    if created:
        # Create a new request and send notifications/emails
        Requests.objects.create(
            request_type='requirements',
            user=instance.requested_by,
            requirements=instance,
        )

    else:
        # Handle the update case (else block)
        request, created = Requests.objects.get_or_create(
            request_type='requirements',
            user=instance.requested_by,
            requirements=instance,
        )
        request.save()


@receiver(post_save, sender=Requests)
def notify_admin_on_request(sender, instance, created, **kwargs):
    grant_closeout = instance.grant_closeout
    modification = instance.modifications
    requirements = instance.requirements
    extension = instance.extensions

    if instance.request_type == 'grant_closeout':
        if not grant_closeout.initiated_by.is_staff:
            admin_users = CustomUser.objects.filter(is_staff=True)
            for admin in admin_users:
                text = f'A closeout for funding opportunity {grant_closeout.grant_account.grant.name} has been initiated by {grant_closeout.initiated_by.organisation_name}. Reason: {grant_closeout.reason}'
                create_notification(admin, 'admin', 'grant_closeout', text)

                html_content = f"""
                <html>
                <body>
                    <h2>Grant Closeout Notification</h2>
                    <p>A closeout has been initiated for the following grant:</p>
                    <ul>
                        <li><strong>Grant:</strong> {html_escape(grant_closeout.grant_account.grant.name)}</li>
                        <li><strong>Initiated By:</strong> {html_escape(grant_closeout.initiated_by.organisation_name)}</li>
                        <li><strong>Reason:</strong> {html_escape(grant_closeout.reason)}</li>
                    </ul>
                    <p>Please review this closeout request at your earliest convenience.</p>
                </body>
                </html>
                """
                send_formatted_email(
                    subject='Grant Closeout Notification',
                    html_content=html_content,
                    recipient_list=[admin.email]
                )

        elif grant_closeout.initiated_by.is_staff:
            text = f'A closeout for funding opportunity {grant_closeout.grant_account.grant.name} has been initiated. Reason: {grant_closeout.reason}'
            create_notification(
                grant_closeout.grant_account.account_holder, 'grantee', 'requests', text)

            html_content = f"""
            <html>
            <body>
                <h2>Grant Closeout Request</h2>
                <p>Dear {html_escape(grant_closeout.grant_account.account_holder.organisation_name)},</p>
                <p>A closeout has been initiated for the following grant:</p>
                <ul>
                    <li><strong>Grant:</strong> {html_escape(grant_closeout.grant_account.grant.name)}</li>
                    <li><strong>Reason:</strong> {html_escape(grant_closeout.reason)}</li>
                </ul>
                <p>Please review this closeout request and take any necessary actions.</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject='Grant Closeout Request',
                html_content=html_content,
                recipient_list=[
                    grant_closeout.grant_account.account_holder.email]
            )

    elif instance.request_type == 'requirements':
        admins = CustomUser.objects.filter(is_staff=True)
        for admin in admins:
            create_notification(admin, 'admin', 'requests',
                                f"A new requirements request has been created by {requirements.requested_by.organisation_name}.")

        # Build the items HTML table for email
        items_html = """
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
        """
        for item in requirements.items:
            items_html += f"""
                <tr>
                    <td>{html_escape(item.get('name', 'N/A'))}</td>
                    <td>{html_escape(item.get('quantity', 'N/A'))}</td>
                    <td>{html_escape(item.get('description', 'N/A'))}</td>
                </tr>
            """
        items_html += """
            </tbody>
        </table>
        """

        html_content = f"""
        <html>
        <body>
        <h2>Requirements Request</h2>
        <p>A request for requirements:</p>
        <p>Requested by: {html_escape(requirements.requested_by.organisation_name)}</p>
        <p>Items requested:</p>
        {items_html}
        </body>
        </html>
        """

        # Send email to each admin
        for admin in admins:
            send_formatted_email(
                subject='Requirements Request',
                html_content=html_content,
                recipient_list=[admin.email]
            )

    elif instance.request_type == 'modification':
        admins = CustomUser.objects.filter(is_staff=True)
        for admin in admins:
            create_notification(admin, 'admin', 'requests',
                                f"A new modification request has been created by {modification.requested_by.organisation_name}.")
            html_content = f"""
            <html>
            <body>
            <h2>Modification Request</h2>
            <p>A modification request has been created by {html_escape(modification.requested_by.organisation_name)}.</p>
            <p>Please review this request and take any necessary actions.</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject='Modification Request',
                html_content=html_content,
                recipient_list=[admin.email]
            )

    elif instance.request_type == 'extension':
        admins = CustomUser.objects.filter(is_staff=True)
        for admin in admins:
            create_notification(admin, 'admin', 'requests',
                                f"An extension request has been created by {extension.requested_by.organisation_name} .")
            html_content = f"""
            <html>
            <body>
            <h2>Extension Request</h2>
            <p>A extension request has been created by {html_escape(extension.requested_by.organisation_name)}.</p>
            <p>Please review this request and take any necessary actions.</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject='Extension Request',
                html_content=html_content,
                recipient_list=[admin.email]
            )
