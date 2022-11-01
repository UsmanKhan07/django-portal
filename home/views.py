import json
import subprocess
import pandas as pd
from time import sleep
from datetime import datetime
from home.models import Contact
from django.contrib import messages
from django.shortcuts import render, HttpResponse
from IPython.display import HTML
from IPython.display import display


def validate(text):
    results = subprocess.Popen(
        [
            "python",
            "home/validate_solution.py",
            "--solution",
            text,
            "--score",
            str(score),
            "--groundtruths",
            json.dumps(test)
        ],
        stdout= subprocess.PIPE
    )
    return results.communicate()[0].strip().decode()

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
        answer = request.POST.get('answer')
        blow = validate(answer)
        contact = Contact( answer=answer)
        contact.save()
        messages.success(request, 'Your solution has been sent!')
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
    return HttpResponse("this is homepage")
 

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
 