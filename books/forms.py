from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'asin', 'language', 'genre']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'asin': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BookCoverForm(forms.Form):
    cover_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'  # Только изображения
        })
    )

class BookFileForm(forms.Form):
    BOOK_FILE_TYPES = ['pdf', 'epub', 'doc', 'docx']
    
    book_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.epub,.doc,.docx'
        })
    )
    
    def clean_book_file(self):
        file = self.cleaned_data.get('book_file')
        if file:
            # Проверка размера файла (максимум 50MB)
            if file.size > 50 * 1024 * 1024:  # 50MB в байтах
                raise forms.ValidationError('Файл слишком большой. Максимальный размер 50MB.')
            
            # Проверка типа файла
            ext = file.name.split('.')[-1].lower()
            if ext not in self.BOOK_FILE_TYPES:
                raise forms.ValidationError(f'Недопустимый тип файла. Разрешены: {", ".join(self.BOOK_FILE_TYPES)}')
        
        return file
    
class GetReviewedForm(forms.Form):
    reading_type = forms.ChoiceField(
        choices=Book.READING_TYPES,
        widget=forms.RadioSelect,
        label="Выберите тип обзора"
    )
    
    # Для Verified eBook
    book_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    # Для Verified Print
    print_book_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    print_book_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    # Goodreads
    add_goodreads_review = forms.BooleanField(required=False)
    goodreads_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    
    # Фото/видео (для Verified Print)
    add_photo_review = forms.BooleanField(required=False)
    add_video_review = forms.BooleanField(required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        reading_type = cleaned_data.get('reading_type')
        
        # Валидация для Verified eBook
        if reading_type == 'verified_ebook':
            book_price = cleaned_data.get('book_price')
            if book_price is None:
                raise forms.ValidationError("Укажите цену книги для Verified Purchase (eBook)")
        
        # Валидация для Verified Print
        if reading_type == 'verified_print':
            print_book_link = cleaned_data.get('print_book_link')
            print_book_price = cleaned_data.get('print_book_price')
            if not print_book_link:
                raise forms.ValidationError("Укажите ссылку на печатную книгу")
            if print_book_price is None:
                raise forms.ValidationError("Укажите цену печатной книги")
        
        # Валидация Goodreads
        add_goodreads = cleaned_data.get('add_goodreads_review')
        goodreads_link = cleaned_data.get('goodreads_link')
        if add_goodreads and not goodreads_link:
            raise forms.ValidationError("Укажите ссылку на Goodreads")
            
        return cleaned_data