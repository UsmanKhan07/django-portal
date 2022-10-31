from django.shortcuts import render, HttpResponse
from datetime import datetime
from home.models import Contact
from django.contrib import messages
from time import sleep
import pandas as pd
from IPython.display import HTML
from IPython.display import display
# Create your views here.
def index(request):
    # context = {
    #     "variable":"Write a code for even number",
    #     #"variable1":"Rohan is great",
    #     #"myFunction()":"hello"
    #     "blow":
    # } 
    kow=323

    def evaluate_solution(func, groundtruths_dict, score):
        score_per_unit = score/sum([v.get("score_points",1) for k,v in groundtruths_dict.items()])
        results = {}
        results["obtained_score"] = 0
        for k,v in groundtruths_dict.items():
            results[k] = {}
            s = score_per_unit*v.get("score_points",1)
            out=""
            try:
                out = func(v["input"])
                if out==v["output"]:
                    results[k]["status"] = "Passed"
                    results[k]["score"] = str(round(s,2))+"/"+str(round(s,2))
                    results["obtained_score"] += s
                else:
                    results[k]["status"] = "Failed"
                    results[k]["score"] = "0/"+str(round(s,2))
            except:
                results[k]["status"] = "Error"
                results[k]["score"] = "0/"+str(round(s,2))
            if v["hidden"]:
                results[k]["input"] = "Hidden"
                results[k]["output"] = "Hidden"
                results[k]["expected_output"] = "Hidden"
            else:
                results[k]["input"] = v["input"]
                results[k]["output"] = out
                results[k]["expected_output"] = v["output"]
            
        return results


    

    def disp(r):
        r_dict = {
            "Test Case": [],
            "Input": [],
            "Expected Output": [],
            "Output": [],
            "Status": [],
            "Score": [],
        }
        for k,v in r.items():
            if k!="obtained_score":
                r_dict["Test Case"] += [k]
                r_dict["Input"] += [v.get("input","N/A")]
                r_dict["Expected Output"] += [v.get("output","N/A")]
                r_dict["Output"] += [v.get("output","N/A")]
                r_dict["Status"] += [v.get("status","N/A")]
                r_dict["Score"] += [v.get("score","N/A")]
        df = pd.DataFrame.from_dict(r_dict)
        
        return HTML(df.to_html(classes='table table-stripped'))

















    def validate(fun,test):
#     def correct_solution(s):
#         return s == s[::-1]
        lis=[]
        for i in test.keys():
            a=test[i]["input"]
            
            b=fun(a)
            if test[i]["output"]==b:
                lis.append("True")
            else:
                lis.append("False")
        return lis
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

    def ab():
        return "redivider"
    # b=eval("ab" + "()")
    # ans1 = "def ishfaq(a,b):\n   return a+b"
    # ans1 = "lambda x,y:x+y"
    # func = eval(ans1)
    # print(func(2,6))
    from types import ModuleType
    import sys

    mod = ModuleType('my_module', 'doc string here')
    #exec('def umar(a,b):\n    return a+b', mod.__dict__)
    sys.modules['my_module'] = mod
    #print(mod.umar(1,5))
    blow=[]
    if request.method == "POST":
        #name = request.POST.get('name')
        #email = request.POST.get('email')
        #phone = request.POST.get('phone')
        answer = request.POST.get('answer')
        print(type(answer))
        print(answer)
    
        # exec(answer)
        #lambda
        # func = eval(answer)
        # print(func(1,2))
        # print(dir())
        exec(answer, mod.__dict__)
        sys.modules['my_module'] = mod
        
        score = 100
        #r1 = evaluate_solution(dummy_solution, groundtruths_dict, score)


        #blow=validate(mod.solution,test)
        r1=evaluate_solution(mod.solution, test, score)
        blow=disp(r1)
        #print(mod.solution(1,5))
        
        # testing Umar
        print(dir())
        exec(answer)
        # sleep(5)
        print(dir())
        # global umar
        # print(umar(1,2))
        # b=eval("answer"+ "()")
        contact = Contact( answer=answer)
        contact.save()
        messages.success(request, 'Your solution has been sent!')
    #return render(request, 'index.html')

    context = {
        "variable":"Write a code for even number",
        #"variable1":"Rohan is great",
        #"myFunction()":"hello"
        "blow":blow
    }
    return render(request, 'index.html', context)
    #return HttpResponse("this is homepage")

def about(request):
    return render(request, 'about.html') 

def services(request):
    return HttpResponse("this is homepage")
#    return render(request, 'services.html')
 

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
 