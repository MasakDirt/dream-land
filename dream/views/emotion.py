from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from dream.models import Emotion


class EmotionCreateView(LoginRequiredMixin, CreateView):
    model = Emotion
    fields = ("name", "description")
    success_url = reverse_lazy("dream:dream-list")
