from .serializers import GrantApplicationSerializer
from .models import GrantApplication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
import logging
from django.utils import timezone
from .serializers import GrantApplicationResponsesSerializer, FilteredGrantApplicationResponseSerializer, BudgetCategorySerializer, ModificationsSerializer, RequestReviewSerializer, ExtensionSerializer, FinancialReportSerializer, GrantApplicationReviewDocumentSerializer
from .models import CustomUser, Grant, DefaultApplicationQuestion, GrantApplication, GrantApplicationResponses, Notification, Disbursement, Modifications, RequestReview, Extensions
from rest_framework import permissions, status
from django.db import transaction, IntegrityError
from django.core.mail import send_mail
from .serializers import GrantApplicationResponsesSerializer, GrantSerializer, GrantTypeSerializer, DonorSerializer, DefaultApplicationQuestionSerializer, GrantApplicationSerializer, GrantAccountSerializer, FundingAllocationSerializer, BudgetItemSerializer, ProgressReportSerializer, GrantCloseOutSerializer, GrantCloseOutDocumentsSerializer, RequestsSerializer
from .models import Grant, GrantType, Donor, DefaultApplicationQuestion, GrantApplicationResponses, GrantApplication, GrantApplicationReview, FilteredGrantApplicationResponse, GrantAccount, FundingAllocation, BudgetCategory, BudgetItem, GrantCloseOut, GrantCloseOutDocuments, Requests, Requirements, GrantApplicationReviewDocument
from django.shortcuts import render
from rest_framework import generics, authentication, permissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.utils import timezone
from authentication.models import CustomUser
from .models import Grant, GrantType, Donor, DefaultApplicationQuestion, GrantApplicationResponses, GrantApplication, GrantApplicationDocument, TransformedGrantApplicationData, FinancialReport, ProgressReport
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import GrantApplicationResponsesSerializer, GrantSerializer, GrantTypeSerializer, DonorSerializer, DefaultApplicationQuestionSerializer, GrantApplicationSerializer, GrantApplicationDocumentSerializer, GrantApplicationReviewSerializer, TransformedGrantApplicationDataSerializer, DisbursementSerializer, GrantApplicationReviewSerializer, RequirementsSerializer
from rest_framework.views import APIView
from django.db import transaction
from notifications.models import Notification
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from .tasks import generate_monthly_financial_report
from django.http import JsonResponse
from django.db.models import Sum
from decimal import Decimal


class GrantListCreateAPIView(ListCreateAPIView):
    queryset = Grant.objects.all()
    serializer_class = GrantSerializer


