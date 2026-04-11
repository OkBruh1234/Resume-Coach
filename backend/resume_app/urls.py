from django.urls import path
from .views import AnalyzeResumeView, ChatbotView

urlpatterns = [
    path('analyze/', AnalyzeResumeView.as_view(), name='analyze_resume'),
    path('chat/', ChatbotView.as_view(), name='chatbot'),
]
