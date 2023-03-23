import json
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from django.db.models import Sum, Count
from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt

from .models import SSLHour


# Mttb1tm!


@csrf_exempt
def login(request):
    if request.POST:
        studentvue_username = request.POST["studentvue_username"]
        password = request.POST["password"]
        sslhours_username = request.POST["sslhours_username"]
        club = request.POST["club"]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=200)
            page = browser.new_page()

            # LOGIN
            page.goto("https://md-mcps-psv.edupoint.com/PXP2_Login_Student.aspx")

            page.fill("#ctl00_MainContent_username", studentvue_username)
            page.fill("#ctl00_MainContent_password", password)

            # DISCARD USERNAME AND PASSWORD -- WE ONLY NEEDED IT TO LOG IN
            parentvue_username = None
            password = None

            page.click("#ctl00_MainContent_Submit1")

            # GO TO THE COURSE AND SSL HOURS HISTORY PAGE
            page.goto("https://md-mcps-psv.edupoint.com/PXP2_CourseHistory.aspx?AGU=0")

            # WARM UP THE SOUP
            soup = BeautifulSoup(page.content(), "html.parser")

            # GET THE STUDENT ID
            student_id = soup.select(
                "#ctl00_ctl00_MainContent_StudentSelector > div > div > div.student-photo > span"
            )[0].text[4:]
            print(f"Your student ID is: {student_id}")

            # GET THE SCHOOL NAME
            school_name = soup.select(
                "#ctl00_ctl00_MainContent_StudentSelector > div > div > div.student-details > div.school"
            )[0].text
            print(f"Your school is: {school_name}")

            # MAKE SURE THE SSL DATA IS LOADED
            page.wait_for_selector(
                "#ctl00_ctl00_MainContent_PXPMainContent_ServiceLearningGridDetails"
            )

            # MAKE SURE THE dxDataGrid LIBRARIES ARE LOADED, SO THAT I CAN GET THE DATA
            page.wait_for_selector(".dx-datagrid")

            # OK NOW GET THE DATA
            data = page.evaluate(
                """() => {
                    const dataGrid = $('#ctl00_ctl00_MainContent_PXPMainContent_ServiceLearningGridDetails').dxDataGrid('instance');
                    return dataGrid.option('dataSource');
                }"""
            )

            # CONVERT IT TO PYTHON
            ssl_hours = [json.loads(json.dumps(row)) for row in data]

            # Close the browser
            browser.close()

        # DELETE ANY EXISTING HOURS FOR THIS STUDENT BC WE ARE GOING TO RECREATE THEM
        SSLHour.objects.filter(student_id=student_id).delete()

        for row in ssl_hours:
            SSLHour.objects.create(
                SSL_ID=row["ID"],
                date_earned=datetime.strptime(row["DateEarned"], "%m/%d/%Y").date(),
                project_name=row["ProjectName"],
                hours=row["Hours"],
                username=sslhours_username,
                student_id=student_id,
                school_name=school_name,
                club=club,
            )

        return redirect("cv", username=sslhours_username)

    return render(request, "login.html")


def cv(request, username):
    ssl_hours = SSLHour.objects.filter(username=username)
    total_hours = ssl_hours.aggregate(Sum("hours"))["hours__sum"]
    return render(
        request,
        "cv.html",
        {"username": username, "total_hours": total_hours, "ssl_hours": ssl_hours},
    )


def school(request, school_name):
    ssl_hours = (
        SSLHour.objects.filter(school_name=school_name)
        .values("username")
        .annotate(total_hours=Sum("hours"))
    )
    total_hours = SSLHour.objects.filter(school_name=school_name).aggregate(
        Sum("hours")
    )["hours__sum"]
    return render(
        request,
        "school.html",
        {
            "school_name": school_name,
            "total_hours": total_hours,
            "ssl_hours": ssl_hours,
        },
    )


def club(request, club):
    ssl_hours = (
        SSLHour.objects.filter(club=club)
        .values("username")
        .annotate(total_hours=Sum("hours"))
        .order_by("total_hours")
    )
    total_hours = SSLHour.objects.filter(club=club).aggregate(Sum("hours"))[
        "hours__sum"
    ]
    return render(
        request,
        "club.html",
        {
            "total_hours": total_hours,
            "club": club,
            "ssl_hours": ssl_hours,
        },
    )


def home(request):
    ssl_hours = SSLHour.objects.all()
    total_hours = SSLHour.objects.aggregate(Sum("hours"))["hours__sum"]

    return render(
        request,
        "home.html",
        {
            "total_hours": total_hours,
            "ssl_hours": ssl_hours,
        },
    )
