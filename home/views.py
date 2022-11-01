import json
import subprocess
import pandas as pd
from time import sleep
from datetime import datetime
from home.models import Contact
from home.models import Questions
from home.models import Test
from django.contrib import messages
from django.shortcuts import render, HttpResponse
from IPython.display import HTML
from IPython.display import display


def validate(text):
    results = subprocess.Popen(
        [
            "python",
            "home/validate_solution.py", # for linux / mac
            # "home/validate_solution_w.py", # for windows (less functionality)
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

t_id = 1
q_id = 1
problem_statement = "Write a code for Usman Khan ;-)"
score = 100
test= {
    1: {
        "input": "redivider",
        "output": "redivider",
        "hidden": True
    },
    2: {
        "input": "civic",
        "output": "civic",
        "hidden": False
    },
    3: {
        "input": "hello",
        "output": "olleh",
        "hidden": False
    }
}


def index(request):
    blow = ""
    if request.method == "POST":
        email = request.POST.get('email')
        answer = request.POST.get('answer')
        if Contact.objects.filter(t_id=t_id, q_id=q_id, email=email):
            messages.error(request, 'Not Submitted!\nSolution is already submitted for this question against this email id!')
        else:
            blow_flag, blow, obt_marks = validate(answer)   
            if blow_flag:
                contact = Contact(email=email,solution=answer, t_id=t_id, q_id=q_id, obtained_marks=obt_marks, total_marks=score)
                contact.save()
                messages.success(request, 'Your solution has been sent!')
            else:
                messages.error(request, 'Not Submitted!\nRemove errors from your code!')
    context = {
        "variable":problem_statement,
        #"variable1":"Rohan is great",
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
        score = request.POST.get('score')
        t_id = request.POST.get('t_ids')
        testcases = request.POST.get('testcases')
        questions = Questions.objects.filter(t_id=t_id)
        q_id = len(questions)+1
        v_flag = True
        if v_flag:
            q = Questions(q_id=q_id,t_id=t_id, groundtruths=testcases, statement=statement, score=score)
            q.save()
            messages.success(request, 'Questiuon is saved against q_id '+str(q_id)+" in test "+t_id)
        else:
            messages.error(request, 'Unable to Save question')
    context = {
        "t_ids": available_t_ids
    }
    return render(request, 'add_question.html', context)



def contact(request):
    if request.method == "POST":
        #name = request.POST.get('name')
        #email = request.POST.get('email')
        #phone = request.POST.get('phone')
        answer = request.POST.get('freeform')
        contact = Contact( answer=answer)
        contact.save()
        messages.success(request, 'Your message has been sent!')
    return render(request, 'index.html')
 