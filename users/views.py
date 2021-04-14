from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm

# Create your views here.


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("signup")
    template_name = "signup.html"