from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from dream.models import Symbol


class SymbolCreateView(LoginRequiredMixin, CreateView):
    model = Symbol
    fields = "__all__"
    success_url = reverse_lazy("dream:dream-list")
