from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'core/landing.html'
    
    def get(self, request, *args, **kwargs):
        # Если пользователь залогинен, перенаправляем его на My Books
        if request.user.is_authenticated:
            return redirect('books:my_books')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Данные для тарифов
        plans = [
            {
                'name': 'Monthly Plan',
                'price': '$19.99',
                'period': 'per month',
                'features': [
                    'Unlimited books',
                    'Unlimited reviews for all books',
                    'No charge per review',
                    '2000 stars signup bonus',
                    'Cancel anytime',
                    '30-day money back guarantee',
                    'Free for 7 days'
                ],
                'is_popular': False
            },
            {
                'name': 'Yearly Plan',
                'price': '$150',
                'period': 'per year',
                'original_price': '$240',
                'features': [
                    'Unlimited books',
                    'Unlimited reviews for all books',
                    'No charge per review',
                    '2000 stars signup bonus',
                    'Cancel anytime',
                    '30-day money back guarantee',
                    'Free for 7 days'
                ],
                'is_popular': True,
                'save_text': 'Save $90'
            }
        ]
        
        # Данные для FAQ
        faqs = [
            {
                'question': 'Is BOOKSTARS a reliable way to get reviews?',
                'answer': 'Yes! BOOKSTARS is a reliable and fun way to generate reviews for your books. Our rules are carefully designed to ensure every user follows Amazon’s Review Guidelines, which state that all reviews should be authentic, respectful, and honest, and that no review should be influenced in any way by the product’s owner (or author). BOOKSTARS keeps true to these principles and our methodology ensures the reviews our users post are legitimate and authentic.'
            },
            {
                'question': 'I am not from the US. Does that matter?',
                'answer': 'Nope, not at all. BOOKSTARS welcomes customers from all over the world, no matter where you are. We do, however, only accept reviews on the following Amazon marketplaces: United States (.com), Canada (.ca), Mexico (.com.mx), United Kingdom (.co.uk), Germany (.de), France (.fr), Italy (.it), Spain (.es), Japan (.jp), Australia (.com.au), and Netherlands (.nl). If you live in a country without an Amazon marketplace or your marketplace is not listed, then you will need to set up an Amazon account in another country and meet their minimum criteria to submit reviews.'
            },
            {
                'question': 'What is a \'review swap\' and why is it a bad idea?',
                'answer': 'A review swap is when two (or more) authors agree to leave reviews of each other\'s books. It sounds like a good idea in theory, however due to the lack of scrutiny and honesty in these reviews, Amazon have clamped down on this and will remove any reviews they believe to have been left from a review swap. Our web developers have created a comprehensive algorithm to ensure that once you have selected someone else’s book, they are never offered one of yours in return. That way we steer well clear of the \'review swap\' problem and your reviews will be secure.'
            },
            {
                'question': 'What Genres do you accept?',
                'answer': 'We accept Low content books (such as children\'s books, trivia books, workbooks and etc), No Content Books and Non-fiction books'
            },
            {
                'question': 'Why do I need to purchase the book from Amazon?',
                'answer': 'We ask our users to purchase books from Amazon for three reasons. Firstly, it helps the author by boosting their book in Amazon’s rankings system. Secondly, it ensures that the review left is a \'Verified Review\' (meaning that the book is more likely to come back in Amazon’s search engine). And finally, it prevents your books from being pirated and shared illegally. We have members selling their books from as little as 0.99¢, so you don’t have to spend a lot to use BOOKSTARS. Plus, you will always make some of what you spend back in royalties whenever someone buys your book. (Note: we do allow our users to use Kindle Unlimited if they have subscribed to it. That way the author still gets paid, however, they will not get a Verified Review).'
            },
            {
                'question': 'I\'m not an author. Can I use BOOKSTARS?',
                'answer': 'Yes! We welcome all kinds of readers who are just looking for a good book. An author can also use a \'proxy reader\' to read books on their behalf. (Please note that if you do use a proxy reader then both the author and the reader will need to share the same BOOKSTARS account).'
            },
            {
                'question': 'Do I need a Kindle to use BOOKSTARS?',
                'answer': 'Ideally, yes. If you don’t have one then you can download the Kindle App for free on your smartphone or tablet. Head to the App Store or Google Play to see if it is compatible on your device.'
            },
            {
                'question': 'How many Amazon reviews do I need to start generating sales?',
                'answer': 'Amazon are very secretive about their algorithms - no one can give you an exact number. Some say that you need a minimum of fifty reviews, whereas others say you need a hundred. All we know is that the more you have, the better your book will sell.'
            },
            {
                'question': 'Is there a limit to how many reviews I can acquire?',
                'answer': 'Nope. You can use BOOKSTARS as often as you like. Just set yourself a goal and don’t stop until you reach it!'
            },
            {
                'question': 'I have more than one pen name. Do I need a separate account?',
                'answer': 'BOOKSTARS encourages you to use only one account for all of your books, regardless of the name it is published under. That way we can prevent accidental review swapping and you can see all of your books in one place. You can change the name of your book’s author at any time in Your Profile.'
            },
            {
                'question': 'My book is written in another language. Will it be accepted?',
                'answer': 'Yes, a Non-English books are welcome on BOOKSTARS as long as they are for sale on Amazon.'
            }
        ]
        
        context.update({
            'plans': plans,
            'faqs': faqs
        })
        
        return context