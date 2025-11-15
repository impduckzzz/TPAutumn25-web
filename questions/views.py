from django.shortcuts import render
from .models import Question
from django.core.paginator import Paginator

from django.shortcuts import render
from .models import Question
from django.core.paginator import Paginator

def question_list(request):
    questions = Question.objects.all().order_by('-created_at')  
    paginator = Paginator(questions, 10) 
    page = request.GET.get('page')  
    paginated_questions = paginator.get_page(page) 
    return render(request, 'index.html', {'questions': paginated_questions})

def question_detail(request, id):
    question = Question.objects.get(id=id)
    return render(request, 'question.html', {'question': question})

def ask_question(request):
    if request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']
        tags = request.POST['tags']
        

        question = Question(title=title, body=body)
        question.save()
        

        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                tag = tag.strip()

                tag_instance, created = Tag.objects.get_or_create(name=tag)
                question.tags.add(tag_instance)
        
        return redirect('home')
    return render(request, 'ask.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Неверный логин или пароль") 
    return render(request, 'login.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request, 'Ваш аккаунт был успешно создан!')
            return redirect('login') 
            messages.error(request, 'Ошибка при регистрации')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})