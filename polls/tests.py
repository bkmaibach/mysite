from django.test import TestCase
from django.utils import timezone
import datetime
from polls.models import Question
from django.urls import reverse

def create_question(question_text, days):
    '''Create and return a question with given text and day offset from today'''
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(pub_date=time, question_text=question_text)

class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        '''If no questions exist, test that an appropriate message is displayed'''
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        print(response)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        '''Questions with a pub_date in the past are displayed on the index page'''
        create_question(question_text='Past question.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )
    
    def test_future_question(self):
        '''Questions with pub_date in the future should not show up in the query'''
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        '''Only past questions are displayed even if both past and future exist'''
        create_question(question_text='Future question.', days=30)
        create_question(question_text='Past question.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )
    
    def test_multiple_quesitons(self):
        '''Test that two past questions are returned appropriately'''
        create_question(question_text='Past question 1.', days=-30)
        create_question(question_text='Past question 2.', days=-10)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        '''was_published_recently() should return false for Questions whose pub_date is in the future'''
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        '''Test that was_published_recently() returns false for an old question'''
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        '''Test that was_published_recently() returns True for a recent question'''
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        '''The detail view should return a 404 if quesiton is in the future'''
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = create_question(question_text='future', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        '''The detail view of a question published in the past displays the question text'''
        past_question = create_question(question_text='future', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


        



