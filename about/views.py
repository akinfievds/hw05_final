from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_title'] = 'Об авторе'
        context['author_preview'] = 'Hmm...'
        context['author_main_text'] = 'На создание страницы у меня ушло 5 мин!'
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tech_title'] = 'О технологиях'
        context['tech_preview'] = 'Hmm...'
        context['tech_main_text'] = 'На создание страницы у меня ушло 5 мин!'
        return context
