import json
import subprocess
import pandas as pd
from time import sleep
from datetime import datetime
from home.models import Results
from home.models import Questions
from home.models import Test
from django.contrib import messages
from django.shortcuts import render, HttpResponse,redirect
from IPython.display import HTML
from IPython.display import display
from django.core.paginator import Paginator,EmptyPage
from django.http import Http404,HttpResponseRedirect
from django.urls import reverse



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


def index(request, defualt_email="test@ml1.ai", t_id="demo1"):
    if not request.META.get('HTTP_REFERER'):
        raise Http404
    default_text = "def solution(input_value):\n    # your code here"
    questions = Questions.objects.all()
    available_questions = [q for q in questions if q.t_id==t_id]
    blow = ""
    pg_no = 0
    q = available_questions[pg_no]
    q_id = q.q_id
    problem_statement = q.statement
    test = json.loads(q.groundtruths)
    score = q.score
    # solution = q.solution
    if request.method == "POST":
        if "Submit" in request.POST or "Verify" in request.POST:
            email = request.POST.get('email')
            answer = request.POST.get('answer')
            if Results.objects.filter(t_id=t_id, q_id=q_id, email=email):
                messages.error(request, 'unsuccessful!\nSolution is already submitted for this question against this email id!')
            else:
                blow_flag, blow, obt_marks = validate(answer, test, score)  
                if blow_flag:
                    if "Submit" in request.POST:
                        r = Results(email=email,solution=answer, t_id=t_id, q_id=q_id, obtained_marks=obt_marks, total_marks=score)
                        r.save()
                        messages.success(request, 'Your solution has been sent!')
                    else:
                        messages.success(request, 'Your solution has been Verified!')
                else:
                    messages.error(request, 'Unsuccessful!\nRemove errors from your code!')
            default_text = answer
        if "Next" in request.POST:
            current_page = request.POST.get('Next')
            pg_no=int(current_page)+1
            if pg_no>=len(available_questions):
                pg_no = len(available_questions)-1
        if "Previous" in request.POST:
            current_page = request.POST.get('Previous')
            pg_no=int(current_page)-1
            if pg_no<=0:
                pg_no = 0

    q = available_questions[pg_no]
    q_id = q.q_id
    problem_statement = q.statement
    test = json.loads(q.groundtruths)
    score = q.score
    # solution = q.solution
    context = {
        "variable":problem_statement,
        "no_of_qs": len(available_questions),
        "test_id": t_id,
        "q_id": q_id,
        "pg_no": pg_no,
        #"myFunction()":"hello"
        "blow":blow,
        "defualt_email":defualt_email,
        "defualt_text":default_text
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html') 

def services(request):
    if not request.user.is_authenticated:
        raise Http404
        return HttpResponseRedirect(reverse("admin"))
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
 

def main(request):
    tests = Test.objects.all()
    available_t_ids = [t.t_id for t in tests if t.is_open]
    if request.method == "POST":
        t_id = request.GET.get('t_ids')
        email = request.GET.get('email')
        # return redirect(index)
        return redirect(index,defualt_email=email,t_id=t_id)
    return render(request, 'main.html', {"t_ids": available_t_ids})



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
 