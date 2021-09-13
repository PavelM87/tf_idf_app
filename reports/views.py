import string
import math

from django.shortcuts import redirect, render
from django.core.paginator import Paginator

from .forms import FileForm
from .models import File



def get_data(filename):
    """ Cчитывание данных из файла"""
    corpus = {}
    cnt = 0
    prev = '' # Переменная для хранения значение предыдущей строки файла
    with open('media/' + filename, 'r') as f:
        for line in f:
            if line.strip(): # Если строка не пустая
                line = line.lower().translate(str.maketrans('', '', string.punctuation)) # Убираю знаки препинания и делаю слова строчными
                corpus.setdefault(cnt, []).extend(line.split())
                prev = line
            elif line.strip() == '' and prev == '': # На случай если будет больше одной пустой строки между текстами в файле
                pass
            else:
                cnt += 1
                prev = ''
    return corpus


def tf_idf(corpus):
    """Обработка данных"""
    # Создаю множество из всех слов в документе
    word_set = set()
    for _, lst in corpus.items():
        word_set = word_set.union(set(lst))
    # Создаю словарь где ключ - номер текста, значение - слова и их количество в тексте
    word_count = {i: dict.fromkeys(word_set, 0) for i in range(len(corpus))}
    for c_key, c_list in corpus.items():
        for term in c_list:
            word_count[c_key][term] += 1
    # idf - результирующий словарь важности слова в тексте
    idf = dict.fromkeys(word_count[0].keys(), 0)
    for key, dct in word_count.items():
        for word, count in dct.items():
            if count > 0:
                idf[word] += 1     
    size = len(corpus)   
    for word, cnt in idf.items():
        idf[word] = round(math.log(size / cnt), 5)
    # Подсчет частоты слов и добавление в результирующей список tf_list idf и tf каждого слова
    tf_list = []
    for key, term_list in corpus.items():
        tf_list.append(('TEXT', '№', key + 1))  # добавляю разделитель текстов в документе
        for term in set(term_list):
            tf_list.append(
                (term, round(term_list.count(term) / len(term_list), 5), idf[term])
                )
    print(tf_list)
    return tf_list 
    

def upload_file(request):
    """Представление страницы для загрузки файла"""
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('term_table')
    else:
        form = FileForm()

    return render(request, 'upload.html', {'form': form})

def term_table(request):
    """Представление страницы для отображения обработанных данных"""
    document = File.objects.last()
    data = get_data(document.file.name)
    tfidf = tf_idf(data)
    # Сортировка по убыванию tdf каждого текста
    ind = 1
    for n, tup in enumerate(tfidf[1:],start=1):
        if tup[0] == 'TEXT':
            tfidf = tfidf[:ind] + sorted(tfidf[ind:n], key=lambda x: x[2], reverse=True) + tfidf[n:]
            ind = n + 1
    tfidf = tfidf[:ind] + sorted(tfidf[ind:], key=lambda x: x[2], reverse=True)
    # Пагинация
    paginator = Paginator(tfidf, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    filename = document.file.name
    return render(request, 'term_table.html', {'page_obj': page_obj, 'filename': filename})