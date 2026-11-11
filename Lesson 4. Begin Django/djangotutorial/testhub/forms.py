from django import forms


class TestStartForm(forms.Form):
    """Дані того, хто проходить тест (ПІБ)."""
    last_name = forms.CharField(
        label="Прізвище",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label="Ім'я",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    middle_name = forms.CharField(
        label="По батькові",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class TestTakeForm(forms.Form):
    """Динамічна форма: одне поле з радіокнопками на кожне питання тесту."""

    def __init__(self, *args, questions, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = list(questions)
        for question in self.questions:
            # Відповідь не обов'язкова: при завершенні часу форма
            # відправляється автоматично, навіть якщо не все заповнено
            self.fields[self.field_name(question)] = forms.ChoiceField(
                label=question.text,
                help_text=f"Балів: {question.points}",
                required=False,
                choices=[(str(o.id), o.text) for o in question.options.all()],
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
            )

    @staticmethod
    def field_name(question):
        return f"question_{question.id}"

    def selected_options(self):
        """Повертає словник {питання: обраний AnswerOption або None}."""
        result = {}
        for question in self.questions:
            option_id = self.cleaned_data.get(self.field_name(question))
            option = None
            if option_id:
                # ChoiceField уже перевірив, що id належить цьому питанню
                option = next(o for o in question.options.all() if str(o.id) == option_id)
            result[question] = option
        return result
