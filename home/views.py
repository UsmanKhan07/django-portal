import json
import subprocess
import pandas as pd
from time import sleep
from datetime import datetime
from home.models import Results
from home.models import Questions
from home.models import Test
from django.contrib import messages
from django.shortcuts import render, HttpResponse
from IPython.display import HTML
from IPython.display import display
from django.core.paginator import Paginator,EmptyPage


def validate(text, test, score):
    results = subprocess.Popen(
        [
            "python",
#             "home/validate_solution.py", # for linux and mac (optimized for speed)
            "home/validate_solution_w.py", # for windows, linux and mac (not optimized in speed)
            "--solution",
            text,
            "--score",
            str(score),
            "--groundtruths",
            json.dumps(test)
        ],
        stdout= subprocess.PIPE
    )
    return json.loads(results.communicate()[0].strip().decode())

count=0

def index(request):
    global count
    t_id = "demo1"
    questions = Questions.objects.all()
    available_questions = [q for q in questions if q.t_id==t_id]



    page_n=request.GET.get('/',count)
    count=count+1
    if count>=len(available_questions):
        count = len(available_questions)-1
    p = Paginator(questions, 1)
    try:
        page = p.page(page_n)
    except EmptyPage:
        page = p.page(1)
    print(page_n)
    q = available_questions[page_n]
    q_id = q.q_id
    problem_statement = q.statement
    test = json.loads(q.groundtruths)
    score = q.score
    solution = q.solution
    blow = ""
    if request.method == "POST":
        email = request.POST.get('email')
        answer = request.POST.get('answer')
        if Results.objects.filter(t_id=t_id, q_id=q_id, email=email):
            messages.error(request, 'Not Submitted!\nSolution is already submitted for this question against this email id!')
        else:
            blow_flag, blow, obt_marks = validate(answer, test, score)  
            if blow_flag:
                r = Results(email=email,solution=answer, t_id=t_id, q_id=q_id, obtained_marks=obt_marks, total_marks=score)
                r.save()
                messages.success(request, 'Your solution has been sent!')
            else:
                messages.error(request, 'Not Submitted!\nRemove errors from your code!')
    context = {
        "variable":problem_statement,
        "no_of_qs": len(available_questions),
        "test_id": t_id,
        "q_id": q_id,
        #"myFunction()":"hello"
        "blow":blow
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html') 

def services(request):
    tests = Test.objects.all()
    available_t_ids = [t.t_id for t in tests if t.is_open]
    if request.method == "POST":
        statement = request.POST.get('statement')
        answer = request.POST.get('solution')
        score = request.POST.get('score')
        t_id = request.POST.get('t_ids')
        testcases = request.POST.get('testcases')
        questions = Questions.objects.filter(t_id=t_id)
        q_id = len(questions)+1
        try:
            ground_truths = json.loads(testcases)
            try:
                exec(answer)
                blow_flag, blow, obt_marks = validate(answer, ground_truths, float(score))
                if round(float(score),2)==round(float(obt_marks),2):
                    q = Questions(q_id=q_id,t_id=t_id, groundtruths=testcases, statement=statement, score=score, solution=answer)
                    q.save()
                    messages.success(request, 'Questiuon is saved against q_id '+str(q_id)+" in test "+t_id)
                else:
                    messages.error(request, 'Your code is unable to pass test cases. There may be issue in code or there may be issue in testcases. Please check again.')
            except Exception as c_e:
                print(c_e)
                messages.error(request, 'There is issue in solution. Please check your code for errors.',str(c_e))
        except Exception as j_e:
            messages.error(request, 'There is issue in testcases. These should be after json.dumps() and this text should be valid for json.loads()',str(j_e))
    return render(request, 'add_question.html', {"t_ids": available_t_ids})



def contact(request):
    if request.method == "POST":
        #name = request.POST.get('name')
        #email = request.POST.get('email')
        #phone = request.POST.get('phone')
        answer = request.POST.get('freeform')
        contact = Results( answer=answer)
        contact.save()
        messages.success(request, 'Your message has been sent!')
    return render(request, 'index.html')
 