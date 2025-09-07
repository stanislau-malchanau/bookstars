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