@api_view(["POST"])
def create_grant(request):
    print("Request data:", request.data)
    serializer = GrantSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def grant_list(request):
    grants = Grant.objects.all()
    serializer = GrantSerializer(grants, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_grant(request, pk):
    try:
        grant = Grant.objects.get(pk=pk)
    except Grant.DoesNotExist:
        return Response({"error": "Grant not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GrantSerializer(grant, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GrantDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Grant.objects.all()
    serializer_class = GrantSerializer


class GrantTypeView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                grant_type = GrantType.objects.get(pk=pk, is_active=True)
                serializer = GrantTypeSerializer(grant_type)
                return Response(serializer.data)
            except GrantType.DoesNotExist:
                return Response({"error": "GrantType not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            grant_types = GrantType.objects.filter(is_active=True)
            serializer = GrantTypeSerializer(grant_types, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = GrantTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        if not pk:
            return Response({"error": "PK is required for updates."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grant_type = GrantType.objects.get(pk=pk, is_active=True)
        except GrantType.DoesNotExist:
            return Response({"error": "GrantType not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GrantTypeSerializer(
            grant_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "PK is required for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grant_type = GrantType.objects.get(pk=pk, is_active=True)
        except GrantType.DoesNotExist:
            return Response({"error": "GrantType not found."}, status=status.HTTP_404_NOT_FOUND)

        grant_type.is_active = False
        grant_type.delete()
        return Response({"message": "GrantType successfully deleted."}, status=status.HTTP_200_OK)


class DonorAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        donor_id = kwargs.get('pk')
        if donor_id:
            try:
                donor = Donor.objects.get(pk=donor_id, is_active=True)
                serializer = DonorSerializer(donor)
                return Response(serializer.data)
            except Donor.DoesNotExist:
                return Response({'detail': 'Donor not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            donors = Donor.objects.filter(is_active=True)
            serializer = DonorSerializer(donors, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = DonorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        donor_id = kwargs.get('pk')
        try:
            donor = Donor.objects.get(pk=donor_id, is_active=True)
        except Donor.DoesNotExist:
            return Response({'detail': 'Donor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DonorSerializer(donor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        donor_id = kwargs.get('pk')
        try:
            donor = Donor.objects.get(pk=donor_id, is_active=True)
        except Donor.DoesNotExist:
            return Response({'detail': 'Donor not found'}, status=status.HTTP_404_NOT_FOUND)

        donor.is_active = False
        donor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DefaultApplicationQuestionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        questions = DefaultApplicationQuestion.objects.all()
        serializer = DefaultApplicationQuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_staff:
            serializer = DefaultApplicationQuestionSerializer(
                data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


class GrantPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class GrantListCreateAPIView(ListCreateAPIView):
    queryset = Grant.objects.all()
    serializer_class = GrantSerializer
    pagination_class = GrantPagination


@api_view(["POST"])
def create_grant(request):
    serializer = GrantSerializer(data=request.data)
    if serializer.is_valid():
        grant = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def grant_list(request):
    paginator = GrantPagination()
    grants = Grant.objects.all()
    paginated_grants = paginator.paginate_queryset(grants, request)
    serializer = GrantSerializer(paginated_grants, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def activegrant_count(request):
    count = Grant.objects.filter(is_open=True).count()
    return Response(count, status=status.HTTP_200_OK)


class GrantDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Grant.objects.all()
    serializer_class = GrantSerializer


class GrantTypeListView(generics.ListAPIView):
    queryset = GrantType.objects.filter(is_active=True)
    serializer_class = GrantTypeSerializer


class DonorListView(generics.ListAPIView):
    queryset = Donor.objects.filter(is_active=True)
    serializer_class = DonorSerializer


class DefaultApplicationQuestionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        questions = DefaultApplicationQuestion.objects.all()
        serializer = DefaultApplicationQuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_staff:
            serializer = DefaultApplicationQuestionSerializer(
                data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


logger = logging.getLogger(__name__)


class GrantApplicationResponsesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = CustomUser.objects.get(email=request.user.email)
        answers = request.data.get("answers")
        grant_id = request.data.get("grant_id")

        if not answers:
            return Response({"error": "No answers provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                grant = Grant.objects.get(id=grant_id)
                # Create or update GrantApplication instance
                application, created = GrantApplication.objects.get_or_create(
                    subgrantee=user,
                    grant=grant,
                    defaults={'status': 'under_review',
                    'updated': False
                    }
                )

                for answer in answers:
                    question = DefaultApplicationQuestion.objects.get(
                        id=answer["question_id"])
                    GrantApplicationResponses.objects.update_or_create(
                        grant=grant, question=question, user=user,
                        defaults={
                            'answer': answer["answer"],
                            'choices': answer.get("choice_answers", "")
                        }
                    )

                # Update application status based on completeness
                all_questions = DefaultApplicationQuestion.objects.filter(
                    grant_id=grant_id).values_list('id', flat=True)
                answered_questions = [answer["question_id"]
                                      for answer in answers]

                logger.debug(
                    f"All questions for grant {grant_id}: {all_questions}")
                logger.debug(f"Answered questions: {answered_questions}")

                if set(all_questions) == set(answered_questions):
                    application.status = 'under_review'
                else:
                    application.status = 'under_review'

                application.last_updated = timezone.now()
                application.save()

        except Grant.DoesNotExist:
            logger.error(f"Grant with ID {grant_id} not found")
            return Response({"error": "Grant not found"}, status=status.HTTP_404_NOT_FOUND)
        except DefaultApplicationQuestion.DoesNotExist:
            logger.error("Question not found in the provided answers")
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An unexpected error occurred while processing the request")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        responses = GrantApplicationResponses.objects.filter(
            grant=grant, user=user)
        serializer = GrantApplicationResponsesSerializer(responses, many=True)
        return Response({"message": "Responses saved successfully", "responses": serializer.data, "application_id": application.id}, status=status.HTTP_200_OK)

    def patch(self, request, grant_id=None):
        if not grant_id:
            return Response({"error": "Grant ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.get(email=request.user.email)
        answers = request.data.get("answers")

        if not answers:
            return Response({"error": "No answers provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                grant = Grant.objects.get(id=grant_id)
                application, created = GrantApplication.objects.get_or_create(
                    subgrantee=user,
                    grant=grant,
                    defaults={
                        'status': 'under_review'
                        
                    }
                )

                for answer in answers:
                    question = DefaultApplicationQuestion.objects.get(
                        id=answer["question_id"])
                    GrantApplicationResponses.objects.update_or_create(
                        grant=grant, question=question, user=user,
                        defaults={
                            'answer': answer["answer"],
                            'choices': answer.get("choice_answers", "")
                        }
                    )
                all_questions = DefaultApplicationQuestion.objects.filter(
                    grant_id=grant_id).values_list('id', flat=True)
                answered_questions = [answer["question_id"]
                                      for answer in answers]

                logger.debug(
                    f"All questions for grant {grant_id}: {all_questions}")
                logger.debug(f"Answered questions: {answered_questions}")

                if set(all_questions) == set(answered_questions):
                    application.status = 'under_review'
                else:
                    application.status = 'under_review'

                application.last_updated = timezone.now()
                application.updated = True
                application.save()

        except Grant.DoesNotExist:
            logger.error(f"Grant with ID {grant_id} not found")
            return Response({"error": "Grant not found"}, status=status.HTTP_404_NOT_FOUND)
        except DefaultApplicationQuestion.DoesNotExist:
            logger.error("Question not found in the provided answers")
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An unexpected error occurred while processing the request")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        responses = GrantApplicationResponses.objects.filter(
            grant=grant, user=user)
        serializer = GrantApplicationResponsesSerializer(responses, many=True)
        return Response({"message": "Responses updated successfully", "responses": serializer.data, "application_id": application.id}, status=status.HTTP_200_OK)

    def get(self, request, grant_id=None):
        user = CustomUser.objects.get(email=request.user.email)
        if grant_id:
            grant = Grant.objects.get(id=grant_id)
            if user.is_staff:
                responses = GrantApplicationResponses.objects.filter(
                    grant=grant)
            else:
                responses = GrantApplicationResponses.objects.filter(
                    grant=grant, user=user)
        else:
            if user.is_staff:
                responses = GrantApplicationResponses.objects.all()
            else:
                responses = GrantApplicationResponses.objects.filter(user=user)
        serializer = GrantApplicationResponsesSerializer(responses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_all_applications(request):
        grant_applications = GrantApplication.objects.all()
        serializer = GrantApplicationSerializer(grant_applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GrantApplicationListCreateView(APIView):

    def get(self, request, user_id, *args, **kwargs):
        try:
            # Fetch applications for the given user
            grant_applications = GrantApplication.objects.filter(
                subgrantee_id=user_id)
            serializer = GrantApplicationSerializer(
                grant_applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GrantApplication.DoesNotExist:
            return Response({"detail": "User has no applications"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        serializer = GrantApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GrantApplicationCountView(APIView):
    def get(self, request, *args, **kwargs):
        count = GrantApplication.objects.count()
        return Response({'count': count}, status=status.HTTP_200_OK)


class GrantApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):

        try:
            grant_application = GrantApplication.objects.get(pk=pk)
            serializer = GrantApplicationSerializer(grant_application)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GrantApplication.DoesNotExist:
            return Response({'detail': 'GrantApplication not found.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, *args, **kwargs):
        try:
            grant_application = GrantApplication.objects.get(pk=pk)
            serializer = GrantApplicationSerializer(
                grant_application, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except GrantApplication.DoesNotExist:
            return Response({'detail': 'GrantApplication not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, *args, **kwargs):
        try:
            grant_application = GrantApplication.objects.get(pk=pk)
            grant_application.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except GrantApplication.DoesNotExist:
            return Response({'detail': 'GrantApplication not found.'}, status=status.HTTP_404_NOT_FOUND)




class GrantApplicationReviewDocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_user(self, request):
        try:
            return CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return None

    def post(self, request, review_id=None):
        if not review_id:
            return Response({"error": "Review ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            review = GrantApplicationReview.objects.get(id=review_id)
        except GrantApplicationReview.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('uploads')
        if not files:
            return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        uploads = []
        for file in files:
            upload = GrantApplicationReviewDocument.objects.create(
                review=review,
                uploads=file
            )
            uploads.append(upload)

        # Create serializer after processing all files
        serializer = GrantApplicationReviewDocumentSerializer(
            uploads, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, review_id=None):
        if not review_id:
            return Response({"error": "Review ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            review = GrantApplicationReview.objects.get(id=review_id)
        except GrantApplicationReview.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        uploads = GrantApplicationReviewDocument.objects.filter(review=review)
        serializer = GrantApplicationReviewDocumentSerializer(
            uploads, many=True)
        return Response({"uploads": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_review_for_application(request, application_id):
    try:
        review = GrantApplicationReview.objects.get(application=application_id)
        serializer = GrantApplicationReviewSerializer(review)
        return Response(serializer.data)
    except GrantApplicationReview.DoesNotExist:
        return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

class GrantApplicationDocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_user(self, request):
        try:
            return CustomUser.objects.get(email=request.user.email)
        except CustomUser.DoesNotExist:
            return None

    def post(self, request, application_id=None):
        if not application_id:
            return Response({"error": "Application ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            application = GrantApplication.objects.get(id=application_id)
        except GrantApplication.DoesNotExist:
            return Response({"error": "GrantApplication does not exist"}, status=status.HTTP_404_NOT_FOUND)

        user = self.get_user(request)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('documents')
        if not files:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

        documents = []
        for file in files:
            document = GrantApplicationDocument.objects.create(
                application=application,
                user=user,
                documents=file
            )
            documents.append(document)

        serializer = GrantApplicationDocumentSerializer(documents, many=True)
        return Response({"documents": serializer.data}, status=status.HTTP_201_CREATED)

    def patch(self, request, application_id=None):
        return Response({"error": "PATCH method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GrantApplicationDocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, application_id=None):
        if not application_id:
            return Response({"error": "Application ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            application = GrantApplication.objects.get(id=application_id)
        except GrantApplication.DoesNotExist:
            return Response({"error": "GrantApplication does not exist"}, status=status.HTTP_404_NOT_FOUND)

        documents = GrantApplicationDocument.objects.filter(
            application=application)
        serializer = GrantApplicationDocumentSerializer(documents, many=True)
        return Response({"documents": serializer.data}, status=status.HTTP_200_OK)


class GrantApplicationReviewListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GrantApplicationReviewSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            review = serializer.save()
            # Update the application status and set reviewed to True
            application = review.application
            application.status = review.status  # Set application status to review status
            # Assuming you have a 'reviewed' field in GrantApplication
            application.reviewed = True
            application.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            review = GrantApplicationReview.objects.select_related(
                'application').get(pk=pk)
        except GrantApplicationReview.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to update this review
        if review.reviewer != request.user and not request.user.is_staff:
            return Response({'error': "You don't have permission to update this review."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = GrantApplicationReviewSerializer(
            review, data=request.data, partial=True)
        if serializer.is_valid():
            updated_review = serializer.save()

            # Update the application status and set reviewed to True for all cases
            application = updated_review.application
            application.status = updated_review.status
            application.reviewed = True
            application.save(update_fields=['status', 'reviewed'])

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        grant_id = request.query_params.get('grant')
        if grant_id:
            try:
                reviews = GrantApplicationReview.objects.filter(
                    application_id=grant_id)
            except ValueError:
                return Response({'error': 'Invalid grant ID'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            reviews = GrantApplicationReview.objects.all()
        serializer = GrantApplicationReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class GrantApplicationReviewDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, application_id):
        try:
            # Retrieve reviews for the given application ID
            reviews = GrantApplicationReview.objects.filter(
                application__id=application_id)

            if not reviews.exists():
                return Response({'error': 'No reviews found for this application'}, status=status.HTTP_404_NOT_FOUND)

            serializer = GrantApplicationReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except GrantApplication.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)


class GrantApplicationApproveCountView(APIView):
    def get(self, request):
        approved_count = GrantApplicationReview.objects.filter(
            status='approved').count()
        return Response({'count': approved_count}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_pending_approval_applications_count(request):
    count = GrantApplicationReview.objects.filter(status='negotiate').count()
    return Response({'count': count}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_rejected_applications_count(request):
    count = GrantApplicationReview.objects.filter(status='rejected').count()
    return Response({'count': count}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_transformed_data(request):
    user_id = request.query_params.get('user_id')
    grant_id = request.query_params.get('grant_id')

    if not user_id or not grant_id:
        return Response({"error": "Both user_id and grant_id are required"}, status=status.HTTP_400_BAD_REQUEST)

    transformed_data = TransformedGrantApplicationData.objects.filter(
        user_id=user_id, grant_id=grant_id)

    if transformed_data.exists():
        serializer = TransformedGrantApplicationDataSerializer(
            transformed_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "No transformed data found for the given user_id and grant_id"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def filtered_responses_view(request):
    application_id = request.query_params.get('application_id')
    user_id = request.query_params.get('user_id')

    if not application_id or not user_id:
        return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

    responses = FilteredGrantApplicationResponse.objects.filter(
        application_id=application_id,
        user_id=user_id
    ).select_related('application__grant')  # Ensure related data is fetched

    serializer = FilteredGrantApplicationResponseSerializer(
        responses, many=True)
    return Response(serializer.data)


class UserApplicationDocumentsView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        application_id = request.query_params.get('application_id')

        if not user_id or not application_id:
            return Response(
                {'error': 'Both user_id and application_id are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the document instance, if it exists
        try:
            document_instance = GrantApplicationDocument.objects.get(
                user_id=user_id, application_id=application_id
            )
        except GrantApplicationDocument.DoesNotExist:
            return Response(
                {'error': 'No documents found for the given user and application.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the document instance
        serializer = GrantApplicationDocumentSerializer(document_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GrantAccountReportView(APIView):
    def get(self, request, account_id):
        try:
            grant_account = GrantAccount.objects.get(pk=account_id)
            report = grant_account.generate_fiscal_year_report()
            return Response(report, status=status.HTTP_200_OK)
        except GrantAccount.DoesNotExist:
            return Response({'detail': 'GrantAccount not found.'}, status=status.HTTP_404_NOT_FOUND)


class GrantAccountDetailView(APIView):
    def get(self, request, user_id):
        # Get all GrantAccount records for the given user_id
        grant_accounts = GrantAccount.objects.filter(account_holder_id=user_id, status='active')

        if not grant_accounts.exists():
            return Response(
                {'detail': 'GrantAccount not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the queryset
        serializer = GrantAccountSerializer(grant_accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BudgetItemListView(APIView):
    def get(self, request, user_id, category_id):
        if not request.user.is_staff and request.user.id != user_id:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        budget_items = BudgetItem.objects.filter(
            user_id=user_id, category_id=category_id)
        serializer = BudgetItemSerializer(budget_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id, category_id):
        data = request.data
        data['user'] = user_id
        data['category'] = category_id
        logger.debug(f"Received data: {data}")

        serializer = BudgetItemSerializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                logger.debug(
                    f"BudgetItem created successfully: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error during save: {str(e)}")
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.error(f"Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BudgetItemDetailView(APIView):
    def get(self, request, user_id, category_id, pk):
        try:
            budget_item = BudgetItem.objects.get(
                pk=pk, user_id=user_id, category_id=category_id)
            serializer = BudgetItemSerializer(budget_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BudgetItem.DoesNotExist:
            return Response({'detail': 'BudgetItem not found or you do not have permission to view it.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, user_id, category_id, pk):
        try:
            budget_item = BudgetItem.objects.get(
                pk=pk, user_id=user_id, category_id=category_id)
            serializer = BudgetItemSerializer(
                budget_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BudgetItem.DoesNotExist:
            return Response({'detail': 'BudgetItem not found or you do not have permission to edit it.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id, category_id, pk):
        try:
            budget_item = BudgetItem.objects.get(
                pk=pk, user_id=user_id, category_id=category_id)
            budget_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BudgetItem.DoesNotExist:
            return Response({'detail': 'BudgetItem not found or you do not have permission to delete it.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_all_budget_items(request, user_id):
    budget_items = BudgetItem.objects.filter(user_id=user_id)
    serializer = BudgetItemSerializer(budget_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

class FundingAllocationListView(APIView):
    def get(self, request, user_id):
        if request.user.id != user_id and not request.user.is_staff:
            return Response({'detail': 'You do not have permission to view these allocations.'}, status=status.HTTP_403_FORBIDDEN)

        allocations = FundingAllocation.objects.filter(user_id=user_id)
        serializer = FundingAllocationSerializer(allocations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        if request.user.id != user_id and not request.user.is_staff:
            return Response({'detail': 'You do not have permission to create allocations for this user.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        data['user'] = user_id
        serializer = FundingAllocationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundingAllocationDetailView(APIView):
    def get(self, request, user_id, pk):
        try:
            allocation = FundingAllocation.objects.get(pk=pk, user_id=user_id)
            if request.user.id != allocation.user.id and not request.user.is_staff:
                return Response({'detail': 'You do not have permission to view this allocation.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = FundingAllocationSerializer(allocation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FundingAllocation.DoesNotExist:
            return Response({'detail': 'FundingAllocation not found.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, user_id, pk):
        try:
            allocation = FundingAllocation.objects.get(pk=pk, user_id=user_id)
            if request.user.id != allocation.user.id and not request.user.is_staff:
                return Response({'detail': 'You do not have permission to edit this allocation.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = FundingAllocationSerializer(
                allocation, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except FundingAllocation.DoesNotExist:
            return Response({'detail': 'FundingAllocation not found.'}, status=status.HTTP_404_NOT_FOUND)


class BudgetCategoryListView(APIView):

    def get(self, request, user_id):
        try:
            # Filter BudgetCategories by user_id
            categories = BudgetCategory.objects.filter(user_id=user_id)
            serializer = BudgetCategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BudgetCategory.DoesNotExist:
            return Response({'detail': 'BudgetCategories not found.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id):
        data = request.data
        data['user'] = user_id  # Use the user_id from the URL
        serializer = BudgetCategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, category_id):
        try:
            category = BudgetCategory.objects.get(
                id=category_id, user_id=user_id)
            category.delete()
            return Response({'detail': 'Category deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except BudgetCategory.DoesNotExist:
            return Response({'detail': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)


class BudgetCategoryDetailView(APIView):
    def get(self, request, pk, user_id):
        try:
            category = BudgetCategory.objects.get(pk=pk, user_id=user_id)
            serializer = BudgetCategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BudgetCategory.DoesNotExist:
            return Response({'detail': 'BudgetCategory not found or you do not have permission to view it.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, user_id):
        try:
            category = BudgetCategory.objects.get(pk=pk, user_id=user_id)
            serializer = BudgetCategorySerializer(
                category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BudgetCategory.DoesNotExist:
            return Response({'detail': 'BudgetCategory not found or you do not have permission to edit it.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, user_id):
        try:
            category = BudgetCategory.objects.get(pk=pk, user_id=user_id)
            category.delete()
            return Response({'detail': 'BudgetCategory deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except BudgetCategory.DoesNotExist:
            return Response({'detail': 'BudgetCategory not found or you do not have permission to delete it.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_report(request, grant_account_id, report_date):
    grant_account = get_object_or_404(GrantAccount, id=grant_account_id)
    try:
        report = FinancialReport.objects.get(
            grant_account=grant_account, report_date=report_date)
        return JsonResponse(report.report_data)
    except FinancialReport.DoesNotExist:
        return JsonResponse({'error': 'Report not found'}, status=404)


@api_view(['POST'])
def generate_report(request, grant_account_id):
    logger.info(
        f"Received generate_report request with grant_account_id={grant_account_id}")

    grant_account = get_object_or_404(GrantAccount, id=grant_account_id)
    date = request.data.get('date')

    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        logger.info(
            f"Calling generate_monthly_financial_report for account {grant_account_id} and date {date}")
    else:
        logger.info("No date provided, using default")

    # Run synchronously for debugging
    result = generate_monthly_financial_report(grant_account.id, date)
    logger.info(f"Task result: {result}")

    return JsonResponse({'message': 'Report generation completed.'})


@api_view(['GET'])
def get_most_recent_report(request, grant_account_id):
    # Fetch the GrantAccount instance
    grant_account = get_object_or_404(GrantAccount, id=grant_account_id)

    # Fetch the most recent FinancialReport for the specified GrantAccount
    report = FinancialReport.objects.filter(
        grant_account=grant_account).order_by('-report_date').first()

    if report:
        # Return the report data if a report exists
        return JsonResponse(report.report_data)
    else:
        # If no report exists, return an error response
        return JsonResponse({'error': 'No reports found for this account'}, status=404)

@api_view(['GET'])
def list_reports(request, grant_account_id):
    grant_account = get_object_or_404(GrantAccount, id=grant_account_id)
    reports = FinancialReport.objects.filter(
        grant_account=grant_account).values('id', 'report_date', 'fiscal_year')
    return JsonResponse(list(reports), safe=False)


class ProgressReportView(APIView):
    def get(self, request, grant_account_id):
        try:
            grant_account = GrantAccount.objects.get(pk=grant_account_id)
            latest_report = ProgressReport.objects.filter(
                grant_account=grant_account).order_by('-report_date').first()

            if latest_report:
                serializer = ProgressReportSerializer(latest_report)
                return Response(serializer.data)
            else:
                return Response({})
        except GrantAccount.DoesNotExist:
            return Response({"error": "Grant account not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, grant_account_id):
        try:
            grant_account = GrantAccount.objects.get(id=grant_account_id)
        except GrantAccount.DoesNotExist:
            return Response({"detail": "GrantAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()
        existing_report = ProgressReport.objects.filter(
            grant_account=grant_account, report_date=today).first()

        data = request.data.copy()
        data['grant_account'] = grant_account_id

        if existing_report:
            serializer = ProgressReportSerializer(
                existing_report, data=data, partial=True)

        else:
            serializer = ProgressReportSerializer(data=data)

        if serializer.is_valid():
            progress_report = ProgressReport(
                grant_account=grant_account,
                completed_pkis=serializer.validated_data['completed_pkis'],
                progress_percentage=serializer.validated_data.get(
                    'progress_percentage', 0),
                status=serializer.validated_data.get('status', 'pending'),
                review_comments=serializer.validated_data.get(
                    'review_comments', ''),
                reviewer=serializer.validated_data.get('reviewer', None)
            )
            progress_report.save()

            return Response(ProgressReportSerializer(progress_report).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_most_recent_progress_report(request, grant_account_id):
    # Fetch the GrantAccount instance
    grant_account = get_object_or_404(GrantAccount, id=grant_account_id)

    # Fetch the most recent ProgressReport for the specified GrantAccount
    report = ProgressReport.objects.filter(
        grant_account=grant_account).order_by('-report_date').first()

    if report:
        # Serialize the report data
        report_data = {
            'report_date': report.report_date,
            'completed_pkis': report.completed_pkis,
            'status': report.status,
            'progress_percentage': report.progress_percentage,
            'review_status': report.review_status,
            'review_comments': report.review_comments,
            'reviewer': report.reviewer.email if report.reviewer else None,
            'last_updated': report.last_updated,
        }
        return JsonResponse(report_data)
    else:
        # If no report exists, return an error response
        return JsonResponse({'error': 'No progress reports found for this account'}, status=404)

class AllProgressReportsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        reports = ProgressReport.objects.all()
        serializer = ProgressReportSerializer(reports, many=True)
        return Response(serializer.data)

class AllFinanceReportsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        reports = FinancialReport.objects.all()
        serializer = FinancialReportSerializer(reports, many=True)
        return Response(serializer.data) 


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def review_progress_report(request, report_id):
    try:
        report = ProgressReport.objects.get(pk=report_id)
        report.review_status = 'reviewed'
        report.review_comments = request.data.get('review_comments', '')
        report.reviewer = request.user
        report.save(update_fields=['review_status',
                    'review_comments', 'reviewer'])
        return Response({
            'message': 'Report reviewed successfully',
            'review_status': report.review_status,
            'reviewer': report.reviewer.email if report.reviewer else None
        }, status=status.HTTP_200_OK)
    except ProgressReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def review_financial_report(request, report_id):
    try:
        report = FinancialReport.objects.get(pk=report_id)
        report.review_status = 'reviewed'
        report.review_comments = request.data.get('review_comments', '')
        report.reviewer = request.user
        report.save(update_fields=['review_status',
                    'review_comments', 'reviewer'])
        return Response({
            'message': 'Report reviewed successfully',
            'review_status': report.review_status,
            'reviewer': report.reviewer.email if report.reviewer else None
        }, status=status.HTTP_200_OK)
    except FinancialReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

class DisbursementView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DisbursementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def get_all_accounts(request):
    accounts = GrantAccount.objects.all()
    serializer = GrantAccountSerializer(accounts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_disbursements(request):
    disbursements = Disbursement.objects.all()
    serializer = DisbursementSerializer(disbursements, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def get_disbursements_by_account(request, account_id):
    try:
        disbursements = Disbursement.objects.filter(
            grant_account_id=account_id)
        serializer = DisbursementSerializer(disbursements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Disbursement.DoesNotExist:
        return Response({"error": "Disbursements not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PATCH"])
@permission_classes([permissions.IsAdminUser])
def update_disbursement(request, pk):
    try:
        disbursement = Disbursement.objects.get(pk=pk)
    except Disbursement.DoesNotExist:
        return Response({"error": "Disbursement not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DisbursementSerializer(
        disbursement, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def create_disbursement(request, account_id):
    try:
        account = GrantAccount.objects.get(pk=account_id)
    except GrantAccount.DoesNotExist:
        return Response({"error": "Grant account not found"}, status=status.HTTP_404_NOT_FOUND)

    disbursement_amount = request.data.get("disbursement_amount")
    if disbursement_amount is None:
        return Response({"error": "Disbursement amount is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        disbursement_amount = float(disbursement_amount)
    except ValueError:
        return Response({"error": "Invalid disbursement amount"}, status=status.HTTP_400_BAD_REQUEST)
    disbursement = Disbursement(
        grant_account=account,
        disbursement_amount=disbursement_amount
    )
    disbursement.save()
    serializer = DisbursementSerializer(disbursement)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class GrantCloseoutView(APIView):
    permission_classes = [IsAuthenticated]

    # def post(self, request, grant_account_id):
    #     try:
    #         grant_account = GrantAccount.objects.get(id=grant_account_id)
    #     except GrantAccount.DoesNotExist:
    #         return Response({"error": "Grant account not found"}, status=status.HTTP_404_NOT_FOUND)

    #     if grant_account.status != 'active':
    #         return Response({"error": "Only active accounts can be closed out"}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         closeout = GrantCloseOut.objects.get(grant_account=grant_account)
    #         # Update existing closeout
    #         serializer = GrantCloseOutSerializer(
    #             closeout, data=request.data, partial=True)
    #     except GrantCloseOut.DoesNotExist:
    #         # Create a new closeout record
    #         serializer = GrantCloseOutSerializer(data=request.data)

    #     if serializer.is_valid():
    #         closeout = serializer.save(
    #             grant_account=grant_account, initiated_by=request.user)
    #         grant_account.status = 'pending_closeout'
    #         grant_account.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, grant_account_id):
        try:
            grant_account = GrantAccount.objects.get(id=grant_account_id)
        except GrantAccount.DoesNotExist:
            return Response({"error": "Grant account not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            closeout = GrantCloseOut.objects.get(grant_account=grant_account)
        except GrantCloseOut.DoesNotExist:
            return Response({"error": "No closeout record found for this grant account"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GrantCloseOutSerializer(closeout)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, grant_account_id):
        try:
            grant_account = GrantAccount.objects.get(id=grant_account_id)
        except GrantAccount.DoesNotExist:
            return Response({"error": "Grant account not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            closeout = GrantCloseOut.objects.get(grant_account=grant_account)
        except GrantCloseOut.DoesNotExist:
            return Response({"error": "No closeout record found for this grant account"}, status=status.HTTP_404_NOT_FOUND)

        if grant_account.status != 'pending_closeout':
            return Response({"error": "Only pending closeout accounts can be updated"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GrantCloseOutSerializer(
            closeout, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_all_grantcloseout_requests(request):
    closeout_requests = GrantCloseOut.objects.all()
    serializer = GrantCloseOutSerializer(closeout_requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_grant_application_details(request, application_id):
    try:
        grant_application = GrantApplication.objects.get(id=application_id)
        serializer = GrantApplicationSerializer(grant_application)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except GrantApplication.DoesNotExist:
        return Response({"error": "GrantApplication not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_closeout_request_details(request, closeout_id):
    try:
        closeout_request = GrantCloseOut.objects.get(id=closeout_id)
        serializer = GrantCloseOutSerializer(closeout_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except GrantCloseOut.DoesNotExist:
        return Response({"error": "GrantCloseOut not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_or_update_closeout_request(request):
    serializer = GrantCloseOutSerializer(
        data=request.data, context={'request': request})
    if serializer.is_valid():
        
            instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RequestsListCreateAPIView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        requests = Requests.objects.filter(user=user)

        serializer = RequestsSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_all_requests(request):
    requests = Requests.objects.all()
    serializer = RequestsSerializer(requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class ModificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ModificationsSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                instance = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(
                    f"Error saving modification: {str(e)}", exc_info=True)
                return Response({'error': f'Internal Server Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GrantCloseOutReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, closeout_id):
        reviews = GrantCloseOutReview.objects.filter(closeout_id=closeout_id)
        serializer = GrantCloseOutReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, closeout_id):
        data = request.data
        data['closeout'] = closeout_id
        data['reviewer'] = request.user.id

        serializer = GrantCloseOutReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def signed_applications_percentage(request):
    percentage = GrantApplication.get_compliance_percentange()
    return Response({'signed_percentage': percentage})

def total_disbursements(request):
    total_disbursements = Disbursement.objects.aggregate(total_amount=Sum('disbursement_amount'))['total_amount'] or Decimal('0')
    return JsonResponse({'total_disbursements': total_disbursements})


class RequirementsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Correct filter to match `requested_by` field
        requirements = Requirements.objects.filter(requested_by=request.user)
        serializer = RequirementsSerializer(requirements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RequirementsSerializer(data=request.data)
        if serializer.is_valid():
            # Set the requested_by field to the current user
            serializer.save(requested_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RequirementsDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            # Correct filter to match `requested_by` field
            return Requirements.objects.get(pk=pk, requested_by=self.request.user)
        except Requirements.DoesNotExist:
            return None

    def get(self, request, pk):
        requirement = self.get_object(pk)
        if requirement is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RequirementsSerializer(requirement)
        return Response(serializer.data)

    def put(self, request, pk):
        requirement = self.get_object(pk)
        if requirement is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RequirementsSerializer(requirement, data=request.data)
        if serializer.is_valid():
            # No need to set `requested_by` again since it's unchanged
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        requirement = self.get_object(pk)
        if requirement is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        requirement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RequestReview.objects.all()
    serializer_class = RequestReviewSerializer


class RequestReviewCreateView(generics.CreateAPIView):
    queryset = RequestReview.objects.all()
    serializer_class = RequestReviewSerializer

class ExtensionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Extensions.objects.all()
    serializer_class = ExtensionSerializer

class ExtensionCreateView(generics.CreateAPIView):
    queryset = Extensions.objects.all()
    serializer_class = ExtensionSerializer