from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from recruiter_app.models import Recruiter, RecruiterDetail, JobDetail, JobApplied


def homepage(request):
    return render(request, "./recruiter_app/home.html")


def recruiter_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        name = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        if Recruiter.objects.filter(username=username).exists():
            return render(request, "./recruiter_app/signup.html", {"error": "Username already taken."})

        Recruiter.objects.create(
            username=username,
            name=name,
            email=email,
            phone=phone,
            password=password
        )
        return redirect("recruiter_login")
    else:
        return render(request, "./recruiter_app/signup.html")


def recruiter_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = Recruiter.objects.filter(username=username, password=password).first()

        if user:
            request.session["recruiter_id"] = user.id
            request.session["recruiter_username"] = user.username
            request.session["recruiter_name"] = user.name
            request.session["recruiter_email"] = user.email
            request.session["recruiter_phone"] = user.phone
            return redirect("recruiter_dashboard")
        else:
            return render(request, "./recruiter_app/login.html", {"error": "Invalid username or password."})
    else:
        return render(request, "./recruiter_app/login.html")


def recruiter_dashboard(request):
    if "recruiter_username" not in request.session:
        return redirect("recruiter_login")

    recruiter_id = request.session.get("recruiter_id")
    username = request.session.get("recruiter_name")

    total_jobs = JobDetail.objects.filter(recruiter_id=recruiter_id).count()
    total_applications = JobApplied.objects.filter(recruiter_id=recruiter_id).count()
    approved_count = JobApplied.objects.filter(recruiter_id=recruiter_id, scheduled=True).count()

    return render(request, "./recruiter_app/dashboard.html", {
        "username": username,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "approved_count": approved_count,
    })


def recruiter_profile(request):
    if "recruiter_username" not in request.session:
        return redirect("recruiter_login")

    userid = request.session.get("recruiter_id")
    name = request.session.get("recruiter_name")
    email = request.session.get("recruiter_email")
    phone = request.session.get("recruiter_phone")

    user = RecruiterDetail.objects.filter(user_id=userid).first()

    if user:
        bio = user.bio
        address = user.address
        city = user.city
        state = user.state
        profile_pic = user.profile_pic
    else:
        bio = address = city = state = None
        profile_pic = None

    context = {
        "name": name,
        "email": email,
        "phone": phone,
        "bio": bio,
        "address": address,
        "city": city,
        "state": state,
        "profile_pic": profile_pic,
    }
    return render(request, "./recruiter_app/profile.html", context)


def recruiter_profile_update(request):
    if "recruiter_username" not in request.session:
        return redirect("recruiter_login")

    id = request.session.get("recruiter_id")
    recruiter = Recruiter.objects.filter(id=id).first()
    existing = RecruiterDetail.objects.filter(user=recruiter).first()

    if request.method == "POST":
        bio = request.POST.get("bio")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        image = request.FILES.get("image")

        defaults = {
            "bio": bio,
            "address": address,
            "city": city,
            "state": state,
        }
        if image:
            defaults["profile_pic"] = image

        RecruiterDetail.objects.update_or_create(
            user=recruiter,
            defaults=defaults
        )
        return redirect("recruiter_profile")
    else:
        return render(request, "./recruiter_app/profile_update.html", {"existing": existing})


def job_details(request):
    if "recruiter_username" not in request.session:
        return redirect("recruiter_login")

    id = request.session.get("recruiter_id")
    recruiter = Recruiter.objects.filter(id=id).first()

    if request.method == "POST":
        company_name = request.POST.get("company_name")
        company_address = request.POST.get("company_address")
        company_image = request.FILES.get("company_image")
        job_role = request.POST.get("job_role")
        job_description = request.POST.get("job_description")
        skills = request.POST.get("skills")
        salary = request.POST.get("salary")
        experience = request.POST.get("experience")
        qualification = request.POST.get("qualification")
        vacancy = request.POST.get("vacancy")
        employment_type = request.POST.get("employment_type")
        location = request.POST.get("location")
        industry = request.POST.get("industry")
        last_date = request.POST.get("last_date")
        hiring_process = request.POST.get("hiring_process")

        JobDetail.objects.create(
            recruiter=recruiter,
            company_name=company_name,
            company_address=company_address,
            company_image=company_image,
            job_role=job_role,
            skills_required=skills,
            job_decription=job_description,
            salary_range=salary,
            experience_rqeuired=experience,
            qualifications=qualification,
            vacancy=vacancy,
            job_location=location,
            employment_type=employment_type,
            industry_type=industry,
            last_date=last_date,
            hiring_process=hiring_process
        )
        return redirect("recruiter_dashboard")
    else:
        return render(request, "./recruiter_app/job_detail.html")


def my_jobs(request):
    if "recruiter_username" not in request.session:
        return redirect("recruiter_login")

    recruiter_id = request.session.get("recruiter_id")
    jobs = JobDetail.objects.filter(recruiter_id=recruiter_id).order_by("-job_posted_on")
    return render(request, "./recruiter_app/my_jobs.html", {"jobs": jobs})


def delete_job(request, id):
    if "recruiter_username" not in request.session:
        return redirect("recruiter_login")

    job = get_object_or_404(JobDetail, id=id, recruiter_id=request.session.get("recruiter_id"))
    job.delete()
    return redirect("my_jobs")


def applied_job(request):
    if "recruiter_username" not in request.session:
        return redirect("recruiter_login")

    recruiter_id = request.session.get("recruiter_id")
    jobs = JobApplied.objects.filter(recruiter=recruiter_id).select_related(
        "candidate", "job_detail"
    )
    return render(request, "./recruiter_app/applied_job.html", {"a": jobs})


def approve(request, id):
    if "recruiter_username" not in request.session:
        return redirect("recruiter_login")

    job = get_object_or_404(JobApplied, id=id)
    job.scheduled = True
    job.save()
    return redirect("applied_job")


def recruiter_logout(request):
    request.session.flush()
    return redirect("recruiter_login")
