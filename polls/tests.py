import datetime

from django.urls import reverse
from django.utils import timezone
from django.test import TestCase

from .models import Choice, Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose
        pub_date is in the future.
        """

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose
        pub_date is older than 1 day.
        """

        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recentl_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose
        pub_data is within the last day.
        """

        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days, has_choice=False):
    """
    Create a question with the given `question_text` and published
    the given number of `days` offset from now (negetive for questions published
    in the past, positive for questions that have yet to be published).
    """

    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)

    if has_choice:
        Choice.objects.create(question=question, choice_text="Choice")

    return question


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exists, an appropriate message is displayed.
        """

        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question_with_choice(self):
        """
        Questions with pub_date in the past and with choice are displayed on the index page.
        """

        question = create_question(
            question_text="Past question.", days=-30, has_choice=True
        )
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_past_question_with_and_without_choice(self):
        """
        Past question without choice are not displayed on the index page.
        Only question with choice are displayed on the index page.
        """

        question1 = create_question(
            question_text="Past question 1.", days=-5, has_choice=True
        )
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question1])

    def test_future_question_with_choice(self):
        """
        Questions with pub_date in the future aren't displayed on the index page
        even if they have choice.
        """

        create_question(question_text="Future question 1.", days=30)
        create_question(question_text="Future question 2.", days=30, has_choice=True)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question_with_choice(self):
        """
        Even if both past and future questions exist, only past questions
        with choices are displayed.
        """

        question = create_question(
            question_text="Past question.", days=-30, has_choice=True
        )
        create_question(question_text="Future question.", days=30, has_choice=True)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_two_past_questions_with_choice(self):
        """
        The questions index page may display multiple questions if they have choices.
        """

        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(
            question_text="Past question 1.", days=-30, has_choice=True
        )
        question3 = create_question(
            question_text="Past question 2.", days=-5, has_choice=True
        )
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question3, question2]
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question_with_choice(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """

        future_question = create_question(
            question_text="Future question.", days=5, has_choice=True
        )
        url = reverse(
            "polls:detail", args=(future_question.id,)
        )  # notice the trailing comma in the tuple
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_with_choice(self):
        """
        The detail view of a past question with a choice
        displays the question's text and choice.
        """

        past_question = create_question(
            question_text="Past question.", days=-5, has_choice=True
        )
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        self.assertContains(response, past_question.choice_set.first().choice_text)

    def test_past_question_without_choice(self):
        """
        The detail view of a past question without a choice
        returns a 404 not found.
        """

        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionResultsViewTests(TestCase):
    def test_future_question_with_choice(self):
        """
        The results view of a future question even with a choice
        returns a 404 not found.
        """

        future_question = create_question(
            question_text="Future question.", days=5, has_choice=True
        )
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_with_choice(self):
        """
        The results view of a past question with a choice
        displays the question's text and choices.
        """

        past_question = create_question(
            question_text="Past question.", days=-5, has_choice=True
        )
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)
        for choice in past_question.choice_set.all():
            self.assertContains(response, choice.choice_text)
            self.assertContains(response, str(choice.votes))

    def test_past_question_without_choice(self):
        """
        The results view of a past question without a choice
        returns a 404 not found.
        """

        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
