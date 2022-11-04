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


def download_df_as_csv(df,filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename='+filename
    df.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
    return response



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
    
    default_text = "def solution(x):\n    # your code here"
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
        defualt_email = request.POST.get('email')
        if "Submit" in request.POST or "Verify" in request.POST:
            pg_no = int(request.POST.get('Submit') if "Submit" in request.POST else request.POST.get('Verify'))
            q = available_questions[pg_no]

            q_id = q.q_id
            problem_statement = q.statement
            test = json.loads(q.groundtruths)
            score = q.score
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
        t_id = request.POST.get('t_ids')
        email = request.POST.get('email')
        # return redirect(index)
        return redirect(index,defualt_email=email,t_id=t_id)
    return render(request, 'main.html', {"t_ids": available_t_ids})


def reports(request):
    if not request.user.is_authenticated:
        raise Http404
    tests = Test.objects.all()
    questions = Questions.objects.all()
    test_wise_questions = {t.t_id:[q for q in questions if q.t_id==t.t_id] for t in tests}
    if request.method == "POST":
        if "download_by_email" in request.POST or "view_by_email" in request.POST:
            email = request.POST.get('email')
            r_dict = {"test":[]}
            max_qs = max([len(x) for x in test_wise_questions.values()])
            r_dict.update({"q"+str(i+1):[] for i in range(max_qs)})
            r_dict.update({"total":[]})
            for t,qs in test_wise_questions.items():
                r_dict["test"] += [t]
                rs = [(Results.objects.filter(t_id=t, q_id=q_id+1, email=email).values(),qs[q_id].score if q_id<len(qs) else 0) for q_id in range(max_qs)]
                rs = [(r[0]["obtained_marks"], s) if r else (0,s) for r,s in rs]
                for i in range(max_qs):
                    r_dict["q"+str(i+1)] += ["" if rs[i][1]==0 else str(rs[i][0])+"/"+str(rs[i][1])]
                r_dict["total"] += [str(sum([x[0] for x in rs]))+"/"+str(sum([x[1] for x in rs]))]
            df = pd.DataFrame.from_dict(r_dict)
            if "download_by_email" in request.POST:
                print(email)
                return download_df_as_csv(df, email+".csv")
            else:
                return render(
                    request,
                    'reports.html',
                    {
                        "t_ids":list(test_wise_questions),
                        "df_table_e": df.to_html(classes='table table-stripped'),
                        "df_table_t": ""
                    }
                )
        if "download_by_testid" in request.POST or "view_by_testid" in request.POST:
            t_id = request.POST.get('t_id')
            qs = test_wise_questions[t_id]
            results = Results.objects.filter(t_id=t_id).values()
            email_wise_results = {}
            for r in results:
                email = r["email"]
                if email not in email_wise_results:
                    email_wise_results[email] = {"q"+str(i+1):[0,qs[i].score] for i in range(len(qs))}
                    email_wise_results[email].update({"total":[0, sum([s[1] for s in email_wise_results[email].values()])]})
                email_wise_results[email]["q"+str(r["q_id"])][0] = r["obtained_marks"]
                email_wise_results[email]["total"][0] += r["obtained_marks"]
            r_dict = {"email":[]}
            r_dict.update({"q"+str(i+1):[] for i in range(len(qs))})
            r_dict["total"] = []
            for email,scores in email_wise_results.items():
                r_dict["email"] += [email]
                for s_k,s_v in scores.items():
                    r_dict[s_k] += [str(s_v[0])+"/"+str(s_v[1])]
            df = pd.DataFrame.from_dict(r_dict)
            if "download_by_testid" in request.POST:
                r = download_df_as_csv(df, t_id+".csv")
                return r
            else:
                return render(
                    request,
                    'reports.html',
                    {
                        "t_ids":list(test_wise_questions),
                        "df_table_e": "",
                        "df_table_t": df.to_html(classes='table table-stripped')
                    }
                )
    return render(
        request,
        'reports.html',
        {"t_ids":list(test_wise_questions),
         "df_table_t":"",
         "df_table_e":""
        }
    )



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
 