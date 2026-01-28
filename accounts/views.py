from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import (
    RegistrationSerializer, LoginSerializer, ProfileSerializer, OTPSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from .models import OTPVerification, User
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from django.conf import settings

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if user:
            tokens = get_tokens_for_user(user)
            return Response(tokens)
        return Response({"detail": "Неверный email или пароль"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

class SendOTPView(generics.GenericAPIView):
    serializer_class = OTPSerializer

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email обязателен"}, status=400)
        code = f"{random.randint(1000, 9999)}"
        OTPVerification.objects.create(email=email, code=code)
        send_mail(
            subject="Ваш код подтверждения",
            message=f"Ваш код: {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email]
        )
        return Response({"detail": "Код отправлен на email"})

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not self.object.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Неверный пароль"]}, status=400)
        self.object.set_password(serializer.validated_data['new_password'])
        self.object.save()
        return Response({"detail": "Пароль успешно изменен"})

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = f"{random.randint(1000, 9999)}"
        OTPVerification.objects.create(email=email, code=code)
        send_mail(
            "Сброс пароля",
            f"Ваш код для сброса пароля: {code}",
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        return Response({"detail": "Код отправлен на email"})

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            otp = OTPVerification.objects.filter(email=email, code=code).latest('created_at')
        except OTPVerification.DoesNotExist:
            return Response({"detail": "Неверный код"}, status=400)

        if otp.is_expired():
            return Response({"detail": "Код истек"}, status=400)

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Пароль успешно сброшен"})
